from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush, QFont

from tracezero.ui.styles import ThemeManager
from tracezero.registry.startup_manager import get_startup_apps, toggle_startup_app

class StartupPage(QWidget):
    """UI for managing Windows Startup Applications."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self.apps = []
        self._build_ui()

    def _build_ui(self):
        p = ThemeManager.palette()

        # Title
        title_frame = QFrame()
        title_frame.setFixedHeight(68)
        title_frame.setStyleSheet(f"background: {p['card']}; border-bottom: 1px solid {p['border']};")
        tl = QVBoxLayout(title_frame)
        tl.setContentsMargins(28, 12, 20, 12)
        
        title = QLabel("Startup Apps Manager")
        title.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {p['t1']}; border: none;")
        tl.addWidget(title)
        
        sub = QLabel("Enable or disable apps that run when Windows starts.")
        sub.setStyleSheet(f"font-size: 11px; color: {p['t2']}; border: none;")
        tl.addWidget(sub)
        
        self._layout.addWidget(title_frame)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["App Name", "Command", "Status"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background: {p['bg']};
                border: none;
                color: {p['t1']};
                font-size: 12px;
            }}
            QHeaderView::section {{
                background: {p['panel']};
                color: {p['t2']};
                font-weight: 600;
                border: none;
                border-bottom: 1px solid {p['border']};
                padding: 6px;
            }}
            QTableWidget::item {{
                border-bottom: 1px solid {p['border']};
                padding: 4px;
            }}
        """)
        self._layout.addWidget(self.table)

        # Action Bar
        act_bar = QFrame()
        act_bar.setFixedHeight(56)
        act_bar.setStyleSheet(f"background: {p['card']}; border-top: 1px solid {p['border']};")
        al = QHBoxLayout(act_bar)
        al.setContentsMargins(24, 0, 20, 0)
        
        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.setObjectName("btn_secondary")
        self.btn_refresh.setFixedHeight(34)
        self.btn_refresh.clicked.connect(self.load_data)
        al.addWidget(self.btn_refresh)
        
        al.addStretch()
        
        self.btn_toggle = QPushButton("Toggle Selected")
        self.btn_toggle.setObjectName("btn_primary")
        self.btn_toggle.setFixedHeight(34)
        self.btn_toggle.clicked.connect(self._toggle_selected)
        al.addWidget(self.btn_toggle)
        
        self._layout.addWidget(act_bar)

        self.load_data()

    def load_data(self):
        self.apps = get_startup_apps()
        self.table.setRowCount(0)
        p = ThemeManager.palette()
        
        for row, app in enumerate(self.apps):
            self.table.insertRow(row)
            self.table.setRowHeight(row, 38)
            
            name = QTableWidgetItem(app["name"])
            name.setForeground(QBrush(QColor(p['t1'])))
            self.table.setItem(row, 0, name)
            
            cmd = QTableWidgetItem(app["command"])
            cmd.setForeground(QBrush(QColor(p['t2'])))
            self.table.setItem(row, 1, cmd)
            
            status_text = "Enabled" if app["enabled"] else "Disabled"
            status = QTableWidgetItem(status_text)
            status.setForeground(QBrush(QColor("#3fb950" if app["enabled"] else p['t2'])))
            status.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            self.table.setItem(row, 2, status)

    def _toggle_selected(self):
        selected = self.table.selectedItems()
        if not selected:
            return
            
        row = selected[0].row()
        app = self.apps[row]
        new_state = not app["enabled"]
        
        success = toggle_startup_app(app, new_state)
        if success:
            self.load_data()

    def apply_theme(self):
        # Full clear and rebuild
        old_layout = self.layout()
        if old_layout:
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        self._build_ui()
