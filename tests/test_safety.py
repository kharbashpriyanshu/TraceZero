"""
tests/test_safety.py

Safety tests for TraceZero.
Ensures that forbidden paths are NEVER scanned or deleted.
Run with: python -m pytest tests/
"""

import sys
import os
import pytest
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tracezero.utils.helpers import is_path_safe, is_protected_package
from tracezero.utils.constants import FORBIDDEN_PATHS


class TestPathSafety:
    """Verify that forbidden paths are correctly blocked."""

    def test_windows_system32_blocked(self):
        assert is_path_safe(Path(r"C:\Windows\System32")) is False

    def test_windows_folder_blocked(self):
        assert is_path_safe(Path(r"C:\Windows")) is False

    def test_windows_syswow64_blocked(self):
        assert is_path_safe(Path(r"C:\Windows\SysWOW64")) is False

    def test_recovery_blocked(self):
        assert is_path_safe(Path(r"C:\Recovery")) is False

    def test_boot_blocked(self):
        assert is_path_safe(Path(r"C:\Boot")) is False

    def test_appdata_safe(self):
        """AppData should be allowed."""
        home = Path.home()
        appdata = home / "AppData" / "Local" / "SomeApp"
        assert is_path_safe(appdata) is True

    def test_programfiles_safe(self):
        """Program Files should be allowed (for scanning, not deletion of system files)."""
        assert is_path_safe(Path(r"C:\Program Files\SomeApp")) is True

    def test_drive_root_blocked(self):
        """Drive roots should be blocked."""
        assert is_path_safe(Path("C:\\")) is False

    def test_system_volume_blocked(self):
        assert is_path_safe(Path(r"C:\System Volume Information")) is False


class TestProtectedPackages:
    """Test that protected system packages are correctly identified."""

    def test_visual_cpp_protected(self):
        assert is_protected_package("Microsoft Visual C++ 2022 Redistributable") is True

    def test_vcredist_protected(self):
        assert is_protected_package("vcredist_x64.exe") is True

    def test_dotnet_protected(self):
        assert is_protected_package(".NET Framework 4.8") is True

    def test_java_protected(self):
        assert is_protected_package("Java Runtime Environment") is True

    def test_directx_protected(self):
        assert is_protected_package("DirectX Runtime") is True

    def test_random_app_not_protected(self):
        assert is_protected_package("MyRandomApp") is False

    def test_game_not_protected(self):
        assert is_protected_package("Steam Game Leftover") is False


class TestHelpers:
    """Test utility helper functions."""

    def test_format_size_bytes(self):
        from tracezero.utils.helpers import format_size
        assert "B" in format_size(512)

    def test_format_size_kb(self):
        from tracezero.utils.helpers import format_size
        assert "KB" in format_size(2048)

    def test_format_size_mb(self):
        from tracezero.utils.helpers import format_size
        assert "MB" in format_size(2 * 1024 * 1024)

    def test_format_size_gb(self):
        from tracezero.utils.helpers import format_size
        assert "GB" in format_size(2 * 1024 * 1024 * 1024)

    def test_truncate_path(self):
        from tracezero.utils.helpers import truncate_path
        long_path = "C:\\Users\\User\\AppData\\Local\\SomeApp\\Cache\\subdir\\file.txt"
        result = truncate_path(long_path, 30)
        assert len(result) <= 30

    def test_is_path_safe_none_like(self):
        """Empty path should not crash."""
        assert is_path_safe(Path("")) is False or is_path_safe(Path("")) is True  # Graceful handling


class TestRiskAnalyzer:
    """Test risk classification logic."""

    def setup_method(self):
        from tracezero.analyzer.risk_analyzer import RiskAnalyzer
        self.analyzer = RiskAnalyzer(installed_app_names={"chromium", "firefox"})

    def test_cache_file_classified(self):
        item = {
            "path": r"C:\Users\User\AppData\Local\SomeApp\Cache\data.cache",
            "item_type": "file",
            "category": "cache",
            "age_days": 120,
            "size_bytes": 1024,
            "app_name": "SomeApp",
            "risk_level": "",
            "reason": "",
        }
        result = self.analyzer.classify(item)
        assert result["risk_level"] in ("Safe", "Review")

    def test_registry_item_classified(self):
        item = {
            "path": r"HKCU\SOFTWARE\OldApp",
            "item_type": "registry",
            "category": "registry",
            "age_days": 0,
            "size_bytes": 0,
            "app_name": "oldapp",
            "risk_level": "",
            "reason": "",
        }
        result = self.analyzer.classify(item)
        assert result["risk_level"] in ("Safe", "Review", "Risky")

    def test_protected_package_not_deletable(self):
        item = {
            "path": r"C:\Program Files\Microsoft Visual C++ Redistributable\vc_redist.exe",
            "item_type": "file",
            "category": "leftover",
            "age_days": 500,
            "size_bytes": 1024,
            "app_name": "microsoft visual c++",
            "risk_level": "",
            "reason": "",
        }
        result = self.analyzer.classify(item)
        assert result["risk_level"] == "Risky"  # Should be blocked


class TestDatabase:
    """Test database operations."""

    def setup_method(self):
        """Use an in-memory database for tests."""
        from tracezero.database.db_manager import DatabaseManager
        import tempfile
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.db = DatabaseManager(db_path=self.tmp_dir / "test.db")

    def test_create_scan_session(self):
        session = self.db.create_scan_session(["path1", "path2"])
        assert session.id is not None
        assert session.status == "running"

    def test_finish_scan_session(self):
        session = self.db.create_scan_session()
        self.db.finish_scan_session(session.id, total_items=42, total_size=1024.0)
        history = self.db.get_scan_history()
        assert len(history) > 0
        assert history[0]["total_items"] == 42

    def test_get_stats_empty(self):
        stats = self.db.get_stats()
        assert "total_scans" in stats
        assert stats["total_scans"] >= 0

    def test_cache_and_retrieve_apps(self):
        apps = [
            {"name": "TestApp", "publisher": "Test", "source": "registry"},
        ]
        self.db.cache_installed_apps(apps)
        retrieved = self.db.get_cached_apps()
        assert any(a["name"] == "TestApp" for a in retrieved)
