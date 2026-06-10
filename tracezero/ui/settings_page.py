"""
ui/settings_page.py — TraceZero
Premium settings page — Carbon Violet theme, theme-aware, clean layout.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QCheckBox, QSpinBox, QMessageBox, QScrollArea,
    QFileDialog,
)
from PyQt6.QtCore import Qt

from tracezero.utils.constants import (
    APP_DATA_DIR, DATABASE_PATH, OLD_FILE_DAYS, APP_VERSION
)
from tracezero.database.db_manager import get_db
from tracezero.ui.styles import ThemeManager
import tracezero.utils.config as cfg
from tracezero.utils.context_menu import is_context_menu_installed, install_context_menu, remove_context_menu
from tracezero.utils.scheduler import is_task_scheduled, schedule_weekly_cleanup, remove_scheduled_cleanup
from tracezero.utils.i18n import t, get_available_languages
from PyQt6.QtWidgets import QComboBox


class SettingsPage(QWidget):
    """Application settings page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db()

        # Outer layout holds the scroll area
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )
        outer.addWidget(self._scroll)

        # Inner container that holds all cards
        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self._scroll.setWidget(self._container)
        self._scroll.viewport().setStyleSheet("background: transparent;")

        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(36, 24, 36, 24)
        self._layout.setSpacing(16)
        self._populate()

    # ── Helpers ───────────────────────────────────────────────
    def _card(self, p) -> QFrame:
        f = QFrame()
        f.setStyleSheet(f"""
            QFrame {{
                background: {p['card']};
                border: 1px solid {p['border']};
                border-radius: 14px;
            }}
        """)
        return f

    def _hdr(self, icon: str, text: str, p: dict) -> QLabel:
        lbl = QLabel(f"{icon}  {text}")
        lbl.setStyleSheet(
            f"font-size: 11px; font-weight: 800; letter-spacing: 1.2px;"
            f" color: {p['accent2']}; border: none;"
        )
        return lbl

    def _divider(self, p) -> QFrame:
        d = QFrame()
        d.setFixedHeight(1)
        d.setStyleSheet(f"background: {p['border']}; border: none;")
        return d

    def _checkbox(self, text: str, checked: bool, p: dict) -> QCheckBox:
        cb = QCheckBox(text)
        cb.setChecked(checked)
        cb.setStyleSheet(f"""
            QCheckBox {{
                color: {p['t1']};
                font-size: 13px;
                spacing: 10px;
                border: none;
                background: transparent;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 4px;
                border: 1.5px solid {p['border']};
                background: {p['panel']};
            }}
            QCheckBox::indicator:checked {{
                background: {p['accent']};
                border-color: {p['accent']};
                image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='20 6 9 17 4 12'%3E%3C/polyline%3E%3C/svg%3E");
            }}
            QCheckBox::indicator:hover {{
                border-color: {p['accent2']};
            }}
        """)
        return cb

    # ── Build ─────────────────────────────────────────────────
    def _populate(self):
        p = ThemeManager.palette()

        # Header
        title = QLabel("⚙️  Settings")
        title.setStyleSheet(
            f"font-size: 24px; font-weight: 900; color: {p['t1']}; border: none;"
        )
        self._layout.addWidget(title)

        sub = QLabel("Configure scan behavior, thresholds, and database settings")
        sub.setStyleSheet(f"font-size: 13px; color: {p['t2']}; border: none; margin-bottom: 6px;")
        self._layout.addWidget(sub)

        # ── Scan Behavior card ────────────────────────────────
        scan_card = self._card(p)
        sl = QVBoxLayout(scan_card)
        sl.setContentsMargins(22, 18, 22, 18)
        sl.setSpacing(12)
        sl.addWidget(self._hdr("🔍", "SCAN BEHAVIOR", p))
        sl.addWidget(self._divider(p))

        self.chk_scan_appdata      = self._checkbox("Scan AppData folders  (Local, Roaming, LocalLow)", True, p)
        self.chk_scan_programfiles = self._checkbox("Scan Program Files  (x86 & x64)", True, p)
        self.chk_scan_programdata  = self._checkbox("Scan ProgramData folder", True, p)
        self.chk_scan_temp         = self._checkbox("Scan TEMP folders", True, p)
        self.chk_scan_registry     = self._checkbox("Scan registry for orphaned keys", True, p)
        self.chk_scan_shortcuts    = self._checkbox("Scan for dead shortcuts  (.lnk files)", True, p)

        for cb in [self.chk_scan_appdata, self.chk_scan_programfiles,
                   self.chk_scan_programdata, self.chk_scan_temp,
                   self.chk_scan_registry, self.chk_scan_shortcuts]:
            sl.addWidget(cb)

        self._layout.addWidget(scan_card)

        # ── Windows Integration card ──────────────────────────
        win_card = self._card(p)
        wl = QVBoxLayout(win_card)
        wl.setContentsMargins(22, 18, 22, 18)
        wl.setSpacing(14)
        wl.addWidget(self._hdr("🖱", "WINDOWS INTEGRATION", p))
        wl.addWidget(self._divider(p))

        self.chk_context_menu = self._checkbox("Add \"Analyze Space with TraceZero\" to Windows right-click menu", is_context_menu_installed(), p)
        self.chk_context_menu.toggled.connect(self._toggle_context_menu)
        wl.addWidget(self.chk_context_menu)
        
        self.chk_scheduled_scan = self._checkbox("Enable Automatic Weekly Background Cleanups (Every Sunday at 12:00 PM)", is_task_scheduled(), p)
        self.chk_scheduled_scan.toggled.connect(self._toggle_scheduled_scan)
        wl.addWidget(self.chk_scheduled_scan)
        
        self._layout.addWidget(win_card)

        # ── Language card ──────────────────────────
        lang_card = self._card(p)
        ll = QVBoxLayout(lang_card)
        ll.setContentsMargins(22, 18, 22, 18)
        ll.setSpacing(14)
        ll.addWidget(self._hdr("🌐", t("settings.title"), p))
        ll.addWidget(self._divider(p))

        lbl = QLabel(t("settings.lbl"))
        lbl.setStyleSheet(f"color: {p['t1']}; font-weight: 500;")
        ll.addWidget(lbl)

        self.lang_combo = QComboBox()
        self.lang_combo.setFixedSize(250, 36)
        self.lang_combo.setStyleSheet(f"""
            QComboBox {{
                background: {p['bg']}; color: {p['t1']};
                border: 1px solid {p['border']}; border-radius: 6px; padding: 4px 10px;
            }}
            QComboBox::drop-down {{ border: none; }}
        """)
        
        languages = get_available_languages()
        current_lang = cfg.get("language")
        
        for code, name in languages.items():
            self.lang_combo.addItem(name, code)
            
        # Set current
        idx = self.lang_combo.findData(current_lang)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
            
        self.lang_combo.currentIndexChanged.connect(self._change_language)
        ll.addWidget(self.lang_combo)
        
        self._layout.addWidget(lang_card)

        # ── Analysis Thresholds card ──────────────────────────
        analysis_card = self._card(p)
        al = QVBoxLayout(analysis_card)
        al.setContentsMargins(22, 18, 22, 18)
        al.setSpacing(14)
        al.addWidget(self._hdr("🧠", "ANALYSIS THRESHOLDS", p))
        al.addWidget(self._divider(p))

        age_row = QHBoxLayout()
        age_lbl = QLabel("Mark files as 'old' after:")
        age_lbl.setStyleSheet(f"color: {p['t1']}; border: none; font-size: 13px;")
        age_row.addWidget(age_lbl)

        self.age_spinbox = QSpinBox()
        self.age_spinbox.setRange(7, 365)
        self.age_spinbox.setValue(OLD_FILE_DAYS)
        self.age_spinbox.setSuffix("  days")
        self.age_spinbox.setFixedWidth(115)
        self.age_spinbox.setStyleSheet(f"""
            QSpinBox {{
                background: {p['panel']}; border: 1px solid {p['border']};
                border-radius: 8px; padding: 5px 10px;
                color: {p['t1']}; font-weight: 600;
            }}
            QSpinBox:focus {{ border-color: {p['accent']}; }}
            QSpinBox::up-button, QSpinBox::down-button {{ background:transparent; border:none; width:16px; }}
        """)
        age_row.addWidget(self.age_spinbox)
        age_row.addStretch()
        al.addLayout(age_row)

        self.chk_auto_safe = self._checkbox("Auto-select 'Safe' items for deletion", False, p)
        al.addWidget(self.chk_auto_safe)
        self._layout.addWidget(analysis_card)

        # ── Database card ─────────────────────────────────────
        db_card = self._card(p)
        dl = QVBoxLayout(db_card)
        dl.setContentsMargins(22, 18, 22, 18)
        dl.setSpacing(12)
        dl.addWidget(self._hdr("🗃", "DATABASE & STORAGE", p))
        dl.addWidget(self._divider(p))

        db_path_lbl = QLabel(f"📍  {DATABASE_PATH}")
        db_path_lbl.setStyleSheet(
            f"color: {p['t2']}; font-size: 11px; border: none;"
            " font-family: 'Consolas', 'Courier New', monospace;"
        )
        db_path_lbl.setWordWrap(True)
        dl.addWidget(db_path_lbl)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        btn_clear = QPushButton("🗑   Clear Scan History")
        btn_clear.setObjectName("btn_secondary")
        btn_clear.setFixedHeight(36)
        btn_clear.clicked.connect(self._clear_scan_history)

        btn_open = QPushButton("📁   Open App Data Folder")
        btn_open.setObjectName("btn_secondary")
        btn_open.setFixedHeight(36)
        btn_open.clicked.connect(self._open_app_data_folder)

        btn_row.addWidget(btn_clear)
        btn_row.addWidget(btn_open)
        btn_row.addStretch()
        dl.addLayout(btn_row)
        self._layout.addWidget(db_card)

        # ── Custom Scan Paths card ────────────────────────────
        custom_card = self._card(p)
        cl = QVBoxLayout(custom_card)
        cl.setContentsMargins(22, 18, 22, 18)
        cl.setSpacing(12)
        cl.addWidget(self._hdr("📂", "CUSTOM SCAN PATHS", p))
        cl.addWidget(self._divider(p))

        hint = QLabel(
            "Add folders on any drive (D:\\, E:\\, etc.) to include in scans."
        )
        hint.setStyleSheet(f"color: {p['t2']}; font-size: 12px; border: none;")
        hint.setWordWrap(True)
        cl.addWidget(hint)

        # Existing paths list
        self._custom_paths_layout = QVBoxLayout()
        self._custom_paths_layout.setSpacing(6)
        cl.addLayout(self._custom_paths_layout)
        self._refresh_custom_paths(p)

        add_btn = QPushButton("📁   Add Folder...")
        add_btn.setObjectName("btn_secondary")
        add_btn.setFixedHeight(36)
        add_btn.clicked.connect(self._add_custom_path)
        cl.addWidget(add_btn)

        self._layout.addWidget(custom_card)

        # ── About card ────────────────────────────────────────
        about_card = self._card(p)
        abl = QVBoxLayout(about_card)
        abl.setContentsMargins(22, 18, 22, 18)
        abl.setSpacing(12)
        abl.addWidget(self._hdr("ℹ️", "ABOUT", p))
        abl.addWidget(self._divider(p))

        name_row = QHBoxLayout()
        app_name = QLabel("TraceZero ⚡")
        app_name.setStyleSheet(
            f"font-size: 17px; font-weight: 900; color: {p['accent2']}; border: none;"
        )
        name_row.addWidget(app_name)
        ver = QLabel(f"v{APP_VERSION}")
        ver.setStyleSheet(
            f"font-size: 11px; font-weight: 700; color: {p['accent']};"
            f" background: {p['accent']}18; border: 1px solid {p['accent']}44;"
            " border-radius: 10px; padding: 2px 10px;"
        )
        name_row.addWidget(ver)
        name_row.addStretch()
        abl.addLayout(name_row)

        for icon, text in [
            ("🔍", "Scans AppData, Program Files, Temp, and Registry"),
            ("🛡", "Never permanently deletes — always uses Recycle Bin"),
            ("⚠️", "Protects system files, drivers, and runtimes"),
            ("🧠", "AI-like risk classification for every detected item"),
        ]:
            r = QHBoxLayout()
            r.setSpacing(8)
            ic = QLabel(icon)
            ic.setFixedWidth(22)
            ic.setStyleSheet("border: none; font-size: 13px;")
            r.addWidget(ic)
            lb = QLabel(text)
            lb.setStyleSheet(f"color: {p['t2']}; font-size: 12px; border: none;")
            r.addWidget(lb, 1)
            abl.addLayout(r)

        self._layout.addWidget(about_card)
        self._layout.addStretch()

    def _clear_widgets(self):
        """Remove all items from the layout without destroying the layout itself."""
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Clear child layouts
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

    def apply_theme(self):
        """Rebuild content with updated theme colors."""
        self._clear_widgets()
        self._populate()

    def _toggle_context_menu(self, checked: bool):
        if checked:
            success = install_context_menu()
            if not success:
                QMessageBox.warning(self, "Error", "Failed to add context menu. You may need to run as Administrator.")
                self.chk_context_menu.blockSignals(True)
                self.chk_context_menu.setChecked(False)
                self.chk_context_menu.blockSignals(False)
        else:
            success = remove_context_menu()
            if not success:
                QMessageBox.warning(self, "Error", "Failed to remove context menu. You may need to run as Administrator.")
                self.chk_context_menu.blockSignals(True)
                self.chk_context_menu.setChecked(True)
                self.chk_context_menu.blockSignals(False)

    def _toggle_scheduled_scan(self, checked: bool):
        if checked:
            success = schedule_weekly_cleanup()
            if not success:
                QMessageBox.warning(self, "Error", "Failed to create Windows Scheduled Task. You may need to run as Administrator.")
                self.chk_scheduled_scan.blockSignals(True)
                self.chk_scheduled_scan.setChecked(False)
                self.chk_scheduled_scan.blockSignals(False)
        else:
            success = remove_scheduled_cleanup()
            if not success:
                QMessageBox.warning(self, "Error", "Failed to remove Windows Scheduled Task. You may need to run as Administrator.")
                self.chk_scheduled_scan.blockSignals(True)
                self.chk_scheduled_scan.setChecked(True)
                self.chk_scheduled_scan.blockSignals(False)

    def _change_language(self, index: int):
        code = self.lang_combo.itemData(index)
        cfg.set("language", code)
        QMessageBox.information(
            self, "Language Changed", 
            "Language preference saved successfully!\n\nPlease restart TraceZero to apply the new language."
        )

    # ── Custom Paths ───────────────────────────────────────────
    def _refresh_custom_paths(self, p=None):
        """Rebuild the custom paths chip list."""
        if p is None:
            p = ThemeManager.palette()
        # Clear existing
        while self._custom_paths_layout.count():
            item = self._custom_paths_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        paths = cfg.get_custom_paths()
        if not paths:
            empty = QLabel("No custom paths added yet.")
            empty.setStyleSheet(f"color: {p['t2']}; font-size: 12px; border: none; font-style: italic;")
            self._custom_paths_layout.addWidget(empty)
            return

        for path in paths:
            row = QFrame()
            row.setStyleSheet(f"""
                QFrame {{
                    background: {p['panel']};
                    border: 1px solid {p['border']};
                    border-radius: 8px;
                    padding: 2px;
                }}
            """)
            rl = QHBoxLayout(row)
            rl.setContentsMargins(10, 4, 6, 4)
            rl.setSpacing(8)

            path_lbl = QLabel(f"📂  {path}")
            path_lbl.setStyleSheet(f"color: {p['t1']}; font-size: 12px; border: none; font-family: 'Consolas', monospace;")
            path_lbl.setWordWrap(False)
            rl.addWidget(path_lbl, 1)

            rm_btn = QPushButton("✕")
            rm_btn.setFixedSize(24, 24)
            rm_btn.setToolTip(f"Remove {path}")
            rm_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; border: none;
                    color: {p['t2']}; font-size: 13px; font-weight: 700;
                    border-radius: 4px;
                }}
                QPushButton:hover {{ background: #f8717133; color: #f87171; }}
            """)
            rm_btn.clicked.connect(lambda _, x=path: self._remove_custom_path(x))
            rl.addWidget(rm_btn)

            self._custom_paths_layout.addWidget(row)

    def _add_custom_path(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Folder to Scan", "C:\\",
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontUseNativeDialog
        )
        if folder:
            cfg.add_custom_path(folder)
            self._refresh_custom_paths()

    def _remove_custom_path(self, path: str):
        cfg.remove_custom_path(path)
        self._refresh_custom_paths()

    # ── Actions ───────────────────────────────────────────────

    def _clear_scan_history(self):
        reply = QMessageBox.question(
            self, "Clear History",
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
        import subprocess
        try:
            subprocess.Popen(f'explorer "{APP_DATA_DIR}"')
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open folder:\n{e}")
