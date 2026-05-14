"""
registry/package_managers.py

Detects applications installed via third-party package managers:
- Winget (Windows Package Manager)
- Chocolatey
- Steam
- Epic Games Launcher

Returns a unified list of installed app dicts.
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from typing import List, Dict

from app_trace_cleaner.utils.logger import app_logger


class PackageManagerDetector:
    """Detects apps installed via Winget, Chocolatey, Steam, and Epic Games."""

    def get_all_apps(self) -> List[Dict]:
        """Run all detectors and return combined app list."""
        all_apps = []
        all_apps.extend(self._get_winget_apps())
        all_apps.extend(self._get_chocolatey_apps())
        all_apps.extend(self._get_steam_apps())
        all_apps.extend(self._get_epic_apps())
        return all_apps

    # ─────────────────────────────────────────────
    #  WINGET
    # ─────────────────────────────────────────────

    def _get_winget_apps(self) -> List[Dict]:
        """Get list of apps installed via winget."""
        apps = []
        try:
            result = subprocess.run(
                ["winget", "list", "--accept-source-agreements"],
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            lines = result.stdout.splitlines()

            # Skip header lines (first 3 lines are header/separator)
            data_started = False
            for line in lines:
                if "------" in line:
                    data_started = True
                    continue
                if not data_started or not line.strip():
                    continue

                parts = line.split()
                if parts:
                    # Winget format: Name Id Version Available Source
                    name = parts[0] if parts else "Unknown"
                    apps.append({
                        "name": name,
                        "publisher": "",
                        "version": parts[2] if len(parts) > 2 else "",
                        "install_location": "",
                        "source": "winget",
                    })

            app_logger.info(f"Winget: found {len(apps)} apps")
        except FileNotFoundError:
            app_logger.info("Winget not found on this system.")
        except subprocess.TimeoutExpired:
            app_logger.warning("Winget timed out.")
        except Exception as e:
            app_logger.warning(f"Error reading winget apps: {e}")
        return apps

    # ─────────────────────────────────────────────
    #  CHOCOLATEY
    # ─────────────────────────────────────────────

    def _get_chocolatey_apps(self) -> List[Dict]:
        """Get list of apps installed via Chocolatey."""
        apps = []
        try:
            result = subprocess.run(
                ["choco", "list", "--local-only"],
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            for line in result.stdout.splitlines():
                parts = line.strip().split(" ")
                if len(parts) >= 1 and parts[0] and not parts[0].startswith("#"):
                    apps.append({
                        "name": parts[0],
                        "version": parts[1] if len(parts) > 1 else "",
                        "publisher": "",
                        "install_location": str(Path(os.environ.get("ChocolateyInstall", r"C:\ProgramData\chocolatey")) / "lib" / parts[0]),
                        "source": "chocolatey",
                    })
            app_logger.info(f"Chocolatey: found {len(apps)} apps")
        except FileNotFoundError:
            app_logger.info("Chocolatey not found on this system.")
        except subprocess.TimeoutExpired:
            app_logger.warning("Chocolatey timed out.")
        except Exception as e:
            app_logger.warning(f"Error reading Chocolatey apps: {e}")
        return apps

    # ─────────────────────────────────────────────
    #  STEAM
    # ─────────────────────────────────────────────

    def _get_steam_apps(self) -> List[Dict]:
        """
        Detect Steam-installed games by reading steamapps manifests.
        Looks in default Steam library and VDF library folders.
        """
        apps = []

        # Common Steam installation paths
        steam_paths = [
            Path(r"C:\Program Files (x86)\Steam\steamapps"),
            Path(r"C:\Program Files\Steam\steamapps"),
            Path(os.path.expanduser("~")) / "Steam" / "steamapps",
        ]

        # Also check the registry for Steam path
        if sys.platform == "win32":
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
                    steam_path_val, _ = winreg.QueryValueEx(key, "SteamPath")
                    steam_paths.insert(0, Path(steam_path_val) / "steamapps")
            except (ImportError, OSError):
                pass

        for steamapps_path in steam_paths:
            if not steamapps_path.exists():
                continue
            try:
                for manifest in steamapps_path.glob("appmanifest_*.acf"):
                    app_info = self._parse_acf(manifest)
                    if app_info:
                        apps.append(app_info)
            except (PermissionError, OSError):
                continue

        app_logger.info(f"Steam: found {len(apps)} games")
        return apps

    def _parse_acf(self, path: Path) -> Dict:
        """Parse a Steam .acf manifest file."""
        try:
            data = {}
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip().strip('"')
                    if "\"\t\t\"" in line:
                        parts = line.split("\"\t\t\"")
                        if len(parts) == 2:
                            data[parts[0].strip('"')] = parts[1].strip('"')

            name = data.get("name", "")
            if not name:
                return None

            install_dir = data.get("installdir", "")
            full_path = str(path.parent / "common" / install_dir) if install_dir else ""

            return {
                "name": name,
                "publisher": "Steam",
                "version": data.get("buildid", ""),
                "install_location": full_path,
                "source": "steam",
            }
        except Exception:
            return None

    # ─────────────────────────────────────────────
    #  EPIC GAMES
    # ─────────────────────────────────────────────

    def _get_epic_apps(self) -> List[Dict]:
        """
        Detect Epic Games Launcher installed games.
        Reads from the Epic Games manifests folder.
        """
        apps = []
        epic_manifest_paths = [
            Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")) / "Epic" / "EpicGamesLauncher" / "Data" / "Manifests",
        ]

        for manifest_dir in epic_manifest_paths:
            if not manifest_dir.exists():
                continue
            try:
                for item_file in manifest_dir.glob("*.item"):
                    app_info = self._parse_epic_item(item_file)
                    if app_info:
                        apps.append(app_info)
            except (PermissionError, OSError):
                continue

        app_logger.info(f"Epic Games: found {len(apps)} games")
        return apps

    def _parse_epic_item(self, path: Path) -> Dict:
        """Parse an Epic Games .item manifest file (JSON)."""
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)

            name = data.get("DisplayName", data.get("AppName", ""))
            if not name:
                return None

            return {
                "name": name,
                "publisher": data.get("DeveloperName", "Epic Games"),
                "version": data.get("AppVersionString", ""),
                "install_location": data.get("InstallLocation", ""),
                "source": "epic",
            }
        except Exception:
            return None
