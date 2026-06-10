"""
ui/uninstaller_page.py — TraceZero

Smart Uninstaller Module: lists installed applications and allows uninstalling
them, then prompts for leftover cleanup.
"""

import subprocess
import shlex
from typing import List, Dict

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QColor, QBrush, QFont

from tracezero.ui.styles import ThemeManager
from tracezero.registry.registry_reader import RegistryReader


class UninstallThread(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, cmd: str):
        super().__init__()
        self.cmd = cmd

    def run(self):
        try:
            # We use shell=True to handle complex arguments safely on Windows
            process = subprocess.run(self.cmd, shell=True, capture_output=True, text=True)
            if process.returncode == 0 or process.returncode == 1602: # 1602 is user cancelled MSI
                self.finished.emit(True, "Uninstaller finished.")
            else:
                self.finished.emit(False, f"Uninstaller exited with code {process.returncode}")
        except Exception as e:
            self.finished.emit(False, str(e))


class LoadAppsThread(QThread):
    finished = pyqtSignal(list)

    def run(self):
        reader = RegistryReader()
        apps = reader.get_installed_apps()
        # Sort apps alphabetically by name
        apps.sort(key=lambda x: x.get("name", "").lower())
        self.finished.emit(apps)


class UninstallerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.apps: List[Dict] = []
        self._build_ui()
        self.load_apps()

    def _build_ui(self):
        layout = self.layout()
        if layout is None:
            layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        p = ThemeManager.palette()

        # Title frame
        title_frame = QFrame()
        title_frame.setFixedHeight(68)
        title_frame.setStyleSheet(f"background: {p['card']}; border-bottom: 1px solid {p['border']};")
        tl = QVBoxLayout(title_frame)
        tl.setContentsMargins(28, 12, 20, 12)
        
        title = QLabel("Smart Uninstaller")
        title.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {p['t1']}; border: none;")
        tl.addWidget(title)
        
        sub = QLabel("Uninstall applications and immediately scan for leftover traces.")
        sub.setStyleSheet(f"font-size: 11px; color: {p['t2']}; border: none;")
        tl.addWidget(sub)
        
        layout.addWidget(title_frame)

        # Body Layout
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(24, 20, 24, 20)
        body_layout.setSpacing(16)

        # Controls
        ctrl_layout = QHBoxLayout()
        self.status_lbl = QLabel("Loading installed applications...")
        self.status_lbl.setStyleSheet(f"color: {p['t1']}; font-weight: 600;")
        ctrl_layout.addWidget(self.status_lbl)
        
        ctrl_layout.addStretch()

        self.btn_refresh = QPushButton("🔄 Refresh List")
        self.btn_refresh.setObjectName("btn_secondary")
        self.btn_refresh.setFixedSize(140, 36)
        self.btn_refresh.clicked.connect(self.load_apps)
        ctrl_layout.addWidget(self.btn_refresh)
        
        body_layout.addLayout(ctrl_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Application Name", "Publisher", "Version", "Install Date", "Action"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 130)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        
        self._apply_table_style()
        body_layout.addWidget(self.table)

        layout.addWidget(body)

    def _apply_table_style(self):
        p = ThemeManager.palette()
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background: {p['bg']};
                border: 1px solid {p['border']};
                border-radius: 8px;
                color: {p['t1']};
                font-size: 13px;
                gridline-color: {p['border']};
            }}
            QHeaderView::section {{
                background: {p['panel']};
                color: {p['t2']};
                font-weight: 600;
                border: none;
                border-bottom: 1px solid {p['border']};
                padding: 8px;
            }}
            QTableWidget::item {{
                padding: 4px 8px;
                border-bottom: 1px solid {p['border']}55;
            }}
            QTableWidget::item:selected {{
                background: {p['accent']}33;
            }}
        """)

    def load_apps(self):
        self.btn_refresh.setEnabled(False)
        self.table.setRowCount(0)
        self.status_lbl.setText("Loading installed applications...")
        
        self.load_thread = LoadAppsThread()
        self.load_thread.finished.connect(self._on_apps_loaded)
        self.load_thread.start()

    @pyqtSlot(list)
    def _on_apps_loaded(self, apps: list):
        self.apps = apps
        self.btn_refresh.setEnabled(True)
        self.status_lbl.setText(f"Found {len(apps)} installed applications.")
        
        self.table.setRowCount(len(apps))
        p = ThemeManager.palette()

        for row, app in enumerate(apps):
            self.table.setRowHeight(row, 46)
            
            name_item = QTableWidgetItem(app.get("name", ""))
            name_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            self.table.setItem(row, 0, name_item)
            
            self.table.setItem(row, 1, QTableWidgetItem(app.get("publisher", "")))
            
            ver_item = QTableWidgetItem(app.get("version", ""))
            ver_item.setForeground(QBrush(QColor(p['t2'])))
            self.table.setItem(row, 2, ver_item)
            
            # Format raw YYYYMMDD string to YYYY-MM-DD
            raw_date = app.get("install_date", "")
            if raw_date and len(raw_date) == 8 and raw_date.isdigit():
                formatted_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
            else:
                formatted_date = raw_date
                
            date_item = QTableWidgetItem(formatted_date)
            date_item.setForeground(QBrush(QColor(p['t2'])))
            self.table.setItem(row, 3, date_item)
            
            # Action Button
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 4, 4, 4)
            btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            uninstall_btn = QPushButton("Uninstall")
            uninstall_btn.setFixedSize(100, 30)
            
            cmd = app.get("uninstall_string", "")
            if not cmd:
                uninstall_btn.setEnabled(False)
                uninstall_btn.setText("No Uninstaller")
            else:
                uninstall_btn.setObjectName("btn_primary")
                uninstall_btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {p['red']}; color: white; border-radius: 6px; font-weight: bold;
                    }}
                    QPushButton:hover {{ background: #ef4444; }}
                """)
                uninstall_btn.clicked.connect(lambda _, a=app: self.start_uninstall(a))
            
            btn_layout.addWidget(uninstall_btn)
            self.table.setCellWidget(row, 4, btn_widget)

    def start_uninstall(self, app: Dict):
        cmd = app.get("uninstall_string", "")
        if not cmd:
            return
            
        reply = QMessageBox.question(
            self, 'Confirm Uninstall',
            f"Are you sure you want to uninstall {app.get('name', 'this app')}?\n\nThe official uninstaller will launch.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.status_lbl.setText(f"Waiting for uninstaller: {app.get('name')} ...")
            self.table.setEnabled(False)
            
            self.app_being_uninstalled = app
            self.uninstall_thread = UninstallThread(cmd)
            self.uninstall_thread.finished.connect(self._on_uninstall_finished)
            self.uninstall_thread.start()

    @pyqtSlot(bool, str)
    def _on_uninstall_finished(self, success: bool, message: str):
        self.table.setEnabled(True)
        app_name = self.app_being_uninstalled.get('name', 'The app')
        
        if success:
            QMessageBox.information(
                self, "Uninstaller Finished",
                f"{app_name} uninstaller has closed.\n\n"
                "TraceZero highly recommends running a 'Start Scan' from the Dashboard "
                "to find any orphaned registry keys or files left behind by the uninstaller."
            )
            self.load_apps()
        else:
            QMessageBox.warning(
                self, "Uninstall Error",
                f"The uninstaller for {app_name} encountered an error or was blocked.\n\n"
                f"Details: {message}"
            )
            self.status_lbl.setText(f"Found {len(self.apps)} installed applications.")

    def apply_theme(self):
        root = self.layout()
        if root:
            self._clear_layout(root)
        self._build_ui()
        self.load_apps()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
                item.layout().deleteLater()
