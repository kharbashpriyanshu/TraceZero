"""
scanner/file_scanner.py

Multithreaded filesystem scanner.

Scans configured paths for orphaned files, leftover app data,
cache, logs, crash dumps, and temp files.

Features:
- Concurrent scanning with ThreadPoolExecutor
- Pause/resume support
- Progress callbacks
- Permission error handling
- Path safety validation on every item
"""

import os
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Callable, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed

from tracezero.utils.constants import (
    SCAN_PATHS,
    CACHE_EXTENSIONS,
    LOG_EXTENSIONS,
    CRASH_DUMP_EXTENSIONS,
    MAX_SCAN_THREADS,
    MAX_SCAN_DEPTH,
    OLD_FILE_DAYS,
)
from tracezero.utils.helpers import (
    is_path_safe,
    is_protected_package,
    get_dir_size,
    get_file_age_days,
    format_date,
)
from tracezero.utils.logger import app_logger


class FileScanner:
    """
    Multithreaded file system scanner.

    Usage:
        scanner = FileScanner(installed_locations, installed_names)
        scanner.on_item_found = callback_fn
        scanner.on_progress = progress_fn
        results = scanner.scan()
    """

    def __init__(
        self,
        installed_locations: Set[str] = None,
        installed_app_names: Set[str] = None,
    ):
        """
        Args:
            installed_locations: Set of known install paths (lowercase).
            installed_app_names: Set of installed app name fragments (lowercase).
        """
        self.installed_locations = installed_locations or set()
        self.installed_app_names = installed_app_names or set()

        # State management
        self._pause_event = threading.Event()
        self._pause_event.set()  # Not paused by default
        self._stop_event = threading.Event()

        # Callbacks (set by the UI)
        self.on_item_found: Optional[Callable[[Dict], None]] = None
        self.on_progress: Optional[Callable[[str, int], None]] = None
        self.on_status: Optional[Callable[[str], None]] = None

        # Results accumulator
        self.found_items: List[Dict] = []
        self._lock = threading.Lock()

    # ─────────────────────────────────────────────
    #  CONTROL METHODS
    # ─────────────────────────────────────────────

    def pause(self):
        """Pause the scan at the next checkpoint."""
        self._pause_event.clear()
        app_logger.info("Scan paused.")

    def resume(self):
        """Resume a paused scan."""
        self._pause_event.set()
        app_logger.info("Scan resumed.")

    def stop(self):
        """Signal the scan to stop."""
        self._stop_event.set()
        self._pause_event.set()  # Unblock if paused
        app_logger.info("Scan stop requested.")

    def reset(self):
        """Reset scanner state for a new scan."""
        self._pause_event.set()
        self._stop_event.clear()
        self.found_items.clear()

    def _check_pause_stop(self) -> bool:
        """Wait if paused; return True if stop was requested."""
        self._pause_event.wait()
        return self._stop_event.is_set()

    # ─────────────────────────────────────────────
    #  MAIN SCAN ENTRY POINT
    # ─────────────────────────────────────────────

    def scan(self, custom_paths: List[Path] = None) -> List[Dict]:
        """
        Run the full scan across all configured paths.

        Args:
            custom_paths: Additional paths to scan beyond defaults.

        Returns:
            List of detected leftover item dicts.
        """
        self.reset()
        self._seen_paths: set = set()  # dedup guard

        # Build list of all paths to scan — skip temp (handled by _scan_temp_files)
        paths_to_scan = []
        for category, paths in SCAN_PATHS.items():
            if category == "temp":
                continue  # Handled separately by _scan_temp_files()
            for p in paths:
                if p.exists() and is_path_safe(p):
                    paths_to_scan.append((category, p))

        if custom_paths:
            for p in custom_paths:
                p = Path(p)
                if p.exists() and is_path_safe(p):
                    paths_to_scan.append(("custom", p))

        self._emit_status(f"Starting scan of {len(paths_to_scan)} locations...")
        app_logger.info(f"Scanning {len(paths_to_scan)} root paths")

        # Scan temp files first (fastest)
        self._scan_temp_files()

        # Scan each root path
        with ThreadPoolExecutor(max_workers=MAX_SCAN_THREADS) as executor:
            futures = {
                executor.submit(self._scan_root, category, path): (category, path)
                for category, path in paths_to_scan
            }
            for future in as_completed(futures):
                if self._stop_event.is_set():
                    break
                try:
                    future.result()
                except Exception as e:
                    cat, path = futures[future]
                    app_logger.error(f"Error scanning {path}: {e}")

        # Scan shortcuts for dead links
        self._scan_dead_shortcuts()

        app_logger.info(f"Scan complete. Found {len(self.found_items)} items.")
        return self.found_items

    # ─────────────────────────────────────────────
    #  ROOT PATH SCANNER
    # ─────────────────────────────────────────────

    def _scan_root(self, category: str, root_path: Path):
        """Scan a single root directory for leftover items."""
        self._emit_status(f"Scanning: {root_path}")

        try:
            for entry in self._walk_path(root_path, depth=0):
                if self._check_pause_stop():
                    return

                item = self._analyze_entry(entry, category)
                if item:
                    path_key = item["path"].lower()
                    with self._lock:
                        if path_key in self._seen_paths:
                            continue  # skip duplicate
                        self._seen_paths.add(path_key)
                        self.found_items.append(item)
                    if self.on_item_found:
                        self.on_item_found(item)
        except (PermissionError, OSError) as e:
            app_logger.warning(f"Cannot access {root_path}: {e}")

    def _walk_path(self, path: Path, depth: int):
        """
        Generator that yields Path objects recursively.
        Respects MAX_SCAN_DEPTH, safety checks, and stop signals.
        """
        if depth > MAX_SCAN_DEPTH:
            return
        if self._stop_event.is_set():
            return

        try:
            for entry in os.scandir(path):
                if self._check_pause_stop():
                    return

                entry_path = Path(entry.path)

                # Safety check every entry
                if not is_path_safe(entry_path):
                    continue

                if is_protected_package(entry.name):
                    continue

                yield entry_path

                # Recurse into directories
                if entry.is_dir(follow_symlinks=False):
                    yield from self._walk_path(entry_path, depth + 1)

        except (PermissionError, OSError):
            pass  # Skip inaccessible directories silently

    # ─────────────────────────────────────────────
    #  ENTRY ANALYSIS
    # ─────────────────────────────────────────────

    def _analyze_entry(self, path: Path, category: str) -> Optional[Dict]:
        """
        Determine if a path entry is a leftover item.

        Returns:
            Dict representing the leftover, or None if not a leftover.
        """
        try:
            stat = path.stat()
        except (PermissionError, OSError):
            return None

        name_lower = path.name.lower()
        ext = path.suffix.lower()
        is_dir = path.is_dir()

        # ── Check if it's a cache/log/temp file ───────────────────
        item_category = None

        if ext in CACHE_EXTENSIONS or "cache" in name_lower:
            item_category = "cache"
        elif ext in LOG_EXTENSIONS or "logs" == name_lower or name_lower.endswith(".log"):
            item_category = "log"
        elif ext in CRASH_DUMP_EXTENSIONS or "crashdump" in name_lower or "crash dump" in name_lower:
            item_category = "crash_dump"
        elif "temp" in name_lower or "tmp" in name_lower:
            item_category = "temp"
        elif self._is_orphaned_appdata(path, is_dir):
            item_category = "leftover"
        else:
            return None  # Not a leftover

        # Calculate size
        if is_dir:
            size = get_dir_size(path)
        else:
            size = stat.st_size

        # Age
        age_days = get_file_age_days(path)

        # Find associated app name
        app_name = self._guess_app_name(path)

        return {
            "path": str(path),
            "item_type": "directory" if is_dir else "file",
            "category": item_category,
            "size_bytes": size,
            "last_accessed": datetime.fromtimestamp(stat.st_atime) if stat.st_atime else None,
            "age_days": age_days,
            "risk_level": "Review",  # Will be set by RiskAnalyzer
            "reason": "",            # Will be set by RiskAnalyzer
            "app_name": app_name,
        }

    def _is_orphaned_appdata(self, path: Path, is_dir: bool) -> bool:
        """
        Check if a path in AppData is orphaned (no matching installed app).

        Returns True only for top-level folders in AppData locations.
        """
        if not is_dir:
            return False

        # Only flag top-level directories inside AppData locations
        appdata_roots = [
            str(p).lower() for paths in SCAN_PATHS["appdata"] for p in paths
            if isinstance(paths, list)
        ]
        # Flatten
        flat_roots = []
        for paths in SCAN_PATHS["appdata"]:
            flat_roots.append(str(paths).lower())

        path_lower = str(path).lower()
        parent_lower = str(path.parent).lower()

        is_direct_child_of_appdata = any(
            parent_lower == root for root in flat_roots
        )

        if not is_direct_child_of_appdata:
            return False

        # Check if this folder name matches an installed app
        folder_name = path.name.lower()
        return not any(
            folder_name in app_name or app_name in folder_name
            for app_name in self.installed_app_names
        )

    def _guess_app_name(self, path: Path) -> str:
        """Try to guess the application name from the path."""
        # Walk up the path to find a meaningful parent name
        for parent in path.parents:
            parent_lower = str(parent).lower()
            for app_name in self.installed_app_names:
                if app_name in parent_lower:
                    return app_name.title()
        return path.parent.name  # Fallback: immediate parent folder name

    # ─────────────────────────────────────────────
    #  TEMP FILES SCAN
    # ─────────────────────────────────────────────

    def _scan_temp_files(self):
        """Fast scan of %TEMP% folder for temporary files."""
        for temp_path in SCAN_PATHS["temp"]:
            if not temp_path.exists() or not is_path_safe(temp_path):
                continue
            self._emit_status(f"Scanning TEMP: {temp_path}")
            try:
                for entry in os.scandir(temp_path):
                    if self._stop_event.is_set():
                        return
                    try:
                        p = Path(entry.path)
                        if not is_path_safe(p):
                            continue

                        stat = entry.stat(follow_symlinks=False)
                        size = get_dir_size(p) if entry.is_dir() else stat.st_size
                        age = get_file_age_days(p)

                        item = {
                            "path": str(p),
                            "item_type": "directory" if entry.is_dir() else "file",
                            "category": "temp",
                            "size_bytes": size,
                            "last_accessed": datetime.fromtimestamp(stat.st_atime),
                            "age_days": age,
                            "risk_level": "Safe",
                            "reason": "Temporary file in TEMP folder",
                            "app_name": "",
                        }
                        with self._lock:
                            self.found_items.append(item)
                        if self.on_item_found:
                            self.on_item_found(item)
                    except (PermissionError, OSError):
                        continue
            except (PermissionError, OSError):
                pass

    # ─────────────────────────────────────────────
    #  SHORTCUT SCANNER
    # ─────────────────────────────────────────────

    def _scan_dead_shortcuts(self):
        """
        Find .lnk shortcut files pointing to non-existent targets.
        Checks Desktop and Start Menu locations.
        """
        from tracezero.utils.constants import SHORTCUT_LOCATIONS
        import sys

        for shortcut_dir in SHORTCUT_LOCATIONS:
            if not shortcut_dir.exists():
                continue
            try:
                for lnk in shortcut_dir.rglob("*.lnk"):
                    if self._stop_event.is_set():
                        return
                    try:
                        target = self._resolve_shortcut_target(lnk)
                        if target and not Path(target).exists():
                            stat = lnk.stat()
                            item = {
                                "path": str(lnk),
                                "item_type": "shortcut",
                                "category": "dead_shortcut",
                                "size_bytes": stat.st_size,
                                "last_accessed": datetime.fromtimestamp(stat.st_atime),
                                "age_days": get_file_age_days(lnk),
                                "risk_level": "Safe",
                                "reason": f"Dead shortcut → target missing: {target}",
                                "app_name": lnk.stem,
                            }
                            with self._lock:
                                self.found_items.append(item)
                            if self.on_item_found:
                                self.on_item_found(item)
                    except Exception:
                        continue
            except (PermissionError, OSError):
                continue

    def _resolve_shortcut_target(self, lnk_path: Path) -> Optional[str]:
        """
        Resolve .lnk file target using Windows Shell API.

        Returns:
            Target path string, or None if can't resolve.
        """
        if os.name != "nt":
            return None
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(lnk_path))
            return shortcut.Targetpath
        except Exception:
            return None

    # ─────────────────────────────────────────────
    #  HELPERS
    # ─────────────────────────────────────────────

    def _emit_status(self, message: str):
        """Emit status update to UI callback."""
        if self.on_status:
            self.on_status(message)
        if self.on_progress:
            self.on_progress(message, len(self.found_items))
