"""
utils/helpers.py

Common utility functions used across the application:
- Human-readable file sizes
- Path safety checks
- Date formatting
- File age calculations
"""

import os
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from tracezero.utils.constants import (
    FORBIDDEN_PATHS_NORMALIZED,
    FORBIDDEN_PATH_KEYWORDS,
    PROTECTED_KEYWORDS,
    OLD_FILE_DAYS,
)


def format_size(size_bytes: int) -> str:
    """Convert bytes to human-readable string (e.g., 1.23 GB)."""
    if size_bytes < 0:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def format_date(timestamp: float) -> str:
    """Convert Unix timestamp to readable date string."""
    try:
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
    except (OSError, ValueError, OverflowError):
        return "Unknown"


def get_file_age_days(path: Path) -> Optional[int]:
    """
    Calculate how many days since a file was last accessed.

    Returns:
        Number of days since last access, or None if can't determine.
    """
    try:
        stat = path.stat()
        last_access = stat.st_atime
        age_seconds = time.time() - last_access
        return int(age_seconds / 86400)
    except (OSError, PermissionError):
        return None


def get_dir_size(path: Path) -> int:
    """
    Recursively calculate total size of a directory.

    Returns:
        Total size in bytes.
    """
    total = 0
    try:
        for entry in os.scandir(path):
            try:
                if entry.is_dir(follow_symlinks=False):
                    total += get_dir_size(Path(entry.path))
                else:
                    total += entry.stat(follow_symlinks=False).st_size
            except (PermissionError, OSError):
                continue
    except (PermissionError, OSError):
        pass
    return total


def is_path_safe(path: Path) -> bool:
    """
    Check if a path is safe to scan/delete.

    Rules:
    1. Path must exist
    2. Path must not be in FORBIDDEN_PATHS
    3. Path string must not contain forbidden keywords
    4. Path must not be a Windows drive root

    Returns:
        True if safe, False if forbidden.
    """
    try:
        path_str = str(path).lower()

        # Block Windows drive roots (C:\, D:\, etc.)
        if len(path_str) <= 3 and path_str[1:] in [":\\", ":/", ":"]:
            return False

        # Check against forbidden path list
        for forbidden in FORBIDDEN_PATHS_NORMALIZED:
            # Exact match or starts-with check
            if path_str == forbidden or path_str.startswith(forbidden + "\\") or path_str.startswith(forbidden + "/"):
                return False

        # Check for forbidden keywords in path
        for keyword in FORBIDDEN_PATH_KEYWORDS:
            if keyword in path_str:
                return False

        return True
    except Exception:
        return False  # If in doubt, block it


def is_protected_package(name: str) -> bool:
    """
    Check if an application name matches a protected system package.

    Args:
        name: Application or folder name to check.

    Returns:
        True if it matches a protected package name.
    """
    name_lower = name.lower()
    for keyword in PROTECTED_KEYWORDS:
        if keyword in name_lower:
            return True
    return False


def compute_file_hash(path: Path, algorithm: str = "md5") -> Optional[str]:
    """
    Compute file hash for duplicate/integrity detection.

    Args:
        path: Path to file.
        algorithm: Hash algorithm ('md5', 'sha256').

    Returns:
        Hex digest string, or None on error.
    """
    try:
        h = hashlib.new(algorithm)
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except (OSError, PermissionError):
        return None


def truncate_path(path: str, max_len: int = 60) -> str:
    """Shorten a long path for display, keeping the end intact."""
    if not path or path.strip() == "":
        return "(unknown path)"
    if len(path) <= max_len:
        return path
    # Show filename + partial parent
    from pathlib import Path as _Path
    try:
        name = _Path(path).name
        if len(name) >= max_len - 6:
            return "..." + path[-(max_len - 3):]
        return "..." + path[-(max_len - 3):]
    except Exception:
        return "..." + path[-(max_len - 3):]


def get_folder_item_count(path: Path) -> int:
    """Count items (files + dirs) directly inside a folder (not recursive)."""
    try:
        return sum(1 for _ in path.iterdir())
    except (PermissionError, OSError):
        return 0
