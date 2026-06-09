"""
ui/main_window.py — TraceZero

Main application window. Completely redesigned with:
- Gradient sidebar with glowing active states
- Custom title bar accent
- Smooth page transitions
- Improved deletion flow
"""

import sys
from typing import List, Dict

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget,
    QStatusBar, QMessageBox, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer, QSize, QUrl, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette, QLinearGradient, QPixmap, QPainter, QDesktopServices, QIcon

from tracezero.ui.dashboard_page import DashboardPage
from tracezero.ui.scan_page import ScanPage
from tracezero.ui.history_page import HistoryPage
from tracezero.ui.settings_page import SettingsPage
from tracezero.ui.startup_page import StartupPage
from tracezero.ui.duplicate_page import DuplicatePage
from tracezero.ui.styles import MAIN_STYLESHEET, ThemeManager
from tracezero.scanner.scan_engine import ScanEngine
from tracezero.utils.recycle_bin import RecycleBinManager
from tracezero.utils.helpers import format_size
from tracezero.utils.logger import app_logger
from tracezero.utils.constants import APP_NAME, APP_VERSION, APP_TAGLINE, COLOR_ACCENT

# ─────────────────────────────────────────────────────────────
#  NAV BUTTON
# ─────────────────────────────────────────────────────────────
class NavButton(QPushButton):
    """Sidebar navigation button with smooth active styling."""

    def __init__(self, icon: str, label: str, parent=None):
        super().__init__(parent)
        self._icon  = icon
        self._label = label
        self._active = False
        self.setText(f"  {icon}  {label}")
        self.setObjectName("sidebar_btn")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(42)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_active(self, active: bool):
        self._active = active
        self.setObjectName("sidebar_btn_active" if active else "sidebar_btn")
        self.style().unpolish(self)
        self.style().polish(self)

# ─────────────────────────────────────────────────────────────
#  DELETION THREAD
# ─────────────────────────────────────────────────────────────
class DeletionThread(QThread):
    progress = pyqtSignal(str)
    item_deleted = pyqtSignal(dict, bool)
    finished_deleting = pyqtSignal(list, list)

    def __init__(self, recycle_manager, items):
        super().__init__()
        self.recycle_manager = recycle_manager
        self.items = items

    def run(self):
        successful = []
        failed = []
        for i, item in enumerate(self.items):
            self.progress.emit(f"Sending to Recycle Bin... ({i+1}/{len(self.items)})")
            # delete_items returns (successful_paths, failed_paths_with_reasons)
            succ, fld = self.recycle_manager.delete_items([item])
            if succ:
                successful.extend(succ)
                self.item_deleted.emit(item, True)
            if fld:
                failed.extend(fld)
                self.item_deleted.emit(item, False)
        self.finished_deleting.emit(successful, failed)

