"""
database/models.py

SQLAlchemy ORM models for the TraceZero database.

Tables:
- ScanSession     : Records each scan run with metadata
- DetectedItem    : Each leftover item found during a scan
- DeletedItem     : History of items sent to recycle bin
- InstalledApp    : Cache of detected installed applications
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    DateTime, ForeignKey, Text, create_engine
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class ScanSession(Base):
    """
    Represents a single scan run.
    Stores summary statistics and timing information.
    """
    __tablename__ = "scan_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime, nullable=True)
    total_items_found = Column(Integer, default=0)
    total_size_bytes = Column(Float, default=0.0)
    scan_paths = Column(Text, nullable=True)          # JSON list of scanned paths
    status = Column(String(32), default="running")    # running | completed | cancelled

    # Relationship: one session -> many detected items
    items = relationship("DetectedItem", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ScanSession id={self.id} started={self.started_at} status={self.status}>"


class DetectedItem(Base):
    """
    Represents a single leftover item detected during a scan.
    Each item is linked to a ScanSession.
    """
    __tablename__ = "detected_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("scan_sessions.id"), nullable=False)

    # ── Path Information ─────────────────────────────
    path = Column(String(1024), nullable=False)
    item_type = Column(String(32), nullable=False)    # file | directory | registry | shortcut
    category = Column(String(64), nullable=True)      # cache | log | crash_dump | leftover | temp | registry

    # ── Size & Age ───────────────────────────────────
    size_bytes = Column(Float, default=0.0)
    last_accessed = Column(DateTime, nullable=True)
    age_days = Column(Integer, nullable=True)

    # ── Classification ───────────────────────────────
    risk_level = Column(String(16), default="Review") # Safe | Review | Risky
    reason = Column(Text, nullable=True)              # Why this was flagged
    app_name = Column(String(256), nullable=True)     # Associated app name

    # ── State ────────────────────────────────────────
    is_selected = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)

    # Relationship
    session = relationship("ScanSession", back_populates="items")

    def __repr__(self):
        return f"<DetectedItem path={self.path!r} risk={self.risk_level}>"


class DeletedItem(Base):
    """
    Records every item that was sent to the Recycle Bin.
    Allows restore tracking and undo history.
    """
    __tablename__ = "deleted_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_path = Column(String(1024), nullable=False)
    item_type = Column(String(32), nullable=False)
    size_bytes = Column(Float, default=0.0)
    deleted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    category = Column(String(64), nullable=True)
    risk_level = Column(String(16), nullable=True)
    app_name = Column(String(256), nullable=True)
    session_id = Column(Integer, ForeignKey("scan_sessions.id"), nullable=True)
    restore_possible = Column(Boolean, default=True)  # False once permanently deleted from Bin
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<DeletedItem path={self.original_path!r} deleted_at={self.deleted_at}>"


class InstalledApp(Base):
    """
    Cache of installed applications detected from the registry and package managers.
    Refreshed on each scan.
    """
    __tablename__ = "installed_apps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(512), nullable=False)
    publisher = Column(String(256), nullable=True)
    install_location = Column(String(1024), nullable=True)
    install_date = Column(String(32), nullable=True)
    version = Column(String(128), nullable=True)
    source = Column(String(64), nullable=True)        # registry | winget | chocolatey | steam | epic
    uninstall_string = Column(String(1024), nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<InstalledApp name={self.name!r} source={self.source}>"
