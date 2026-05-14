"""
utils/recycle_bin.py

Safe deletion utility using send2trash.

NEVER permanently deletes files - always sends to Recycle Bin.
Includes undo/restore tracking via the database.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from app_trace_cleaner.utils.logger import app_logger
from app_trace_cleaner.utils.helpers import is_path_safe, is_protected_package
from app_trace_cleaner.database.db_manager import get_db

try:
    import send2trash
    SEND2TRASH_AVAILABLE = True
except ImportError:
    SEND2TRASH_AVAILABLE = False
    app_logger.error("send2trash library not found! Install it: pip install send2trash")


class RecycleBinManager:
    """
    Handles safe deletion of leftover files/folders via Recycle Bin.

    Safety guarantees:
    1. Every path is validated before deletion
    2. Protected packages are never deleted
    3. System paths are blocked
    4. All deletions are logged to database
    5. Files go to Recycle Bin, not permanent deletion
    """

    def __init__(self, session_id: int = None):
        """
        Args:
            session_id: Current scan session ID for tracking.
        """
        self.session_id = session_id
        self.db = get_db()
        self._deleted_this_session: List[Dict] = []

    def delete_items(self, items: List[Dict]) -> Tuple[List[str], List[str]]:
        """
        Send a list of items to the Recycle Bin.

        Args:
            items: List of item dicts with 'path' key.

        Returns:
            Tuple of (successful_paths, failed_paths)
        """
        if not SEND2TRASH_AVAILABLE:
            raise RuntimeError(
                "send2trash library is required for safe deletion.\n"
                "Install it with: pip install send2trash"
            )

        successful = []
        failed = []

        for item in items:
            path_str = item.get("path", "")
            path = Path(path_str)

            # ── Final safety checks ────────────────────────────────
            if not self._pre_delete_validate(item):
                failed.append(f"{path_str} (blocked by safety check)")
                continue

            # ── Registry key deletion (different handling) ─────────
            if item.get("item_type") == "registry":
                result = self._delete_registry_key(item)
                if result:
                    successful.append(path_str)
                    self._record_deletion(item)
                else:
                    failed.append(f"{path_str} (registry deletion failed)")
                continue

            # ── File/folder deletion ───────────────────────────────
            if not path.exists():
                app_logger.warning(f"Path no longer exists, skipping: {path}")
                failed.append(f"{path_str} (no longer exists)")
                continue

            try:
                app_logger.info(f"Sending to Recycle Bin: {path}")
                send2trash.send2trash(str(path))
                successful.append(path_str)
                self._record_deletion(item)
                self._deleted_this_session.append(item)
                app_logger.info(f"✅ Deleted: {path}")
            except Exception as e:
                app_logger.error(f"❌ Failed to delete {path}: {e}")
                failed.append(f"{path_str} ({e})")

        app_logger.info(
            f"Deletion summary: {len(successful)} succeeded, {len(failed)} failed"
        )
        return successful, failed

    def delete_single(self, item: Dict) -> bool:
        """
        Delete a single item. Returns True on success.
        """
        successful, failed = self.delete_items([item])
        return len(successful) > 0

    def get_undo_history(self) -> List[Dict]:
        """Return list of items deleted in this session (for undo)."""
        return self._deleted_this_session.copy()

    # ─────────────────────────────────────────────
    #  VALIDATION
    # ─────────────────────────────────────────────

    def _pre_delete_validate(self, item: Dict) -> bool:
        """
        Run all safety checks before deleting an item.

        Returns:
            True if safe to delete, False if should be blocked.
        """
        path_str = item.get("path", "")
        app_name = item.get("app_name", "")
        risk_level = item.get("risk_level", "Review")
        item_type = item.get("item_type", "file")

        # Registry items handled separately
        if item_type == "registry":
            return True

        path = Path(path_str)

        # Check path safety
        if not is_path_safe(path):
            app_logger.warning(f"BLOCKED (unsafe path): {path_str}")
            return False

        # Check for protected packages
        if is_protected_package(app_name) or is_protected_package(path_str):
            app_logger.warning(f"BLOCKED (protected package): {path_str}")
            return False

        # Block Risky items (they need explicit override)
        if risk_level == "Risky":
            app_logger.warning(f"BLOCKED (risky item): {path_str}")
            return False

        # Block Windows directory paths as extra safety net
        path_lower = str(path).lower()
        blocked_roots = [
            "c:\\windows", "c:\\system32", "c:\\recovery",
            "c:\\boot", "c:\\program files\\windows",
        ]
        for blocked in blocked_roots:
            if path_lower.startswith(blocked):
                app_logger.warning(f"BLOCKED (system path): {path_str}")
                return False

        return True

    # ─────────────────────────────────────────────
    #  REGISTRY KEY DELETION
    # ─────────────────────────────────────────────

    def _delete_registry_key(self, item: Dict) -> bool:
        """
        Delete a registry key. Uses winreg on Windows.
        Only deletes HKCU\\SOFTWARE keys for safety.

        Returns:
            True if successful.
        """
        if sys.platform != "win32":
            return False

        path_str = item.get("path", "")
        try:
            import winreg

            # Only allow HKCU SOFTWARE deletions
            if not path_str.upper().startswith("HKCU\\SOFTWARE\\"):
                app_logger.warning(f"Registry deletion blocked (not HKCU\\SOFTWARE): {path_str}")
                return False

            # Strip the HKCU\ prefix
            key_path = path_str[len("HKCU\\"):]

            # Try to delete
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
            app_logger.info(f"✅ Registry key deleted: {path_str}")
            return True

        except FileNotFoundError:
            app_logger.info(f"Registry key already gone: {path_str}")
            return True
        except PermissionError as e:
            app_logger.error(f"No permission to delete registry key {path_str}: {e}")
            return False
        except Exception as e:
            app_logger.error(f"Registry deletion error for {path_str}: {e}")
            return False

    # ─────────────────────────────────────────────
    #  RECORD KEEPING
    # ─────────────────────────────────────────────

    def _record_deletion(self, item: Dict):
        """Log the deletion to the database."""
        try:
            self.db.record_deleted_item(item, session_id=self.session_id)
        except Exception as e:
            app_logger.error(f"Failed to record deletion in DB: {e}")
