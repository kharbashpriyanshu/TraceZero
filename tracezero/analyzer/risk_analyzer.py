"""
analyzer/risk_analyzer.py

AI-like classification engine for detected leftover items.
Assigns Safe / Review / Risky labels and generates human-readable reasons.

Classification rules are based on:
- File age (last accessed)
- File/folder type
- Category (cache, log, crash_dump, etc.)
- Whether the parent app is installed
- File extension risk profile
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from tracezero.utils.constants import (
    RISK_SAFE, RISK_REVIEW, RISK_RISKY,
    CACHE_EXTENSIONS, LOG_EXTENSIONS, CRASH_DUMP_EXTENSIONS,
    OLD_FILE_DAYS, LARGE_FILE_THRESHOLD,
)
from tracezero.utils.helpers import is_protected_package


# Extensions that are almost certainly safe to delete
DEFINITELY_SAFE_EXTENSIONS = {
    ".tmp", ".temp", ".cache", ".log", ".bak", ".old",
    ".crdownload", ".part", ".dmp", ".mdmp",
}

# Extensions that need human review
REVIEW_EXTENSIONS = {
    ".db", ".sqlite", ".dat", ".json", ".xml", ".ini", ".cfg",
}

# Extensions that should be treated carefully
RISKY_EXTENSIONS = {
    ".exe", ".dll", ".sys", ".bat", ".cmd", ".ps1", ".reg",
}


class RiskAnalyzer:
    """
    Assigns risk levels and explanations to detected leftover items.

    Usage:
        analyzer = RiskAnalyzer(installed_app_names)
        risk, reason = analyzer.classify(item_dict)
    """

    def __init__(self, installed_app_names: set = None):
        """
        Args:
            installed_app_names: Set of lowercase installed app names for cross-referencing.
        """
        self.installed_app_names = installed_app_names or set()
        self._now = time.time()

    def classify(self, item: Dict) -> Dict:
        """
        Classify a detected item and enrich it with risk_level and reason.

        Args:
            item: Dict with keys: path, item_type, category, size_bytes,
                  age_days, app_name, etc.

        Returns:
            Same dict, enriched with 'risk_level' and 'reason'.
        """
        path_str = item.get("path", "")
        item_type = item.get("item_type", "file")
        category = item.get("category", "")
        app_name = item.get("app_name", "").lower()
        age_days = item.get("age_days") or 0
        size_bytes = item.get("size_bytes", 0)

        path = Path(path_str)
        ext = path.suffix.lower() if path_str else ""

        # ── RULE 1: Never flag protected packages ──────────────────
        if is_protected_package(app_name) or is_protected_package(path_str):
            item["risk_level"] = RISK_RISKY
            item["reason"] = "Protected system dependency - DO NOT delete"
            return item

        # ── RULE 2: Registry leftovers ─────────────────────────────
        if item_type == "registry":
            # Check if any installed app matches this registry key
            if any(app_name in installed for installed in self.installed_app_names):
                item["risk_level"] = RISK_REVIEW
                item["reason"] = f"Registry key may belong to still-installed app: {app_name}"
            else:
                item["risk_level"] = RISK_SAFE
                item["reason"] = "Orphaned registry key - no matching installed app found"
            return item

        # ── RULE 3: Shortcuts ──────────────────────────────────────
        if item_type == "shortcut" or category == "dead_shortcut":
            item["risk_level"] = RISK_SAFE
            item["reason"] = "Dead shortcut pointing to non-existent target"
            return item

        # ── RULE 4: Crash dumps and core dumps ────────────────────
        if category == "crash_dump" or ext in CRASH_DUMP_EXTENSIONS:
            item["risk_level"] = RISK_SAFE
            item["reason"] = "Crash dump file - safe to remove after review"
            return item

        # ── RULE 5: Cache files ────────────────────────────────────
        if category == "cache" or ext in CACHE_EXTENSIONS:
            if age_days > OLD_FILE_DAYS:
                item["risk_level"] = RISK_SAFE
                item["reason"] = f"Old cache file not accessed in {age_days} days"
            else:
                item["risk_level"] = RISK_REVIEW
                item["reason"] = f"Cache file accessed {age_days} days ago - verify before deleting"
            return item

        # ── RULE 6: Log files ──────────────────────────────────────
        if category == "log" or ext in LOG_EXTENSIONS:
            item["risk_level"] = RISK_SAFE
            item["reason"] = "Application log file - safe to clean"
            return item

        # ── RULE 7: Temp files ─────────────────────────────────────
        if category == "temp" or ext in {".tmp", ".temp"}:
            item["risk_level"] = RISK_SAFE
            item["reason"] = "Temporary file"
            return item

        # ── RULE 8: Extension-based risk ──────────────────────────
        if ext in RISKY_EXTENSIONS:
            # Check if parent app is still installed
            if app_name and any(app_name in installed for installed in self.installed_app_names):
                item["risk_level"] = RISK_RISKY
                item["reason"] = f"Executable/system file for installed app '{app_name}' - do not delete"
            else:
                item["risk_level"] = RISK_REVIEW
                item["reason"] = f"Executable-type file with no active app reference"
            return item

        # ── RULE 9: Definitely safe extensions ────────────────────
        if ext in DEFINITELY_SAFE_EXTENSIONS:
            item["risk_level"] = RISK_SAFE
            item["reason"] = f"Safe file type ({ext}) - orphaned leftover"
            return item

        # ── RULE 10: Age-based classification ─────────────────────
        if age_days > OLD_FILE_DAYS * 2:  # > 6 months
            item["risk_level"] = RISK_SAFE
            item["reason"] = f"Very old file - not accessed in {age_days} days"
        elif age_days > OLD_FILE_DAYS:
            item["risk_level"] = RISK_REVIEW
            item["reason"] = f"Old file ({age_days} days) - likely leftover"
        else:
            item["risk_level"] = RISK_REVIEW
            item["reason"] = "Possible leftover - verify before deleting"

        # ── RULE 11: Large orphaned folder ────────────────────────
        if size_bytes > LARGE_FILE_THRESHOLD and not app_name:
            item["risk_level"] = RISK_REVIEW
            item["reason"] = f"Large orphaned folder ({size_bytes // (1024**2)} MB) - review carefully"

        return item

    def classify_batch(self, items: list) -> list:
        """Classify a list of items. Returns enriched list."""
        return [self.classify(item) for item in items]
