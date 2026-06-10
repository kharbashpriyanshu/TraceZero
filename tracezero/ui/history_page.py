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
    QFrame, QSizePolicy, QMessageBox, QTreeWidget, QTreeWidgetItem, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QColor, QBrush, QFont
import csv
from collections import defaultdict

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
        layout = self.layout()
        if layout is None:
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

        export_btn = QPushButton("💾  Export CSV")
        export_btn.setObjectName("btn_secondary")
        export_btn.setFixedHeight(36)
        export_btn.clicked.connect(self._export_csv)
        header.addWidget(export_btn)

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

        self.del_tree = QTreeWidget()
        self.del_tree.setColumnCount(6)
        self.del_tree.setHeaderLabels([
            "Item / Path", "Type", "Category", "Size", "Risk", "Deleted At"
        ])
        
        self.del_tree.setSelectionBehavior(QTreeWidget.SelectionBehavior.SelectRows)
        self.del_tree.setAlternatingRowColors(False)
        self.del_tree.setStyleSheet(f"""
            QTreeWidget {{
                background: {ThemeManager.palette()['card']}; border: 1px solid {ThemeManager.palette()['border']};
                border-radius: 12px; outline: none; font-size: 13px; color: {ThemeManager.palette()['t1']};
            }}
            QTreeWidget::item {{ padding: 5px 8px; border-bottom: 1px solid {ThemeManager.palette()['border']}; }}
            QTreeWidget::item:selected {{ background: {ThemeManager.palette()['accent']}22; }}
            QHeaderView::section {{
                background: {ThemeManager.palette()['bg']}; color: {ThemeManager.palette()['t2']};
                padding: 9px 12px; border: none; border-bottom: 1px solid {ThemeManager.palette()['border']};
                font-weight: 700; font-size: 11px;
            }}
        """)
        
        hdr2 = self.del_tree.header()
        hdr2.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hdr2.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        hdr2.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hdr2.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        hdr2.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        hdr2.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        del_layout.addWidget(self.del_tree)
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
        history = self.db.get_deletion_history(limit=500)
        self.del_tree.clear()
        p = ThemeManager.palette()

        RISK_COLORS = {
            "Safe": p['green'],
            "Review": p['orange'],
            "Risky": p['red'],
        }

        # Group by session_id
        grouped = defaultdict(list)
        for record in history:
            sid = record.get("session_id") or "Unknown"
            grouped[sid].append(record)

        for sid, records in grouped.items():
            if not records: continue
            
            total_size = sum(r.get("size_bytes", 0) for r in records)
            date_str = records[0]["deleted_at"]
            
            # Root folder item for the session
            root = QTreeWidgetItem(self.del_tree)
            root.setText(0, f"📁 Scan Session: {date_str} (ID: {sid}) — {len(records)} items")
            root.setText(3, format_size(total_size))
            root.setForeground(0, QBrush(QColor(p['accent2'])))
            root.setFont(0, QFont("Segoe UI", 11, QFont.Weight.Bold))
            
            # Add children
            for record in records:
                child = QTreeWidgetItem(root)
                child.setText(0, record["path"])
                child.setToolTip(0, record["path"])
                child.setText(1, record["item_type"])
                child.setText(2, record.get("category", ""))
                
                child.setText(3, format_size(int(record.get("size_bytes", 0))))
                child.setForeground(3, QBrush(QColor(p['t2'])))
                
                risk = record.get("risk_level", "")
                child.setText(4, risk)
                child.setForeground(4, QBrush(QColor(RISK_COLORS.get(risk, p['t2']))))
                
                child.setText(5, record["deleted_at"])

        # Expand the most recent session automatically if any
        if self.del_tree.topLevelItemCount() > 0:
            self.del_tree.topLevelItem(0).setExpanded(True)

    def _export_csv(self):
        history = self.db.get_deletion_history(limit=5000)
        if not history:
            QMessageBox.information(self, "Export", "No deletion history available to export.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export History", "", "CSV Files (*.csv);;All Files (*)"
        )
        if not file_path:
            return

        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Session ID", "Deleted At", "Path", "Item Type", "Category", "Size Bytes", "Risk Level", "App Name"])
                for r in history:
                    writer.writerow([
                        r.get("session_id", ""),
                        r.get("deleted_at", ""),
                        r.get("path", ""),
                        r.get("item_type", ""),
                        r.get("category", ""),
                        r.get("size_bytes", 0),
                        r.get("risk_level", ""),
                        r.get("app_name", ""),
                    ])
            QMessageBox.information(self, "Export Successful", f"History exported successfully to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export CSV:\n{e}")

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