# ─────────────────────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    """TraceZero main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"TraceZero  v{APP_VERSION}")
        import os
        from tracezero.utils.constants import APP_DATA_DIR
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logo.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setMinimumSize(1120, 700)
        self.resize(1360, 820)

        self.scan_engine     = ScanEngine()
        self.recycle_manager = RecycleBinManager()

        self.setStyleSheet(ThemeManager.stylesheet())
        self._build_ui()
        self._connect_signals()
        self._navigate(0)

        app_logger.info("TraceZero started.")

    # ── Layout ───────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())

        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)

        self.dashboard_page = DashboardPage(self)
        self.scan_page      = ScanPage(self.scan_engine, self)
        self.history_page   = HistoryPage(self)
        self.startup_page   = StartupPage(self)
        self.duplicate_page = DuplicatePage(self)
        self.settings_page  = SettingsPage(self)

        for page in [self.dashboard_page, self.scan_page,
                     self.history_page, self.startup_page, 
                     self.duplicate_page, self.settings_page]:
            self.stack.addWidget(page)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._set_status(f"TraceZero v{APP_VERSION}  —  Ready")

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(224)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Logo block ────────────────────────────────────────
        logo_w = QWidget()
        logo_w.setStyleSheet("background: transparent;")
        ll = QVBoxLayout(logo_w)
        ll.setContentsMargins(18, 22, 18, 12)
        ll.setSpacing(0)

        # App logo image row
        import os
        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'logo.png'))
        
        logo_lbl = QLabel()
        logo_lbl.setStyleSheet("background: transparent; border: none;")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Scale gracefully keeping aspect ratio so it fits perfectly in the sidebar header
            scaled = pixmap.scaled(180, 75, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_lbl.setPixmap(scaled)
        else:
            logo_lbl.setText("⚡ TraceZero")
            logo_lbl.setStyleSheet(f"font-size: 24px; font-weight: 900; color: {ThemeManager.palette()['t1']}; border: none;")

        ll.addWidget(logo_lbl)

        tagline = QLabel("Smart application trace cleaner")
        p = ThemeManager.palette()
        tagline.setStyleSheet(
            f"font-size: 10px; color: {p['t2']}; background: transparent; margin-top: 4px; border: none;"
        )
        tagline.setWordWrap(True)
        ll.addWidget(tagline)

        # Powered by Mart1al credit — links to TraceZero GitHub project
        credit = QLabel(
            '<i style="font-size:9px; color:#8876a8;">Powered by '
            '<a href="https://github.com/kharbashpriyanshu/TraceZero" '
            'style="color:#7c6fa8; text-decoration:none;">Mart1al</a></i>'
        )
        credit.setStyleSheet("background: transparent; border: none; margin-top: 2px;")
        credit.setTextFormat(Qt.TextFormat.RichText)
        credit.setOpenExternalLinks(True)
        ll.addWidget(credit)

        # Version pill
        ver_row = QHBoxLayout()
        ver_row.setSpacing(0)
        ver = QLabel(f"v{APP_VERSION}")
        ver.setStyleSheet(
            f"font-size: 10px; font-weight: 700; color: {p['accent']}; "
            f"background: {p['accent']}18; border: 1px solid {p['accent']}33; "
            "border-radius: 10px; padding: 2px 8px; margin-top: 6px;"
        )
        ver_row.addWidget(ver)
        ver_row.addStretch()
        ll.addLayout(ver_row)

        layout.addWidget(logo_w)

        # ── Divider ───────────────────────────────────────────
        layout.addWidget(self._divider())
        layout.addSpacing(6)

        # ── Nav items ─────────────────────────────────────────
        self.nav_btns: List[NavButton] = []
        items = [
            ("🏠", "Dashboard",   0),
            ("🔍", "Scan && Clean",1),
            ("📋", "History",     2),
            ("🚀", "Startup Apps",3),
            ("👯", "Duplicates",  4),
            ("⚙️", "Settings",    5),
        ]
        for icon, label, idx in items:
            btn = NavButton(icon, label)
            btn.clicked.connect(lambda _, i=idx: self._navigate(i))
            self.nav_btns.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        # ── Theme toggle button ───────────────────────────────
        self.theme_btn = QPushButton(f"{ThemeManager.icon()}  {ThemeManager.label()}")
        self.theme_btn.setObjectName("btn_theme")
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.setFixedHeight(34)
        self.theme_btn.clicked.connect(self._toggle_theme)
        layout.addWidget(self.theme_btn)

        # ── Divider + safe badge ──────────────────────────────

        safe_row = QWidget()
        safe_row.setStyleSheet("background: transparent;")
        sr = QHBoxLayout(safe_row)
        sr.setContentsMargins(14, 8, 14, 12)
        sr.setSpacing(6)

        dot = QLabel("●")
        dot.setStyleSheet(
            "color: #3fb950; font-size: 9px; background: transparent;"
        )
        sr.addWidget(dot)

        badge = QLabel("Safe by Design")
        badge.setStyleSheet(
            "font-size: 11px; color: #3fb950; font-weight: 700; "
            "background: transparent; letter-spacing: 0.2px;"
        )
        sr.addWidget(badge)
        sr.addStretch()

        layout.addWidget(safe_row)

        return sidebar

    def _divider(self) -> QFrame:
        d = QFrame()
        d.setFrameShape(QFrame.Shape.HLine)
        d.setStyleSheet(f"background: {ThemeManager.palette()['border']}; border: none; max-height: 1px;")
        return d

    def _toggle_theme(self):
        ThemeManager.toggle()
        self.setStyleSheet(ThemeManager.stylesheet())
        self.theme_btn.setText(f"{ThemeManager.icon()}  {ThemeManager.label()}")
        # Refresh dividers
        p = ThemeManager.palette()
        for d in self.findChildren(QFrame):
            if d.frameShape() == QFrame.Shape.HLine:
                d.setStyleSheet(f"background:{p['border']}; border:none; max-height:1px;")
        # Refresh dashboard hero + scan button
        if hasattr(self.dashboard_page, 'apply_theme'):
            self.dashboard_page.apply_theme()
        if hasattr(self.settings_page, 'apply_theme'):
            self.settings_page.apply_theme()
        if hasattr(self.startup_page, 'apply_theme'):
            self.startup_page.apply_theme()
        if hasattr(self.duplicate_page, 'apply_theme'):
            self.duplicate_page.apply_theme()
        if hasattr(self.scan_page, 'apply_theme'):
            self.scan_page.apply_theme()
        if hasattr(self.history_page, 'apply_theme'):
            self.history_page.apply_theme()
        app_logger.info(f"Theme switched to: {ThemeManager.mode()}")

    # ── Signals ───────────────────────────────────────────────
    def _connect_signals(self):
        self.dashboard_page.scan_requested.connect(self._start_scan_from_dashboard)
        self.scan_page.delete_requested.connect(self._handle_deletion)

    def _navigate(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_btns):
            btn.set_active(i == index)
        if index == 2:
            self.history_page.refresh()

    @pyqtSlot()
    def _start_scan_from_dashboard(self):
        self._navigate(1)
        self.scan_page.start_scan()

    @pyqtSlot(list)
    def _handle_deletion(self, items: List[Dict]):
        if not items:
            return
            
        self.scan_page.btn_delete.setEnabled(False)
        self._set_status(f"Sending {len(items)} items to Recycle Bin…")
        
        self.recycle_manager.session_id = self.scan_engine._session_id
        
        self.deletion_thread = DeletionThread(self.recycle_manager, items)
        self.deletion_thread.progress.connect(self._set_status)
        self.deletion_thread.item_deleted.connect(self._on_item_deleted)
        self.deletion_thread.finished_deleting.connect(self._on_deletion_finished)
        self.deletion_thread.start()

    @pyqtSlot(dict, bool)
    def _on_item_deleted(self, item: Dict, success: bool):
        if success:
            self.scan_page.remove_deleted_item(item)

    @pyqtSlot(list, list)
    def _on_deletion_finished(self, successful: list, failed: list):
        msg = f"✅  Cleaned {len(successful)} item(s)"
        if failed:
            msg += f"   ⚠️  {len(failed)} failed"
        self._set_status(msg)

        if successful or failed:
            from tracezero.utils.helpers import truncate_path
            formatted_failed = "\n".join(truncate_path(f, 90) for f in failed[:6])
            
            QMessageBox.information(
                self, "Cleanup Complete",
                f"Sent {len(successful)} item(s) to the Recycle Bin.\n\n"
                "You can restore them from the Windows Recycle Bin anytime.\n\n"
                + (f"⚠️ {len(failed)} item(s) could not be removed:\n{formatted_failed}" if failed else ""),
            )
        
        self.scan_page.btn_delete.setEnabled(True)

    def _set_status(self, msg: str):
        self.status_bar.showMessage(msg)

    def closeEvent(self, event):
        if self.scan_engine.is_running():
            self.scan_engine.stop()
        event.accept()
