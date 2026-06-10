"""
utils/config.py — TraceZero

Lightweight JSON config manager.
Persists user preferences (custom scan paths, theme, etc.) to disk.
"""

import json
from pathlib import Path
from tracezero.utils.constants import APP_DATA_DIR
from tracezero.utils.logger import app_logger

CONFIG_FILE = APP_DATA_DIR / "config.json"

_DEFAULTS = {
    "custom_scan_paths": [],
    "theme": "dark",
    "scan_appdata": True,
    "scan_program_files": True,
    "scan_programdata": True,
    "scan_temp": True,
    "scan_registry": True,
    "scan_shortcuts": True,
    "old_file_days": 90,
    "auto_select_safe": False,
    "language": "en",
}


def _load() -> dict:
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Fill missing keys with defaults
            for k, v in _DEFAULTS.items():
                data.setdefault(k, v)
            return data
    except Exception as e:
        app_logger.warning(f"Config load failed: {e}")
    return dict(_DEFAULTS)


def _save(data: dict):
    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        app_logger.warning(f"Config save failed: {e}")


# ── Public API ────────────────────────────────────────────────

def get(key: str):
    return _load().get(key, _DEFAULTS.get(key))


def set(key: str, value):
    data = _load()
    data[key] = value
    _save(data)


def get_custom_paths() -> list[str]:
    return _load().get("custom_scan_paths", [])


def add_custom_path(path: str):
    data = _load()
    paths = data.get("custom_scan_paths", [])
    if path not in paths:
        paths.append(path)
        data["custom_scan_paths"] = paths
        _save(data)


def remove_custom_path(path: str):
    data = _load()
    paths = data.get("custom_scan_paths", [])
    if path in paths:
        paths.remove(path)
        data["custom_scan_paths"] = paths
        _save(data)
