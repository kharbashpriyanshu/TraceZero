"""
ui/settings_page.py

Settings page for App Trace Cleaner.
Allows configuring:
- Scan paths
- Risk thresholds
- Age thresholds
- Auto-select safe items
- Database management
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QCheckBox, QSlider, QSpinBox, QGroupBox,
    QMessageBox, QFileDialog,
)
from PyQt6.QtCore import Qt

from app_trace_cleaner.utils.constants import (
    APP_DATA_DIR, DATABASE_PATH, OLD_FILE_DAYS, APP_VERSION
)
from app_trace_cleaner.database.db_manager import get_db


class SectionGroup(QGroupBox):
    """A styled settings group box."""
    def __init__(self, title: str):
        super().__init__(title)
        self.setStyleSheet("""
            QGroupBox {
                color: #e6edf3;
                font-weight: 700;
                font-size: 13px;
                border: 1px solid #30363d;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 12px;
                background: #161b22;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 8px;
                color: #58a6ff;
            }
        """)


class SettingsPage(QWidget):
    """Application settings page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 24, 30, 20)
        layout.setSpacing(20)

        # ── Header ───────────────────────────────────────────────
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: #e6edf3; background: transparent;")
        layout.addWidget(title)

        subtitle = QLabel("Configure scan behavior, thresholds, and database settings")
        subtitle.setStyleSheet("font-size: 12px; color: #8b949e; background: transparent;")
        layout.addWidget(subtitle)

        # ── Scan Behavior ─────────────────────────────────────────
        scan_group = SectionGroup("  🔍  Scan Behavior")
        scan_layout = QVBoxLayout(scan_group)
        scan_layout.setSpacing(12)
        scan_layout.setContentsMargins(12, 16, 12, 12)

        self.chk_scan_appdata = QCheckBox("Scan AppData folders (Local, Roaming, LocalLow)")
        self.chk_scan_appdata.setChecked(True)
        self.chk_scan_programfiles = QCheckBox("Scan Program Files (x86 & x64)")
        self.chk_scan_programfiles.setChecked(True)
        self.chk_scan_programdata = QCheckBox("Scan ProgramData folder")
        self.chk_scan_programdata.setChecked(True)
        self.chk_scan_temp = QCheckBox("Scan TEMP folders")
        self.chk_scan_temp.setChecked(True)
        self.chk_scan_registry = QCheckBox("Scan registry for orphaned keys")
        self.chk_scan_registry.setChecked(True)
        self.chk_scan_shortcuts = QCheckBox("Scan for dead shortcuts (.lnk files)")
        self.chk_scan_shortcuts.setChecked(True)

        for chk in [
            self.chk_scan_appdata, self.chk_scan_programfiles,
            self.chk_scan_programdata, self.chk_scan_temp,
            self.chk_scan_registry, self.chk_scan_shortcuts
        ]:
            chk.setStyleSheet("QCheckBox { color: #e6edf3; } QCheckBox::indicator { width: 16px; height: 16px; }")
            scan_layout.addWidget(chk)

        layout.addWidget(scan_group)

        # ── Analysis Thresholds ───────────────────────────────────
        analysis_group = SectionGroup("  🧠  Analysis Thresholds")
        analysis_layout = QVBoxLayout(analysis_group)
        analysis_layout.setContentsMargins(12, 16, 12, 12)
        analysis_layout.setSpacing(14)

        # Old file threshold
        age_row = QHBoxLayout()
        age_label = QLabel("Mark files as 'old' after:")
        age_label.setStyleSheet("color: #e6edf3; background: transparent;")
        age_row.addWidget(age_label)

        self.age_spinbox = QSpinBox()
        self.age_spinbox.setRange(7, 365)
        self.age_spinbox.setValue(OLD_FILE_DAYS)
        self.age_spinbox.setSuffix(" days")
        self.age_spinbox.setFixedWidth(120)
        self.age_spinbox.setStyleSheet("""
            QSpinBox {
                background: #0d1117;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 4px 8px;
                color: #e6edf3;
            }
        """)
        age_row.addWidget(self.age_spinbox)
        age_row.addStretch()
        analysis_layout.addLayout(age_row)

        # Auto-select safe items
        self.chk_auto_select_safe = QCheckBox("Auto-select 'Safe' items for deletion")
        self.chk_auto_select_safe.setChecked(False)
        self.chk_auto_select_safe.setStyleSheet("QCheckBox { color: #e6edf3; }")
        analysis_layout.addWidget(self.chk_auto_select_safe)

        layout.addWidget(analysis_group)

        # ── Database Management ───────────────────────────────────
        db_group = SectionGroup("  🗃  Database & Storage")
        db_layout = QVBoxLayout(db_group)
        db_layout.setContentsMargins(12, 16, 12, 12)
        db_layout.setSpacing(12)

        db_path_label = QLabel(f"Database location: {DATABASE_PATH}")
        db_path_label.setStyleSheet("color: #8b949e; font-size: 11px; background: transparent;")
        db_path_label.setWordWrap(True)
        db_layout.addWidget(db_path_label)

        db_btn_row = QHBoxLayout()
        db_btn_row.setSpacing(10)

        btn_clear_history = QPushButton("🗑  Clear Scan History")
        btn_clear_history.setObjectName("btn_secondary")
        btn_clear_history.clicked.connect(self._clear_scan_history)

        btn_open_db_folder = QPushButton("📁  Open App Data Folder")
        btn_open_db_folder.setObjectName("btn_secondary")
        btn_open_db_folder.clicked.connect(self._open_app_data_folder)

        db_btn_row.addWidget(btn_clear_history)
        db_btn_row.addWidget(btn_open_db_folder)
        db_btn_row.addStretch()
        db_layout.addLayout(db_btn_row)

        layout.addWidget(db_group)

        # ── About Section ─────────────────────────────────────────
        about_group = SectionGroup("  ℹ️  About")
        about_layout = QVBoxLayout(about_group)
        about_layout.setContentsMargins(12, 16, 12, 12)

        about_text = QLabel(
            f"<b>App Trace Cleaner</b> v{APP_VERSION}<br>"
            "A safe, intelligent Windows application trace cleaner.<br><br>"
            "• Scans AppData, Program Files, Temp, Registry<br>"
            "• Never permanently deletes files (uses Recycle Bin)<br>"
            "• Protects system files, drivers, and runtimes<br>"
            "• AI-like risk classification for every item"
        )
        about_text.setStyleSheet("color: #8b949e; font-size: 12px; background: transparent; line-height: 1.6;")
        about_text.setWordWrap(True)
        about_layout.addWidget(about_text)

        layout.addWidget(about_group)
        layout.addStretch()

    def _clear_scan_history(self):
        """Clear all scan history from the database."""
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to clear all scan history?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                from sqlalchemy import text
                with self.db.engine.connect() as conn:
                    conn.execute(text("DELETE FROM scan_sessions"))
                    conn.execute(text("DELETE FROM detected_items"))
                    conn.execute(text("DELETE FROM deleted_items"))
                    conn.commit()
                QMessageBox.information(self, "Done", "Scan history cleared successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not clear history:\n{e}")

    def _open_app_data_folder(self):
        """Open the app data folder in Windows Explorer."""
        import subprocess
        import os
        try:
            subprocess.Popen(f'explorer "{APP_DATA_DIR}"')
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open folder:\n{e}")
