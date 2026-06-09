"""
scanner/windows_deep_scanner.py — TraceZero

Scanner module targeting deep Windows OS caches and residues:
- Windows Prefetch (Tracks every launched application)
- SoftwareDistribution/Download (Windows Update leftover installation files)

Note: These paths usually require Administrator privileges to access.
"""

import os
import time
from pathlib import Path
from typing import List, Dict

from tracezero.utils.constants import RISK_SAFE
from tracezero.utils.logger import app_logger

class WindowsDeepScanner:
    """
    Scans for deep Windows OS artifacts.
    Returns results in the same format as FileScanner so they can be seamlessly
    integrated into the scan engine and UI.
    """

    DEEP_PATHS = {
        "Prefetch": Path(os.environ.get("WINDIR", r"C:\Windows")) / "Prefetch",
        "Windows Update Cache": Path(os.environ.get("WINDIR", r"C:\Windows")) / "SoftwareDistribution" / "Download"
    }

    def __init__(self):
        self.results = []

    def scan(self) -> List[Dict]:
        """
        Executes the scan across deep Windows paths.
        Returns a list of item dictionaries.
        """
        self.results = []
        app_logger.info("Starting Windows Deep Core scan...")

        for category_name, path in self.DEEP_PATHS.items():
            if path.exists():
                self._scan_directory(path, category_name)

        app_logger.info(f"Windows Deep Core scan complete. Found {len(self.results)} items.")
        return self.results

    def _scan_directory(self, directory: Path, category: str):
        """Recursively scans a deep OS directory."""
        try:
            for root, dirs, files in os.walk(directory):
                # Don't go too deep to avoid permission loops
                depth = root[len(str(directory)):].count(os.sep)
                if depth > 3:
                    continue
                
                # We could add the files individually, but SoftwareDistribution often has 
                # thousands of files. Better to add the folders or chunk them.
                # Let's add files individually for Prefetch, but maybe folders for Update Cache.
                
                if category == "Prefetch":
                    for f in files:
                        if f.lower().endswith(".pf"):
                            full_path = Path(root) / f
                            self._add_result(full_path, "file", "Windows Prefetch Log", "Windows OS")
                
                elif category == "Windows Update Cache":
                    # For SoftwareDistribution/Download, we usually delete the files and folders inside it
                    # Just add everything inside the root of Download directory
                    if Path(root) == directory:
                        for d in dirs:
                            full_path = Path(root) / d
                            self._add_result(full_path, "folder", "Windows Update Residue", "Windows Update")
                        for f in files:
                            full_path = Path(root) / f
                            self._add_result(full_path, "file", "Windows Update Residue", "Windows Update")
                        # Break after root level to group them logically
                        break
                        
        except PermissionError:
            app_logger.warning(f"Permission denied accessing {directory}. Run as Admin for deep scan.")
        except Exception as e:
            app_logger.error(f"Error scanning {category}: {e}")

    def _add_result(self, path: Path, item_type: str, category: str, app_name: str):
        """Helper to format and append a result dictionary."""
        try:
            stat = path.stat()
            size = stat.st_size
            
            # Estimate folder size
            if item_type == "folder":
                try:
                    size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                except Exception:
                    size = 0
                
            age_days = (time.time() - stat.st_atime) / (24 * 3600)
            
            self.results.append({
                "path": str(path),
                "item_type": item_type,
                "category": category,
                "app_name": app_name,
                "size_bytes": size,
                "age_days": age_days,
                "risk_level": RISK_SAFE, 
                "reason": "Deep OS cleanup (Safe to delete)"
            })
        except Exception:
            pass
