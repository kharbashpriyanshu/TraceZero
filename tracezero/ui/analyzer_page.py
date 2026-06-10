"""
ui/analyzer_page.py — TraceZero

Disk Space Analyzer using an easy-to-understand Tree Table view.
Finds space hogs by scanning a folder and sorting all subfolders by their size.
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QFileDialog, QTreeWidget, QTreeWidgetItem, QHeaderView,
    QProgressBar, QStyledItemDelegate, QStyleOptionViewItem
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QBrush, QFont, QPainter

from tracezero.ui.styles import ThemeManager
from tracezero.utils.helpers import format_size


class DirNode:
    """Represents a file or directory for the analyzer."""
    def __init__(self, path: str, name: str, is_dir: bool):
        self.path = path
        self.name = name
        self.is_dir = is_dir
        self.size = 0
        self.children = []


class ScanDriveThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(object)

    def __init__(self, target_path: str):
        super().__init__()
        self.target_path = target_path
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        root = DirNode(self.target_path, os.path.basename(self.target_path) or self.target_path, True)
        self._scan(root)
        if not self._is_cancelled:
            self.finished.emit(root)

    def _scan(self, node: DirNode):
        if self._is_cancelled:
            return
            
        try:
            for entry in os.scandir(node.path):
                if self._is_cancelled:
                    return
                if entry.is_symlink():
                    continue
                
                if entry.is_dir():
                    child = DirNode(entry.path, entry.name, True)
                    self._scan(child)
                    if child.size > 0:
                        node.size += child.size
                        node.children.append(child)
                else:
                    try:
                        sz = entry.stat().st_size
                        node.size += sz
                        child = DirNode(entry.path, entry.name, False)
                        child.size = sz
                        node.children.append(child)
                    except OSError:
                        pass
                        
            # Sort children by size descending so biggest are always at the top
            node.children.sort(key=lambda x: x.size, reverse=True)
                
        except (PermissionError, OSError):
            pass


class ProgressBarDelegate(QStyledItemDelegate):
    """Draws a visual progress bar inside the QTreeWidget cell."""
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        if index.column() == 2: # The % bar column
            percentage = index.data(Qt.ItemDataRole.UserRole)
            if percentage is not None:
                p = ThemeManager.palette()
                
                # Draw background track
                track_rect = option.rect.adjusted(4, 6, -4, -6)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(p['border']))
                painter.drawRoundedRect(track_rect, 4, 4)
                
                # Draw fill
                if percentage > 0:
                    fill_rect = track_rect.adjusted(0, 0, 0, 0)
                    fill_rect.setWidth(int(track_rect.width() * percentage))
                    
                    # Color based on size (red for > 50%, orange > 20%, blue otherwise)
                    if percentage >= 0.5:
                        color = QColor(p['red'])
                    elif percentage >= 0.2:
                        color = QColor(p['orange'])
                    else:
                        color = QColor(p['accent'])
                        
                    painter.setBrush(color)
                    painter.drawRoundedRect(fill_rect, 4, 4)
                
                # Draw text percentage
                painter.setPen(QColor(p['t1']))
                font = QFont("Segoe UI", 9, QFont.Weight.Bold)
                painter.setFont(font)
                text = f"{int(percentage * 100)}%"
                painter.drawText(option.rect, Qt.AlignmentFlag.AlignCenter, text)
                return
                
        super().paint(painter, option, index)


class AnalyzerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread = None
        self.root_node = None
        self._build_ui()

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
        
        title = QLabel("Disk Space Analyzer")
        title.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {p['t1']}; border: none;")
        tl.addWidget(title)
        
        sub = QLabel("Easily find massive files and folders that are eating up your hard drive space.")
        sub.setStyleSheet(f"font-size: 11px; color: {p['t2']}; border: none;")
        tl.addWidget(sub)
        
        layout.addWidget(title_frame)

        # Body
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(24, 20, 24, 20)
        body_layout.setSpacing(16)

        # Controls
        ctrl_layout = QHBoxLayout()
        
        self.btn_scan = QPushButton("📁 Analyze Folder / Drive")
        self.btn_scan.setObjectName("btn_primary")
        self.btn_scan.setFixedSize(220, 38)
        self.btn_scan.setStyleSheet(f"background: {p['accent']}; color: white; border-radius: 8px; font-weight: bold;")
        self.btn_scan.clicked.connect(self.select_folder)
        ctrl_layout.addWidget(self.btn_scan)
        
        self.status_lbl = QLabel("Ready. Select a folder to begin mapping.")
        self.status_lbl.setStyleSheet(f"color: {p['t2']}; font-weight: 500; font-size: 13px; margin-left: 12px;")
        ctrl_layout.addWidget(self.status_lbl)
        ctrl_layout.addStretch()
        
        body_layout.addLayout(ctrl_layout)

        # Tree Widget for listing large folders
        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Name / Path", "Total Size", "% of Total"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.tree.header().resizeSection(1, 140)
        self.tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.tree.header().resizeSection(2, 200)
        
        # Connect expansion event for lazy loading
        self.tree.itemExpanded.connect(self.on_item_expanded)
        
        # Apply custom progress bar delegate
        self.delegate = ProgressBarDelegate()
        self.tree.setItemDelegate(self.delegate)
        
        self._apply_tree_style()
        body_layout.addWidget(self.tree, 1)

        layout.addWidget(body, 1)

    def _apply_tree_style(self):
        p = ThemeManager.palette()
        self.tree.setStyleSheet(f"""
            QTreeWidget {{
                background: {p['bg']};
                border: 1px solid {p['border']};
                border-radius: 8px;
                color: {p['t1']};
                font-size: 13px;
                padding: 4px;
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
                padding: 6px;
                border-bottom: 1px solid {p['border']}33;
            }}
            QTreeWidget::item:selected {{
                background: {p['accent']}33;
            }}
        """)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Folder or Drive to Analyze", "C:\\",
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontUseNativeDialog
        )
        if folder:
            self.start_scan(folder)

    def start_scan(self, path: str):
        if self.thread and self.thread.isRunning():
            self.thread.cancel()
            self.thread.wait()
            
        self.tree.clear()
        self.btn_scan.setEnabled(False)
        self.status_lbl.setText(f"Scanning & calculating sizes for: {path} ... (This may take a minute)")
        
        self.thread = ScanDriveThread(path)
        self.thread.finished.connect(self.on_scan_finished)
        self.thread.start()

    def on_scan_finished(self, root_node: DirNode):
        self.btn_scan.setEnabled(True)
        self.root_node = root_node
        
        if root_node.size == 0:
            self.status_lbl.setText("Folder is empty or access denied.")
            return
            
        self.status_lbl.setText(f"Analyzed {format_size(root_node.size)} inside {root_node.path}")
        
        # Populate Root
        self._populate_node(root_node, self.tree, root_node.size)

    def _populate_node(self, node: DirNode, parent_widget, total_root_size: int):
        p = ThemeManager.palette()
        
        for child in node.children:
            item = QTreeWidgetItem(parent_widget)
            
            # Icon depending on file/folder
            icon_str = "📁 " if child.is_dir else "📄 "
            item.setText(0, icon_str + child.name)
            item.setToolTip(0, child.path)
            
            if child.is_dir:
                item.setFont(0, QFont("Segoe UI", 10, QFont.Weight.Bold))
                item.setForeground(0, QBrush(QColor(p['accent2'])))
                
            item.setText(1, format_size(child.size))
            
            # Set percentage for custom delegate
            fraction = child.size / total_root_size if total_root_size > 0 else 0
            item.setData(2, Qt.ItemDataRole.UserRole, fraction)
            
            # Store the node reference inside the item for lazy loading
            # But PyQt wrapper can't store complex python objects in data without wrapping, 
            # so we just attach it directly dynamically.
            item._dir_node = child
            item._loaded = False
            
            # Add a dummy child if this is a directory and has children, so the expand arrow appears
            if child.is_dir and child.children:
                dummy = QTreeWidgetItem(item)
                dummy.setText(0, "Loading...")

    def on_item_expanded(self, item: QTreeWidgetItem):
        if not hasattr(item, '_loaded') or item._loaded:
            return
            
        # Remove dummy
        item.takeChildren()
        
        node = item._dir_node
        
        # We calculate the percentage relative to the *root* drive size, not the parent folder size.
        # This shows exactly how much of the ENTIRE drive this specific folder takes up!
        self._populate_node(node, item, self.root_node.size)
        item._loaded = True

    def apply_theme(self):
        root = self.layout()
        if root:
            self._clear_layout(root)
        self._build_ui()
        if self.root_node:
            self.tree.clear()
            self._populate_node(self.root_node, self.tree, self.root_node.size)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
                item.layout().deleteLater()
