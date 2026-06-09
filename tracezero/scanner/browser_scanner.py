"""
scanner/browser_scanner.py — TraceZero

Scanner module targeting major web browsers (Chrome, Edge, Brave, Firefox)
to detect and clear caches, cookies, history, and other privacy-compromising traces.
"""

import os
import time
from pathlib import Path
from typing import List, Dict

from tracezero.utils.constants import BROWSER_PATHS, RISK_SAFE
from tracezero.utils.logger import app_logger

class BrowserScanner:
    """
    Scans for browser profiles and caches.
    Returns results in the same format as FileScanner so they can be seamlessly
    integrated into the scan engine and UI.
    """

    # Target folders/files within a browser profile (Chromium-based)
    CHROMIUM_TARGETS = [
        "Cache",
        "Code Cache",
        "GPUCache",
        "Network", # Network/Cookies
        "History",
        "Cookies",
        "Login Data",
        "Web Data"
    ]

    def __init__(self):
        self.results = []

    def scan(self) -> List[Dict]:
        """
        Executes the scan across all supported browsers.
        Returns a list of item dictionaries.
        """
        self.results = []
        app_logger.info("Starting browser privacy scan...")

        # 1. Chromium-based browsers (Chrome, Edge, Brave)
        for browser_name in ["Chrome", "Edge", "Brave"]:
            base_path = BROWSER_PATHS.get(browser_name)
            if base_path and base_path.exists():
                self._scan_chromium(base_path, browser_name)

        # 2. Firefox
        firefox_path = BROWSER_PATHS.get("Firefox")
        if firefox_path and firefox_path.exists():
            self._scan_firefox(firefox_path)

        app_logger.info(f"Browser scan complete. Found {len(self.results)} items.")
        return self.results

    def _scan_chromium(self, base_path: Path, browser_name: str):
        """Scans a Chromium-based browser directory (looks inside profiles like 'Default', 'Profile 1')."""
        try:
            # Common profile folders: Default, Profile 1, Profile 2, etc.
            # We'll just iterate through the directory to find them, or just target known ones.
            # But the simplest approach is to look for our targets in the base path and direct subdirectories.
            for root, dirs, files in os.walk(base_path):
                # Don't go too deep. Profiles are usually 1 level down.
                depth = root[len(str(base_path)):].count(os.sep)
                if depth > 2:
                    continue
                
                # Check for target directories (like Cache)
                for d in dirs:
                    if d in self.CHROMIUM_TARGETS:
                        full_path = os.path.join(root, d)
                        self._add_result(full_path, "folder", f"{browser_name} Cache/Data", browser_name)
                
                # Check for specific files (like History)
                for f in files:
                    if f in self.CHROMIUM_TARGETS:
                        full_path = os.path.join(root, f)
                        self._add_result(full_path, "file", f"{browser_name} DB/History", browser_name)
                        
        except Exception as e:
            app_logger.error(f"Error scanning {browser_name}: {e}")

    def _scan_firefox(self, base_path: Path):
        """Scans Firefox profiles."""
        try:
            # Firefox profiles are typically in folders like "xxxxxxxx.default-release"
            for profile_dir in base_path.iterdir():
                if profile_dir.is_dir():
                    # Check for cache and history inside profile
                    # Firefox cache is often stored in Local AppData, but we can look for specific files here
                    places_sqlite = profile_dir / "places.sqlite"  # History and Bookmarks
                    cookies_sqlite = profile_dir / "cookies.sqlite"
                    
                    if places_sqlite.exists():
                        self._add_result(str(places_sqlite), "file", "Firefox History/Bookmarks", "Firefox")
                    if cookies_sqlite.exists():
                        self._add_result(str(cookies_sqlite), "file", "Firefox Cookies", "Firefox")
                        
            # Firefox Cache is usually in AppData/Local/Mozilla/Firefox/Profiles
            local_firefox = Path(os.environ.get("LOCALAPPDATA", "")) / "Mozilla" / "Firefox" / "Profiles"
            if local_firefox.exists():
                for profile_dir in local_firefox.iterdir():
                    if profile_dir.is_dir():
                        cache_dir = profile_dir / "cache2"
                        if cache_dir.exists():
                            self._add_result(str(cache_dir), "folder", "Firefox Cache", "Firefox")

        except Exception as e:
            app_logger.error(f"Error scanning Firefox: {e}")

    def _add_result(self, path: str, item_type: str, category: str, app_name: str):
        """Helper to format and append a result dictionary."""
        try:
            stat = os.stat(path)
            size = stat.st_size
            # If it's a directory, maybe we don't calculate full size right now to save time, or do a quick sum
            if item_type == "folder":
                # Quick estimate or just 0
                size = sum(f.stat().st_size for f in Path(path).glob('**/*') if f.is_file())
                
            age_days = (time.time() - stat.st_atime) / (24 * 3600)
            
            self.results.append({
                "path": str(path),
                "item_type": item_type,
                "category": category,
                "app_name": app_name,
                "size_bytes": size,
                "age_days": age_days,
                "risk_level": RISK_SAFE, # Mark as safe to delete because user explicitly requested a privacy sweep
                "reason": "Browser artifact (Privacy sweep)"
            })
        except Exception:
            pass
