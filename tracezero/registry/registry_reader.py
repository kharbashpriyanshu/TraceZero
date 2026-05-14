"""
registry/registry_reader.py

Reads installed application information from the Windows Registry.
Covers both 64-bit and 32-bit application entries.

Also detects orphaned registry keys left by uninstalled apps.
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Optional

from tracezero.utils.logger import app_logger
from tracezero.utils.constants import REGISTRY_SCAN_PATHS
from tracezero.utils.helpers import is_protected_package

# Windows-only imports
if sys.platform == "win32":
    import winreg
else:
    winreg = None  # Non-Windows stub for development


class RegistryReader:
    """
    Reads installed application data from the Windows Registry.

    Scans:
    - HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall
    - HKLM\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall
    - HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall
    """

    def __init__(self):
        self.installed_apps: List[Dict] = []
        self.orphaned_keys: List[Dict] = []

    def get_installed_apps(self) -> List[Dict]:
        """
        Read all installed applications from Windows Registry.

        Returns:
            List of app dicts with keys:
            name, publisher, install_location, install_date, version,
            uninstall_string, source
        """
        if sys.platform != "win32":
            app_logger.warning("Registry reading only supported on Windows.")
            return []

        apps = []
        scan_targets = [
            # (hive, path, hive_name)
            (winreg.HKEY_LOCAL_MACHINE, REGISTRY_SCAN_PATHS["uninstall_hklm"], "HKLM"),
            (winreg.HKEY_LOCAL_MACHINE, REGISTRY_SCAN_PATHS["uninstall_hklm_wow"], "HKLM_WOW"),
            (winreg.HKEY_CURRENT_USER, REGISTRY_SCAN_PATHS["uninstall_hkcu"], "HKCU"),
        ]

        seen_names = set()

        for hive, path, hive_name in scan_targets:
            try:
                entries = self._read_uninstall_key(hive, path, hive_name)
                for app in entries:
                    name = app.get("name", "").strip()
                    if name and name not in seen_names:
                        seen_names.add(name)
                        apps.append(app)
            except Exception as e:
                app_logger.error(f"Error reading {hive_name}\\{path}: {e}")

        self.installed_apps = apps
        app_logger.info(f"Found {len(apps)} installed applications in registry.")
        return apps

    def _read_uninstall_key(self, hive, path: str, source: str) -> List[Dict]:
        """
        Read all subkeys under an Uninstall registry path.

        Args:
            hive: Registry hive constant (HKEY_LOCAL_MACHINE, etc.)
            path: Registry path string
            source: Human-readable hive name for logging

        Returns:
            List of app information dicts.
        """
        apps = []
        try:
            with winreg.OpenKey(hive, path, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
                index = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, index)
                        index += 1
                    except OSError:
                        break  # No more subkeys

                    try:
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            app = self._parse_app_key(subkey, subkey_name, source)
                            if app:
                                apps.append(app)
                    except (PermissionError, OSError):
                        continue

        except FileNotFoundError:
            pass  # Key doesn't exist – normal on some systems
        except PermissionError as e:
            app_logger.warning(f"Permission denied reading {source}\\{path}: {e}")

        return apps

    def _parse_app_key(self, key, key_name: str, source: str) -> Optional[Dict]:
        """
        Extract app information from a single registry subkey.

        Returns:
            Dict with app info, or None if this entry should be skipped.
        """
        def get_val(name: str) -> str:
            try:
                value, _ = winreg.QueryValueEx(key, name)
                return str(value).strip()
            except (FileNotFoundError, OSError):
                return ""

        name = get_val("DisplayName")
        if not name:
            return None  # Skip nameless entries

        # Skip system components and protected packages
        system_component = get_val("SystemComponent")
        if system_component == "1":
            return None

        if is_protected_package(name):
            return None

        return {
            "name": name,
            "publisher": get_val("Publisher"),
            "version": get_val("DisplayVersion"),
            "install_location": get_val("InstallLocation"),
            "install_date": get_val("InstallDate"),
            "uninstall_string": get_val("UninstallString"),
            "source": "registry",
            "registry_key": key_name,
        }

    def get_installed_app_names(self) -> set:
        """Return a set of installed app name fragments (lowercase)."""
        if not self.installed_apps:
            self.get_installed_apps()
        return {app["name"].lower() for app in self.installed_apps}

    def get_installed_locations(self) -> set:
        """Return a set of known install location paths (normalized lowercase)."""
        if not self.installed_apps:
            self.get_installed_apps()
        locations = set()
        for app in self.installed_apps:
            loc = app.get("install_location", "")
            if loc:
                locations.add(loc.lower().rstrip("\\").rstrip("/"))
        return locations

    def find_orphaned_registry_keys(self) -> List[Dict]:
        """
        Scan HKCU\\SOFTWARE for keys whose associated application is no longer installed.
        Cross-references against the installed apps list.

        Returns:
            List of orphaned registry key dicts.
        """
        if sys.platform != "win32":
            return []

        if not self.installed_apps:
            self.get_installed_apps()

        installed_names = self.get_installed_app_names()
        orphaned = []

        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                "SOFTWARE",
                0,
                winreg.KEY_READ
            ) as software_key:
                index = 0
                while True:
                    try:
                        company_name = winreg.EnumKey(software_key, index)
                        index += 1
                    except OSError:
                        break

                    # Skip Microsoft and Windows keys
                    if company_name.lower() in ("microsoft", "windows", "classes"):
                        continue

                    # Check if any installed app references this company
                    is_known = any(
                        company_name.lower() in app_name
                        for app_name in installed_names
                    )

                    if not is_known:
                        key_path = f"HKCU\\SOFTWARE\\{company_name}"
                        orphaned.append({
                            "path": key_path,
                            "item_type": "registry",
                            "category": "registry",
                            "risk_level": "Review",
                            "reason": f"No installed app references registry key: {company_name}",
                            "size_bytes": 0,
                            "app_name": company_name,
                        })

        except (PermissionError, OSError) as e:
            app_logger.warning(f"Error scanning SOFTWARE registry: {e}")

        self.orphaned_keys = orphaned
        app_logger.info(f"Found {len(orphaned)} potentially orphaned registry keys.")
        return orphaned
