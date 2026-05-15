from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QMenu, QMessageBox, QComboBox
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
        
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        self.table.doubleClicked.connect(self._toggle_selected)

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
            
            combo = QComboBox()
            combo.addItems(["Enabled", "Disabled"])
            combo.setCurrentIndex(0 if app["enabled"] else 1)
            combo.currentIndexChanged.connect(lambda idx, r=row, c=combo: self._on_status_combo_changed(r, c))
            combo.setStyleSheet(f"""
                QComboBox {{
                    background: {p['accent']}15;
                    color: {p['green'] if app["enabled"] else p['t2']};
                    font-weight: 800;
                    border: 1px solid {p['accent']}30;
                    border-radius: 12px;
                    padding: 4px 12px;
                    min-width: 85px;
                }}
                QComboBox:hover {{
                    background: {p['accent']}25;
                    border: 1px solid {p['accent']}50;
                }}
                QComboBox::drop-down {{
                    border: none; 
                    width: 20px;
                }}
                QComboBox::down-arrow {{
                    image: none; 
                    /* Custom arrow simulation */
                }}
                QComboBox QAbstractItemView {{
                    background: {p['card']};
                    color: {p['t1']};
                    border: 1px solid {p['border']};
                    border-radius: 8px;
                    selection-background-color: {p['accent']}40;
                    outline: none;
                    padding: 4px;
                }}
                QComboBox QAbstractItemView::item {{
                    padding: 8px 12px;
                    border-radius: 4px;
                }}
            """)
            self.table.setCellWidget(row, 2, combo)

    def _on_status_combo_changed(self, row, combo):
        app = self.apps[row]
        new_state = (combo.currentIndex() == 0)
        
        if new_state == app["enabled"]:
            return
            
        success = toggle_startup_app(app, new_state)
        p = ThemeManager.palette()
        
        if success:
            app["enabled"] = new_state
            combo.setStyleSheet(f"""
                QComboBox {{
                    background: {p['accent']}15;
                    color: {p['green'] if new_state else p['t2']};
                    font-weight: 800;
                    border: 1px solid {p['accent']}30;
                    border-radius: 12px;
                    padding: 4px 12px;
                    min-width: 85px;
                }}
                QComboBox:hover {{
                    background: {p['accent']}25;
                    border: 1px solid {p['accent']}50;
                }}
                QComboBox::drop-down {{
                    border: none; 
                    width: 20px;
                }}
                QComboBox::down-arrow {{
                    image: none; 
                }}
                QComboBox QAbstractItemView {{
                    background: {p['card']};
                    color: {p['t1']};
                    border: 1px solid {p['border']};
                    border-radius: 8px;
                    selection-background-color: {p['accent']}40;
                    outline: none;
                    padding: 4px;
                }}
                QComboBox QAbstractItemView::item {{
                    padding: 8px 12px;
                    border-radius: 4px;
                }}
            """)
            action_text = "enabled" if new_state else "disabled"
            QMessageBox.information(
                self,
                "Success",
                f"Successfully {action_text} startup app:\n{app['name']}"
            )
        else:
            combo.blockSignals(True)
            combo.setCurrentIndex(0 if app["enabled"] else 1)
            combo.blockSignals(False)
            
            QMessageBox.critical(
                self, 
                "Permission Denied",
                f"Failed to {'enable' if new_state else 'disable'} {app['name']}.\n\n"
                "Please run TraceZero as Administrator to manage system-wide startup applications."
            )

    def _show_context_menu(self, pos):
        item = self.table.itemAt(pos)
        if not item:
            return
            
        row = item.row()
        app = self.apps[row]
        menu = QMenu(self)
        
        action_text = "Disable" if app["enabled"] else "Enable"
        toggle_action = menu.addAction(f"{action_text} Startup App")
        
        action = menu.exec(self.table.viewport().mapToGlobal(pos))
        if action == toggle_action:
            self._toggle_selected()

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
            action_text = "enabled" if new_state else "disabled"
            QMessageBox.information(
                self,
                "Success",
                f"Successfully {action_text} startup app:\n{app['name']}"
            )
        else:
            QMessageBox.critical(
                self, 
                "Permission Denied",
                f"Failed to {'enable' if new_state else 'disable'} {app['name']}.\n\n"
                "Please run TraceZero as Administrator to manage system-wide startup applications."
            )

    def apply_theme(self):
        # Full clear and rebuild
        old_layout = self.layout()
        if old_layout:
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        self._build_ui()
