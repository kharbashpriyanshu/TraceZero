"""
ui/history_page.py

Scan history and deletion history page.
Displays:
- Table of past scan sessions
- Table of deleted items with restore info
- Database statistics
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QFrame, QSizePolicy, QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QColor, QBrush, QFont

from tracezero.database.db_manager import get_db
from tracezero.utils.helpers import format_size
from tracezero.ui.styles import ThemeManager


class HistoryPage(QWidget):
    """Scan and deletion history viewer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 24, 30, 20)
        layout.setSpacing(16)

        # ── Header ───────────────────────────────────────────────
        header = QHBoxLayout()

        p = ThemeManager.palette()
        title_col = QVBoxLayout()
        title = QLabel("History")
        title.setStyleSheet(f"font-size: 24px; font-weight: 800; color: {p['t1']}; background: transparent;")
        title_col.addWidget(title)
        subtitle = QLabel("View past scan sessions and deletion history")
        subtitle.setStyleSheet(f"font-size: 12px; color: {p['t2']}; background: transparent;")
        title_col.addWidget(subtitle)

        header.addLayout(title_col)
        header.addStretch()

        refresh_btn = QPushButton("🔄  Refresh")
        refresh_btn.setObjectName("btn_secondary")
        refresh_btn.setFixedHeight(36)
        refresh_btn.clicked.connect(self.refresh)
        header.addWidget(refresh_btn)

        layout.addLayout(header)

        # ── Tabs ─────────────────────────────────────────────────
        self.tabs = QTabWidget()

        # ── Tab 1: Scan History ───────────────────────────────────
        scan_tab = QWidget()
        scan_layout = QVBoxLayout(scan_tab)
        scan_layout.setContentsMargins(0, 12, 0, 0)
        scan_layout.setSpacing(8)

        self.scan_table = QTableWidget()
        self.scan_table.setColumnCount(6)
        self.scan_table.setHorizontalHeaderLabels([
            "ID", "Started At", "Finished At", "Items Found", "Total Size", "Status"
        ])
        self._configure_table(self.scan_table)
        hdr = self.scan_table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.scan_table.setColumnWidth(0, 50)

        scan_layout.addWidget(self.scan_table)
        self.tabs.addTab(scan_tab, "📊  Scan Sessions")

        # ── Tab 2: Deletion History ───────────────────────────────
        del_tab = QWidget()
        del_layout = QVBoxLayout(del_tab)
        del_layout.setContentsMargins(0, 12, 0, 0)

        self.del_table = QTableWidget()
        self.del_table.setColumnCount(6)
        self.del_table.setHorizontalHeaderLabels([
            "Path", "Type", "Category", "Size", "Risk", "Deleted At"
        ])
        self._configure_table(self.del_table)
        hdr2 = self.del_table.horizontalHeader()
        hdr2.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hdr2.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        hdr2.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hdr2.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        hdr2.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        hdr2.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        del_layout.addWidget(self.del_table)
        self.tabs.addTab(del_tab, "🗑  Deletion History")

        layout.addWidget(self.tabs, 1)

        # ── Stats Footer ──────────────────────────────────────────
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet(f"font-size: 12px; color: {p['t2']}; background: transparent;")
        layout.addWidget(self.stats_label)

    def _configure_table(self, table: QTableWidget):
        """Apply common table settings."""
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(False)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)

    def refresh(self):
        """Reload all data from the database."""
        self._load_scan_history()
        self._load_deletion_history()
        self._load_stats()

    def _load_scan_history(self):
        history = self.db.get_scan_history(limit=100)
        self.scan_table.setRowCount(0)
        p = ThemeManager.palette()

        STATUS_COLORS = {
            "completed": p['green'],
            "cancelled": p['orange'],
            "running": p['accent'],
        }

        for record in history:
            row = self.scan_table.rowCount()
            self.scan_table.insertRow(row)
            self.scan_table.setRowHeight(row, 36)

            self.scan_table.setItem(row, 0, QTableWidgetItem(str(record["id"])))
            self.scan_table.setItem(row, 1, QTableWidgetItem(record["started_at"]))
            self.scan_table.setItem(row, 2, QTableWidgetItem(record["finished_at"]))

            items_item = QTableWidgetItem(str(record["total_items"]))
            items_item.setForeground(QBrush(QColor(p['t1'])))
            self.scan_table.setItem(row, 3, items_item)

            size_item = QTableWidgetItem(format_size(int(record["total_size"])))
            size_item.setForeground(QBrush(QColor(p['t2'])))
            self.scan_table.setItem(row, 4, size_item)

            status = record["status"]
            status_item = QTableWidgetItem(status.title())
            color = STATUS_COLORS.get(status, p['t2'])
            status_item.setForeground(QBrush(QColor(color)))
            status_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            self.scan_table.setItem(row, 5, status_item)

    def _load_deletion_history(self):
        history = self.db.get_deletion_history(limit=200)
        self.del_table.setRowCount(0)
        p = ThemeManager.palette()

        RISK_COLORS = {
            "Safe": p['green'],
            "Review": p['orange'],
            "Risky": p['red'],
        }

        for record in history:
            row = self.del_table.rowCount()
            self.del_table.insertRow(row)
            self.del_table.setRowHeight(row, 36)

            path_item = QTableWidgetItem(record["path"])
            path_item.setToolTip(record["path"])
            self.del_table.setItem(row, 0, path_item)
            self.del_table.setItem(row, 1, QTableWidgetItem(record["item_type"]))
            self.del_table.setItem(row, 2, QTableWidgetItem(record.get("category", "")))

            size_item = QTableWidgetItem(format_size(int(record.get("size_bytes", 0))))
            size_item.setForeground(QBrush(QColor(p['t2'])))
            self.del_table.setItem(row, 3, size_item)

            risk = record.get("risk_level", "")
            risk_item = QTableWidgetItem(risk)
            risk_item.setForeground(QBrush(QColor(RISK_COLORS.get(risk, p['t2']))))
            self.del_table.setItem(row, 4, risk_item)

            self.del_table.setItem(row, 5, QTableWidgetItem(record["deleted_at"]))

    def _load_stats(self):
        stats = self.db.get_stats()
        self.stats_label.setText(
            f"Total scans: {stats['total_scans']}  •  "
            f"Total cleaned items: {stats['total_deleted_items']}  •  "
            f"Total space freed: {format_size(int(stats['total_space_freed']))}"
        )

    def apply_theme(self):
        """Rebuild the page completely to apply new theme colors."""
        root = self.layout()
        if root:
            self._clear_layout(root)
        self._build_ui()
        self.refresh()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
                item.layout().deleteLater()
