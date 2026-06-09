"""
ui/duplicate_page.py — TraceZero

Page for scanning and managing duplicate files.
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTreeWidget, QTreeWidgetItem, QHeaderView,
    QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QBrush, QFont

from tracezero.ui.styles import ThemeManager
from tracezero.scanner.duplicate_scanner import DuplicateScanner
from tracezero.utils.helpers import format_size
from tracezero.utils.recycle_bin import RecycleBinManager

class DuplicateScanThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(list)
    
    def __init__(self, targets):
        super().__init__()
        self.targets = targets
        self.scanner = DuplicateScanner()
        
    def run(self):
        self.progress.emit("Scanning for duplicates (this may take a while)...")
        results = self.scanner.scan(self.targets)
        self.finished.emit(results)


class DuplicatePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        
        self.duplicate_groups = []
        self.recycle_manager = RecycleBinManager()
        self._build_ui()
        
    def _build_ui(self):
        p = ThemeManager.palette()

        # Title
        title_frame = QFrame()
        title_frame.setFixedHeight(68)
        title_frame.setStyleSheet(f"background: {p['card']}; border-bottom: 1px solid {p['border']};")
        tl = QVBoxLayout(title_frame)
        tl.setContentsMargins(28, 12, 20, 12)
        
        title = QLabel("Duplicate File Finder")
        title.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {p['t1']}; border: none;")
        tl.addWidget(title)
        
        sub = QLabel("Find and safely remove identical files taking up disk space.")
        sub.setStyleSheet(f"font-size: 11px; color: {p['t2']}; border: none;")
        tl.addWidget(sub)
        
        self._layout.addWidget(title_frame)

        # Body Layout
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(24, 20, 24, 20)
        body_layout.setSpacing(16)
        
        # Scan controls
        ctrl_layout = QHBoxLayout()
        
        self.status_lbl = QLabel("Ready to scan.")
        self.status_lbl.setStyleSheet(f"color: {p['t1']}; font-weight: 600;")
        ctrl_layout.addWidget(self.status_lbl)
        
        ctrl_layout.addStretch()
        
        self.btn_scan = QPushButton("🔍 Scan Common Folders")
        self.btn_scan.setObjectName("btn_secondary")
        self.btn_scan.setFixedSize(180, 36)
        self.btn_scan.clicked.connect(self.start_scan)
        ctrl_layout.addWidget(self.btn_scan)
        
        body_layout.addLayout(ctrl_layout)
        
        # Tree Widget for results
        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["File Name / Path", "Size", "Keep?"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.NoSelection)
        self._apply_tree_style()
        body_layout.addWidget(self.tree)
        
        # Action Bar
        act_layout = QHBoxLayout()
        
        self.btn_smart_select = QPushButton("Smart Select (Keep Newest)")
        self.btn_smart_select.setObjectName("btn_secondary")
        self.btn_smart_select.setFixedHeight(34)
        self.btn_smart_select.clicked.connect(self.smart_select)
        self.btn_smart_select.setEnabled(False)
        act_layout.addWidget(self.btn_smart_select)
        
        act_layout.addStretch()
        
        self.btn_delete = QPushButton("🗑️ Delete Unselected")
        self.btn_delete.setObjectName("btn_primary")
        self.btn_delete.setFixedHeight(34)
        self.btn_delete.setStyleSheet(f"background: {p['red']}; color: white; border-radius: 8px; font-weight: bold; padding: 0 16px;")
        self.btn_delete.clicked.connect(self.delete_selected)
        self.btn_delete.setEnabled(False)
        act_layout.addWidget(self.btn_delete)
        
        body_layout.addLayout(act_layout)
        self._layout.addWidget(body)

    def _apply_tree_style(self):
        p = ThemeManager.palette()
        self.tree.setStyleSheet(f"""
            QTreeWidget {{
                background: {p['bg']};
                border: 1px solid {p['border']};
                border-radius: 8px;
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
            QTreeWidget::item {{
                padding: 4px;
                border-bottom: 1px solid {p['border']}55;
            }}
        """)

    def start_scan(self):
        self.btn_scan.setEnabled(False)
        self.btn_smart_select.setEnabled(False)
        self.btn_delete.setEnabled(False)
        self.tree.clear()
        
        user_home = os.path.expanduser("~")
        targets = [
            os.path.join(user_home, "Downloads"),
            os.path.join(user_home, "Documents"),
            os.path.join(user_home, "Pictures"),
            os.path.join(user_home, "Videos"),
            os.path.join(user_home, "Desktop"),
        ]
        
        self.thread = DuplicateScanThread(targets)
        self.thread.progress.connect(self.update_status)
        self.thread.finished.connect(self.on_scan_finished)
        self.thread.start()
        
    def update_status(self, msg):
        self.status_lbl.setText(msg)
        
    def on_scan_finished(self, results):
        self.duplicate_groups = results
        self.btn_scan.setEnabled(True)
        
        if not results:
            self.status_lbl.setText("Scan complete. No duplicates found!")
            return
            
        self.status_lbl.setText(f"Found {len(results)} groups of duplicate files.")
        self.btn_smart_select.setEnabled(True)
        self.btn_delete.setEnabled(True)
        
        p = ThemeManager.palette()
        
        # Populate Tree
        for i, group in enumerate(results):
            group_size = group[0]['size_bytes']
            total_wasted = group_size * (len(group) - 1)
            
            # Group Header
            parent = QTreeWidgetItem(self.tree)
            parent.setText(0, f"Duplicate Group {i+1} ({len(group)} files)")
            parent.setText(1, f"Wasted: {format_size(total_wasted)}")
            parent.setForeground(0, QBrush(QColor(p['accent'])))
            parent.setFont(0, QFont("Segoe UI", 10, QFont.Weight.Bold))
            parent.setFlags(Qt.ItemFlag.ItemIsEnabled)
            
            for file_info in group:
                child = QTreeWidgetItem(parent)
                child.setText(0, file_info['path'])
                child.setText(1, format_size(file_info['size_bytes']))
                
                # Checkbox for 'keep' vs 'delete'
                child.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                child.setCheckState(2, Qt.CheckState.Unchecked) # Unchecked means delete
                
            parent.setExpanded(True)

    def smart_select(self):
        """Checks the newest file in each group to keep it, unchecks the rest to delete."""
        for i in range(self.tree.topLevelItemCount()):
            parent = self.tree.topLevelItem(i)
            
            # Find newest file among children based on file modification time
            newest_idx = 0
            newest_time = 0
            
            for j in range(parent.childCount()):
                child = parent.child(j)
                path = child.text(0)
                try:
                    mtime = os.path.getmtime(path)
                    if mtime > newest_time:
                        newest_time = mtime
                        newest_idx = j
                except Exception:
                    pass
                    
            for j in range(parent.childCount()):
                child = parent.child(j)
                if j == newest_idx:
                    child.setCheckState(2, Qt.CheckState.Checked) # Keep
                else:
                    child.setCheckState(2, Qt.CheckState.Unchecked) # Delete

    def delete_selected(self):
        to_delete = []
        for i in range(self.tree.topLevelItemCount()):
            parent = self.tree.topLevelItem(i)
            # Ensure at least one is kept!
            kept_count = sum(1 for j in range(parent.childCount()) if parent.child(j).checkState(2) == Qt.CheckState.Checked)
            
            if kept_count == 0:
                QMessageBox.warning(self, "Warning", f"You must keep at least one file in {parent.text(0)}.")
                return
                
            for j in range(parent.childCount()):
                child = parent.child(j)
                if child.checkState(2) == Qt.CheckState.Unchecked:
                    to_delete.append({"path": child.text(0)})
                    
        if not to_delete:
            QMessageBox.information(self, "Info", "No files selected for deletion.")
            return
            
        reply = QMessageBox.question(
            self, 'Confirm Deletion',
            f"Are you sure you want to send {len(to_delete)} duplicate files to the Recycle Bin?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, failed = self.recycle_manager.delete_items(to_delete)
            msg = f"Sent {len(success)} files to the Recycle Bin."
            if failed:
                msg += f"\nFailed to delete {len(failed)} files."
            QMessageBox.information(self, "Deletion Complete", msg)
            
            # Refresh view (easiest is to clear for now or rescan)
            self.tree.clear()
            self.btn_smart_select.setEnabled(False)
            self.btn_delete.setEnabled(False)
            self.status_lbl.setText("Duplicates removed successfully.")

    def apply_theme(self):
        self._apply_tree_style()
