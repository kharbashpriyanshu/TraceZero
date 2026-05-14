"""
database/db_manager.py

Database connection manager and CRUD operations.
Uses SQLAlchemy with SQLite for simplicity and portability.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session

from tracezero.database.models import Base, ScanSession, DetectedItem, DeletedItem, InstalledApp
from tracezero.utils.constants import DATABASE_PATH
from tracezero.utils.logger import app_logger


class DatabaseManager:
    """
    Central database access object.
    Handles all reads/writes to the SQLite database.
    """

    def __init__(self, db_path: Path = None):
        """
        Initialize the database engine and create tables if needed.

        Args:
            db_path: Path to SQLite database file. Defaults to DATABASE_PATH.
        """
        self.db_path = db_path or DATABASE_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # SQLite connection string
        connection_string = f"sqlite:///{self.db_path}"

        self.engine = create_engine(
            connection_string,
            connect_args={"check_same_thread": False},  # Allow multi-thread access
            echo=False
        )

        # Create all tables
        Base.metadata.create_all(self.engine)

        self.SessionFactory = sessionmaker(bind=self.engine)
        app_logger.info(f"Database initialized at: {self.db_path}")

    def get_session(self) -> Session:
        """Return a new SQLAlchemy session."""
        return self.SessionFactory()

    # ─────────────────────────────────────────────
    #  SCAN SESSION OPERATIONS
    # ─────────────────────────────────────────────

    def create_scan_session(self, scan_paths: List[str] = None) -> ScanSession:
        """Create a new scan session record and return it."""
        session = self.get_session()
        try:
            scan = ScanSession(
                started_at=datetime.utcnow(),
                scan_paths=json.dumps(scan_paths or []),
                status="running"
            )
            session.add(scan)
            session.commit()
            session.refresh(scan)
            app_logger.info(f"Created scan session ID={scan.id}")
            return scan
        except Exception as e:
            session.rollback()
            app_logger.error(f"Error creating scan session: {e}")
            raise
        finally:
            session.close()

    def finish_scan_session(self, session_id: int, total_items: int, total_size: float):
        """Mark a scan session as completed."""
        session = self.get_session()
        try:
            scan = session.query(ScanSession).filter_by(id=session_id).first()
            if scan:
                scan.finished_at = datetime.utcnow()
                scan.total_items_found = total_items
                scan.total_size_bytes = total_size
                scan.status = "completed"
                session.commit()
        except Exception as e:
            session.rollback()
            app_logger.error(f"Error finishing scan session: {e}")
        finally:
            session.close()

    def cancel_scan_session(self, session_id: int):
        """Mark a scan session as cancelled."""
        session = self.get_session()
        try:
            scan = session.query(ScanSession).filter_by(id=session_id).first()
            if scan:
                scan.status = "cancelled"
                scan.finished_at = datetime.utcnow()
                session.commit()
        except Exception as e:
            session.rollback()
        finally:
            session.close()

    def get_scan_history(self, limit: int = 50) -> List[Dict]:
        """Get recent scan session records."""
        session = self.get_session()
        try:
            scans = session.query(ScanSession).order_by(desc(ScanSession.started_at)).limit(limit).all()
            return [
                {
                    "id": s.id,
                    "started_at": s.started_at.strftime("%Y-%m-%d %H:%M") if s.started_at else "N/A",
                    "finished_at": s.finished_at.strftime("%Y-%m-%d %H:%M") if s.finished_at else "In Progress",
                    "total_items": s.total_items_found,
                    "total_size": s.total_size_bytes,
                    "status": s.status,
                }
                for s in scans
            ]
        finally:
            session.close()

    # ─────────────────────────────────────────────
    #  DETECTED ITEM OPERATIONS
    # ─────────────────────────────────────────────

    def save_detected_items(self, session_id: int, items: List[Dict]) -> int:
        """
        Bulk insert detected items for a scan session.

        Args:
            session_id: Scan session ID
            items: List of item dicts matching DetectedItem fields

        Returns:
            Number of items saved.
        """
        session = self.get_session()
        saved = 0
        try:
            for chunk_start in range(0, len(items), 100):
                chunk = items[chunk_start:chunk_start + 100]
                db_items = []
                for item in chunk:
                    db_item = DetectedItem(
                        session_id=session_id,
                        path=item.get("path", ""),
                        item_type=item.get("item_type", "file"),
                        category=item.get("category", "leftover"),
                        size_bytes=item.get("size_bytes", 0),
                        last_accessed=item.get("last_accessed"),
                        age_days=item.get("age_days"),
                        risk_level=item.get("risk_level", "Review"),
                        reason=item.get("reason", ""),
                        app_name=item.get("app_name", ""),
                        is_selected=True,
                        is_deleted=False,
                    )
                    db_items.append(db_item)
                session.add_all(db_items)
                session.commit()
                saved += len(db_items)
        except Exception as e:
            session.rollback()
            app_logger.error(f"Error saving detected items: {e}")
        finally:
            session.close()
        return saved

    # ─────────────────────────────────────────────
    #  DELETED ITEM OPERATIONS
    # ─────────────────────────────────────────────

    def record_deleted_item(self, item: Dict, session_id: int = None):
        """Record an item that was sent to the Recycle Bin."""
        session = self.get_session()
        try:
            deleted = DeletedItem(
                original_path=item.get("path", ""),
                item_type=item.get("item_type", "file"),
                size_bytes=item.get("size_bytes", 0),
                deleted_at=datetime.utcnow(),
                category=item.get("category", ""),
                risk_level=item.get("risk_level", ""),
                app_name=item.get("app_name", ""),
                session_id=session_id,
                restore_possible=True,
            )
            session.add(deleted)
            session.commit()
        except Exception as e:
            session.rollback()
            app_logger.error(f"Error recording deleted item: {e}")
        finally:
            session.close()

    def get_deletion_history(self, limit: int = 200) -> List[Dict]:
        """Return list of recently deleted items."""
        session = self.get_session()
        try:
            items = session.query(DeletedItem).order_by(desc(DeletedItem.deleted_at)).limit(limit).all()
            return [
                {
                    "id": i.id,
                    "path": i.original_path,
                    "item_type": i.item_type,
                    "size_bytes": i.size_bytes,
                    "deleted_at": i.deleted_at.strftime("%Y-%m-%d %H:%M") if i.deleted_at else "N/A",
                    "category": i.category,
                    "risk_level": i.risk_level,
                    "app_name": i.app_name,
                }
                for i in items
            ]
        finally:
            session.close()

    # ─────────────────────────────────────────────
    #  INSTALLED APP CACHE
    # ─────────────────────────────────────────────

    def cache_installed_apps(self, apps: List[Dict]):
        """Clear old cache and insert fresh installed apps list."""
        session = self.get_session()
        try:
            session.query(InstalledApp).delete()
            for app in apps:
                db_app = InstalledApp(
                    name=app.get("name", "Unknown"),
                    publisher=app.get("publisher"),
                    install_location=app.get("install_location"),
                    install_date=app.get("install_date"),
                    version=app.get("version"),
                    source=app.get("source", "registry"),
                    uninstall_string=app.get("uninstall_string"),
                    detected_at=datetime.utcnow(),
                )
                session.add(db_app)
            session.commit()
            app_logger.info(f"Cached {len(apps)} installed apps in database")
        except Exception as e:
            session.rollback()
            app_logger.error(f"Error caching installed apps: {e}")
        finally:
            session.close()

    def get_cached_apps(self) -> List[Dict]:
        """Return the cached list of installed apps."""
        session = self.get_session()
        try:
            apps = session.query(InstalledApp).all()
            return [
                {
                    "name": a.name,
                    "publisher": a.publisher,
                    "install_location": a.install_location,
                    "version": a.version,
                    "source": a.source,
                }
                for a in apps
            ]
        finally:
            session.close()

    def get_stats(self) -> Dict:
        """Return overall database statistics."""
        session = self.get_session()
        try:
            total_scans = session.query(ScanSession).count()
            total_deleted = session.query(DeletedItem).count()
            total_space_query = session.query(DeletedItem).all()
            total_space = sum(i.size_bytes for i in total_space_query)
            return {
                "total_scans": total_scans,
                "total_deleted_items": total_deleted,
                "total_space_freed": total_space,
            }
        finally:
            session.close()


# Global database manager singleton
_db_manager: Optional[DatabaseManager] = None


def get_db() -> DatabaseManager:
    """Get or create the global DatabaseManager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
