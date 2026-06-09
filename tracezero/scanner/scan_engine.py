"""
scanner/scan_engine.py

High-level scan orchestrator.

Coordinates:
1. Registry reading (installed apps + orphaned keys)
2. Package manager detection
3. File system scanning
4. Risk classification
5. Database persistence

Exposes simple start/pause/resume/stop API for the UI.
"""

import threading
from typing import List, Dict, Callable, Optional

from tracezero.registry.registry_reader import RegistryReader
from tracezero.registry.package_managers import PackageManagerDetector
from tracezero.scanner.file_scanner import FileScanner
from tracezero.scanner.browser_scanner import BrowserScanner
from tracezero.scanner.windows_deep_scanner import WindowsDeepScanner
from tracezero.analyzer.risk_analyzer import RiskAnalyzer
from tracezero.database.db_manager import get_db
from tracezero.utils.logger import app_logger


class ScanEngine:
    """
    Master scan orchestrator.

    Callbacks (set by UI before calling start):
        on_item_found(item_dict)    - Called for each new leftover item
        on_progress(message, count) - Progress updates
        on_status(message)          - Status bar messages
        on_complete(results)        - Called when scan finishes
        on_error(error_message)     - Called on critical error
    """

    def __init__(self):
        # Callbacks
        self.on_item_found: Optional[Callable] = None
        self.on_progress: Optional[Callable] = None
        self.on_status: Optional[Callable] = None
        self.on_complete: Optional[Callable] = None
        self.on_error: Optional[Callable] = None

        # Internal state
        self._scan_thread: Optional[threading.Thread] = None
        self._file_scanner: Optional[FileScanner] = None
        self._session_id: Optional[int] = None
        self._results: List[Dict] = []
        self._is_running = False

        self.db = get_db()
        self.registry = RegistryReader()
        self.pkg_manager = PackageManagerDetector()

    # ─────────────────────────────────────────────
    #  PUBLIC API
    # ─────────────────────────────────────────────

    def start(self):
        """Start scan in a background thread."""
        if self._is_running:
            app_logger.warning("Scan already running.")
            return

        self._scan_thread = threading.Thread(
            target=self._run_scan,
            name="ScanEngineThread",
            daemon=True
        )
        self._is_running = True
        self._scan_thread.start()

    def pause(self):
        """Pause the scan."""
        if self._file_scanner:
            self._file_scanner.pause()

    def resume(self):
        """Resume a paused scan."""
        if self._file_scanner:
            self._file_scanner.resume()

    def stop(self):
        """Stop the scan."""
        if self._file_scanner:
            self._file_scanner.stop()
        self._is_running = False

        if self._session_id:
            self.db.cancel_scan_session(self._session_id)

    def is_running(self) -> bool:
        return self._is_running

    def get_results(self) -> List[Dict]:
        return self._results

    # ─────────────────────────────────────────────
    #  INTERNAL SCAN LOGIC
    # ─────────────────────────────────────────────

    def _run_scan(self):
        """Full scan pipeline executed in background thread."""
        try:
            self._results = []

            # ── Step 1: Create DB session ──────────────────────────
            scan_session = self.db.create_scan_session()
            self._session_id = scan_session.id
            self._emit_status("🔍 Loading installed applications...")

            # ── Step 2: Get installed apps (registry + pkg managers)
            registry_apps = self.registry.get_installed_apps()
            pkg_apps = self.pkg_manager.get_all_apps()
            all_apps = registry_apps + pkg_apps

            # Cache to database
            self.db.cache_installed_apps(all_apps)

            installed_names = {app["name"].lower() for app in all_apps}
            installed_locations = self.registry.get_installed_locations()

            self._emit_status(f"✅ Found {len(all_apps)} installed applications")
            app_logger.info(f"Total known apps: {len(all_apps)}")

            # ── Step 3: Build risk analyzer ────────────────────────
            analyzer = RiskAnalyzer(installed_names)

            # ── Step 4: Scan orphaned registry keys ────────────────
            self._emit_status("🔍 Scanning registry for orphaned keys...")
            orphaned_keys = self.registry.find_orphaned_registry_keys()
            classified_keys = analyzer.classify_batch(orphaned_keys)
            self._results.extend(classified_keys)
            for item in classified_keys:
                if self.on_item_found:
                    self.on_item_found(item)

            self._emit_status(f"Registry: {len(classified_keys)} orphaned keys found")

            # ── Step 5: File system scan ───────────────────────────
            self._emit_status("🔍 Scanning file system...")

            self._file_scanner = FileScanner(
                installed_locations=installed_locations,
                installed_app_names=installed_names,
            )

            # Wire progress callbacks
            def on_item(item):
                classified = analyzer.classify(item)
                self._results.append(classified)
                if self.on_item_found:
                    self.on_item_found(classified)

            def on_progress(msg, count):
                if self.on_progress:
                    self.on_progress(msg, count)

            self._file_scanner.on_item_found = on_item
            self._file_scanner.on_status = self._emit_status
            self._file_scanner.on_progress = on_progress

            # Load user-defined custom scan paths from config
            try:
                from tracezero.utils.config import get_custom_paths
                from pathlib import Path as _Path
                custom = [_Path(p) for p in get_custom_paths() if _Path(p).exists()]
                if custom:
                    self._emit_status(f"📂 Including {len(custom)} custom path(s)...")
            except Exception:
                custom = []

            file_results = self._file_scanner.scan(custom_paths=custom)

            # ── Step 5b: Browser Privacy Scan ──────────────────────
            self._emit_status("🔍 Scanning browser privacy artifacts...")
            browser_scanner = BrowserScanner()
            browser_results = browser_scanner.scan()
            
            for item in browser_results:
                self._results.append(item)
                if self.on_item_found:
                    self.on_item_found(item)

            self._emit_status(f"Browsers: {len(browser_results)} artifacts found")

            # ── Step 5c: Windows Deep OS Scan ──────────────────────
            self._emit_status("🔍 Scanning deep OS artifacts (Prefetch/Update Cache)...")
            deep_scanner = WindowsDeepScanner()
            deep_results = deep_scanner.scan()
            
            for item in deep_results:
                self._results.append(item)
                if self.on_item_found:
                    self.on_item_found(item)

            self._emit_status(f"Deep OS: {len(deep_results)} artifacts found")

            # ── Step 6: Persist results ────────────────────────────
            total_size = sum(item.get("size_bytes", 0) for item in self._results)
            self.db.finish_scan_session(
                self._session_id,
                total_items=len(self._results),
                total_size=total_size
            )

            if len(self._results) > 0:
                self.db.save_detected_items(self._session_id, self._results[:500])  # Save first 500

            self._emit_status(f"✅ Scan complete! Found {len(self._results)} items")
            app_logger.info(f"Scan finished. Total: {len(self._results)} items, Size: {total_size:,.0f} bytes")

            if self.on_complete:
                self.on_complete(self._results)

        except Exception as e:
            app_logger.error(f"Scan engine error: {e}", exc_info=True)
            if self.on_error:
                self.on_error(str(e))
        finally:
            self._is_running = False

    def _emit_status(self, message: str):
        """Emit a status message."""
        if self.on_status:
            self.on_status(message)
