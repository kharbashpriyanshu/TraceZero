"""
ui/scan_page.py — TraceZero

Redesigned scan page with:
- Real colored risk badges (QLabel inside table cells)
- Improved progress section with animated bar
- Cleaner filter row
- Better action bar
"""

from typing import List, Dict

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QComboBox, QLineEdit, QAbstractItemView,
    QSizePolicy, QMessageBox, QApplication,
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, pyqtSlot
from PyQt6.QtGui import QFont, QColor, QBrush

from tracezero.utils.helpers import format_size, truncate_path
from tracezero.utils.constants import RISK_COLORS, COLOR_ACCENT
from tracezero.ui.styles import CATEGORY_ICONS, ThemeManager
from tracezero.utils.logger import app_logger

# Column indices
COL_CHECK = 0
COL_ICON  = 1
COL_PATH  = 2
COL_CAT   = 3
COL_SIZE  = 4
COL_AGE   = 5
COL_RISK  = 6
COL_WHY   = 7

RISK_CELL_STYLE = {
    "Safe":   ("●  Safe",   "#062010", "#4ade80", "#166534"),
    "Review": ("●  Review", "#1c1400", "#fb923c", "#7c4a00"),
    "Risky":  ("●  Risky",  "#1c0505", "#f87171", "#7f1d1d"),
}

CAT_COLORS = {
    "cache":        "#4ade80",
    "log":          "#a3e635",
    "crash_dump":   "#f87171",
    "temp":         "#fb923c",
    "leftover":     "#7d8c80",
    "dead_shortcut":"#34d399",
    "registry":     "#86efac",
    "unknown":      "#6b7c70",
}


class _Signals(QObject):
    item_found = pyqtSignal(dict)
    progress   = pyqtSignal(str, int)
    status     = pyqtSignal(str)
    complete   = pyqtSignal(list)
    error      = pyqtSignal(str)


class ScanPage(QWidget):
    delete_requested = pyqtSignal(list)

    def __init__(self, scan_engine, parent=None):
        super().__init__(parent)
        self.scan_engine     = scan_engine
        self._all_items: List[Dict] = []
        self._filtered: List[Dict]  = []
        self._row_data: Dict[int, Dict] = {}
        self._is_scanning = False

        self._wire_signals()
        self._build_ui()

    # ── Signal wiring ─────────────────────────────────────────
    def _wire_signals(self):
        self.sig = _Signals()
        self.scan_engine.on_item_found = lambda i: self.sig.item_found.emit(i)
        self.scan_engine.on_progress   = lambda m, c: self.sig.progress.emit(m, c)
        self.scan_engine.on_status     = lambda m: self.sig.status.emit(m)
        self.scan_engine.on_complete   = lambda r: self.sig.complete.emit(r)
        self.scan_engine.on_error      = lambda e: self.sig.error.emit(e)

        self.sig.item_found.connect(self._on_item)
        self.sig.progress.connect(self._on_progress)
        self.sig.status.connect(self._on_status)
        self.sig.complete.connect(self._on_complete)
        self.sig.error.connect(self._on_error)

    # ── UI Build ──────────────────────────────────────────────
    def _build_ui(self):
        root = self.layout()
        if root is None:
            root = QVBoxLayout(self)
            root.setContentsMargins(0, 0, 0, 0)
            root.setSpacing(0)

        # ── Top bar (header + controls) ───────────────────────
        p = ThemeManager.palette()
        topbar = QFrame()
        topbar.setFixedHeight(68)
        topbar.setObjectName("_topbar")
        topbar.setStyleSheet(f"""
            QFrame#_topbar {{
                background: {p['card']};
                border-bottom: 1px solid {p['border']};
            }}
        """)
        tb_row = QHBoxLayout(topbar)
        tb_row.setContentsMargins(28, 0, 20, 0)
        tb_row.setSpacing(10)

        # Title block
        t_col = QVBoxLayout()
        t_col.setSpacing(1)
        page_title = QLabel("Scan & Clean")
        page_title.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {p['t1']}; border: none;")
        t_col.addWidget(page_title)
        self.subtitle = QLabel("Ready — press Start Scan to begin")
        self.subtitle.setStyleSheet(f"font-size: 11px; color: {p['t2']}; border: none;")
        t_col.addWidget(self.subtitle)
        tb_row.addLayout(t_col, 1)

        # Buttons
        self.btn_start = self._make_btn("  ⚡  Start Scan", "btn_primary", w=136)
        self.btn_pause = self._make_btn("⏸  Pause",       "btn_secondary", enabled=False)
        self.btn_stop  = self._make_btn("⏹  Stop",        "btn_secondary", enabled=False)

        self.btn_start.clicked.connect(self._start_scan)
        self.btn_pause.clicked.connect(self._toggle_pause)
        self.btn_stop.clicked.connect(self._stop_scan)

        for b in [self.btn_start, self.btn_pause, self.btn_stop]:
            b.setFixedHeight(38)
            tb_row.addWidget(b)

        root.addWidget(topbar)

        # ── Progress strip ────────────────────────────────────
        self.prog_strip = QFrame()
        self.prog_strip.setFixedHeight(40)
        self.prog_strip.setObjectName("_pstrip")
        self.prog_strip.setStyleSheet(f"""
            QFrame#_pstrip {{
                background: {p['panel']};
                border-bottom: 1px solid {p['border']};
            }}
        """)
        ps_row = QHBoxLayout(self.prog_strip)
        ps_row.setContentsMargins(28, 0, 20, 0)
        ps_row.setSpacing(14)

        self.status_lbl = QLabel("Idle — no scan running")
        self.status_lbl.setStyleSheet(f"font-size: 12px; color: {p['t2']}; border: none;")
        ps_row.addWidget(self.status_lbl, 1)

        self.prog_bar = QProgressBar()
        self.prog_bar.setRange(0, 0)
        self.prog_bar.setFixedSize(160, 5)
        self.prog_bar.setVisible(False)
        ps_row.addWidget(self.prog_bar)

        self.count_lbl = QLabel("Items: 0")
        self.count_lbl.setStyleSheet(
            f"font-size: 12px; color: {p['accent']}; font-weight: 700; border: none;"
        )
        self.count_lbl.setFixedWidth(110)
        self.count_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        ps_row.addWidget(self.count_lbl)

        root.addWidget(self.prog_strip)

        # ── Body ──────────────────────────────────────────────
        body = QWidget()
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(24, 16, 24, 14)
        body_lay.setSpacing(12)

        # ── Filter row ────────────────────────────────────────
        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔎   Filter by path or app name…")
        self.search.setFixedHeight(36)
        self.search.textChanged.connect(self._apply_filters)
        filter_row.addWidget(self.search, 2)

        self.risk_cb = self._make_combo(["All Risks", "Safe", "Review", "Risky"])
        self.cat_cb  = self._make_combo(["All Categories", "cache", "log", "crash_dump",
                                         "temp", "leftover", "dead_shortcut", "registry"])
        self.risk_cb.currentTextChanged.connect(self._apply_filters)
        self.cat_cb.currentTextChanged.connect(self._apply_filters)
        filter_row.addWidget(self.risk_cb)
        filter_row.addWidget(self.cat_cb)

        body_lay.addLayout(filter_row)

        # ── Stats bar ─────────────────────────────────────────
        self.stats_bar = QLabel("Run a scan to detect leftover traces.")
        self.stats_bar.setStyleSheet(f"font-size: 11px; color: {p['t2']}; border: none;")
        body_lay.addWidget(self.stats_bar)

        # ── Table ─────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["", "", "Path", "Category", "Size", "Age", "Risk", "Reason"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.itemClicked.connect(self._on_click)

        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(COL_CHECK, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(COL_ICON,  QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(COL_PATH,  QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(COL_CAT,   QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(COL_SIZE,  QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(COL_AGE,   QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(COL_RISK,  QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(COL_WHY,   QHeaderView.ResizeMode.ResizeToContents)
        self.table.setColumnWidth(COL_CHECK, 36)
        self.table.setColumnWidth(COL_ICON,  34)

        body_lay.addWidget(self.table, 1)

        # ── Action bar ────────────────────────────────────────
        act = QFrame()
        act.setFixedHeight(56)
        act.setObjectName("_actbar")
        act.setStyleSheet(f"""
            QFrame#_actbar {{
                background: {p['card']};
                border-top: 1px solid {p['border']};
            }}
        """)
        act_row = QHBoxLayout(act)
        act_row.setContentsMargins(24, 0, 20, 0)
        act_row.setSpacing(8)

        b_all  = self._make_btn("Select All",    "btn_secondary", h=34)
        b_none = self._make_btn("Deselect All",  "btn_secondary", h=34)
        b_safe = self._make_btn("✅  Safe Only", "btn_secondary", h=34)
        b_all.clicked.connect(lambda: self._set_all(True))
        b_none.clicked.connect(lambda: self._set_all(False))
        b_safe.clicked.connect(self._select_safe)

        act_row.addWidget(b_all)
        act_row.addWidget(b_none)
        act_row.addWidget(b_safe)
        act_row.addStretch()

        self.sel_lbl = QLabel("")
        self.sel_lbl.setStyleSheet(f"font-size: 12px; color: {p['t2']}; border: none;")
        act_row.addWidget(self.sel_lbl)

        self.btn_delete = self._make_btn("  🗑  Delete Selected", "btn_danger", h=38, enabled=False)
        self.btn_delete.setMinimumWidth(160)
        self.btn_delete.clicked.connect(self._confirm_delete)
        act_row.addWidget(self.btn_delete)

        body_lay.addWidget(act)
        root.addWidget(body, 1)

    # ── Helpers ───────────────────────────────────────────────
    def _make_btn(self, text, obj, w=None, h=38, enabled=True) -> QPushButton:
        b = QPushButton(text)
        b.setObjectName(obj)
        b.setEnabled(enabled)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setFixedHeight(h)
        if w:
            b.setMinimumWidth(w)
        return b

    def _make_combo(self, items) -> QComboBox:
        cb = QComboBox()
        cb.addItems(items)
        cb.setFixedHeight(36)
        return cb

    # ── Scan control ──────────────────────────────────────────
    def start_scan(self):
        self._start_scan()

    def _start_scan(self):
        if self._is_scanning:
            return
        self._all_items.clear()
        self._filtered.clear()
        self._row_data.clear()
        self.table.setRowCount(0)
        self.count_lbl.setText("Items: 0")
        self.stats_bar.setText("Scanning…")
        self._is_scanning = True

        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_stop.setEnabled(True)
        self.btn_delete.setEnabled(False)
        self.prog_bar.setVisible(True)
        self.subtitle.setText("Scan in progress…")

        self.scan_engine.start()

    def _toggle_pause(self):
        if not self._is_scanning:
            return
        if "Pause" in self.btn_pause.text():
            self.scan_engine.pause()
            self.btn_pause.setText("▶  Resume")
            self.status_lbl.setText("Scan paused")
        else:
            self.scan_engine.resume()
            self.btn_pause.setText("⏸  Pause")

    def _stop_scan(self):
        self.scan_engine.stop()
        self._finish_scan()
        self.status_lbl.setText("Scan stopped by user")

    def _finish_scan(self):
        self._is_scanning = False
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.prog_bar.setVisible(False)
        self.btn_pause.setText("⏸  Pause")
        if self._all_items:
            self.btn_delete.setEnabled(True)

    # ── Callbacks ─────────────────────────────────────────────
    @pyqtSlot(dict)
    def _on_item(self, item: Dict):
        self._all_items.append(item)
        # Batch UI updates: only rebuild every 25 items for performance
        if len(self._all_items) % 25 == 0 or len(self._all_items) <= 10:
            self._apply_filters()
        self.count_lbl.setText(f"Items: {len(self._all_items)}")

    @pyqtSlot(str, int)
    def _on_progress(self, msg: str, cnt: int):
        self.status_lbl.setText(msg[:90])

    @pyqtSlot(str)
    def _on_status(self, msg: str):
        self.status_lbl.setText(msg[:100])

    @pyqtSlot(list)
    def _on_complete(self, results):
        self._finish_scan()
        self._apply_filters()  # Final full rebuild
        total = sum(i.get("size_bytes", 0) for i in results)
        self.status_lbl.setText(
            f"✅  Scan complete — {len(results)} items, {format_size(int(total))}"
        )
        self.subtitle.setText(f"Found {len(results)} items  ({format_size(int(total))})")
        self._update_stats()

    @pyqtSlot(str)
    def _on_error(self, err: str):
        self._finish_scan()
        self.status_lbl.setText(f"❌  Error: {err}")
        QMessageBox.critical(self, "Scan Error", f"Scan failed:\n\n{err}")

    # ── Filtering & table ─────────────────────────────────────
    def _apply_filters(self):
        search = self.search.text().lower()
        risk_f = self.risk_cb.currentText()
        cat_f  = self.cat_cb.currentText()

        self._filtered = [
            i for i in self._all_items
            if (not search or search in i.get("path","").lower() or search in i.get("app_name","").lower())
            and (risk_f == "All Risks" or i.get("risk_level") == risk_f)
            and (cat_f  == "All Categories" or i.get("category") == cat_f)
        ]
        self._rebuild_table()

    def _rebuild_table(self):
        self.table.setUpdatesEnabled(False)
        self.table.setRowCount(0)
        self._row_data.clear()

        for item in self._filtered:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 38)
            self._row_data[row] = item

            # ── Checkbox ──────────────────────────────────────
            chk = QTableWidgetItem()
            chk.setCheckState(Qt.CheckState.Checked if item.get("is_selected", True) else Qt.CheckState.Unchecked)
            chk.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, COL_CHECK, chk)

            # ── Icon ──────────────────────────────────────────
            cat = item.get("category", "unknown")
            ic  = QTableWidgetItem(CATEGORY_ICONS.get(cat, "❓"))
            ic.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, COL_ICON, ic)

            # ── Path ──────────────────────────────────────────
            path = item.get("path", "")
            pi   = QTableWidgetItem(truncate_path(path, 72))
            pi.setToolTip(path)
            pi.setForeground(QBrush(QColor(ThemeManager.palette()['t1'])))
            self.table.setItem(row, COL_PATH, pi)

            # ── Category (colored) ────────────────────────────
            cat_color = CAT_COLORS.get(cat, "#8b949e")
            ci = QTableWidgetItem(cat.replace("_", " ").title())
            ci.setForeground(QBrush(QColor(cat_color)))
            ci.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            self.table.setItem(row, COL_CAT, ci)

            # ── Size ──────────────────────────────────────────
            sz = QTableWidgetItem(format_size(int(item.get("size_bytes", 0))))
            sz.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            sz.setForeground(QBrush(QColor(ThemeManager.palette()['t2'])))
            self.table.setItem(row, COL_SIZE, sz)

            age = item.get("age_days")
            age_str = f"{age}d" if age is not None else "—"
            ai = QTableWidgetItem(age_str)
            ai.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            ai.setForeground(QBrush(QColor(ThemeManager.palette()['t2'])))
            self.table.setItem(row, COL_AGE, ai)

            risk = item.get("risk_level", "Review")
            label_map = {"Safe": "● Safe", "Review": "● Review", "Risky": "● Risky"}
            ri = QTableWidgetItem(label_map.get(risk, risk))
            ri.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            ri.setForeground(QBrush(QColor(RISK_COLORS.get(risk, ThemeManager.palette()['t2']))))
            ri.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            self.table.setItem(row, COL_RISK, ri)

            reason = item.get("reason", "")
            why = QTableWidgetItem(reason[:65])
            why.setToolTip(reason)
            why.setForeground(QBrush(QColor(ThemeManager.palette()['t2'])))
            self.table.setItem(row, COL_WHY, why)

        self.table.setUpdatesEnabled(True)
        self._update_stats()

    def _on_click(self, item: QTableWidgetItem):
        if item.column() == COL_CHECK:
            data = self._row_data.get(item.row())
            if data:
                data["is_selected"] = item.checkState() == Qt.CheckState.Checked
            self._update_sel_lbl()

    def _update_stats(self):
        total = len(self._all_items)
        shown = len(self._filtered)
        safe  = sum(1 for i in self._all_items if i.get("risk_level") == "Safe")
        rev   = sum(1 for i in self._all_items if i.get("risk_level") == "Review")
        risky = sum(1 for i in self._all_items if i.get("risk_level") == "Risky")
        sz    = sum(i.get("size_bytes", 0) for i in self._all_items)
        self.stats_bar.setText(
            f"Showing {shown}/{total}  •  "
            f"<span style='color:#3fb950;'>Safe {safe}</span>  "
            f"<span style='color:#e3b341;'>Review {rev}</span>  "
            f"<span style='color:#f85149;'>Risky {risky}</span>  •  "
            f"Total {format_size(int(sz))}"
        )
        self.stats_bar.setTextFormat(Qt.TextFormat.RichText)
        self._update_sel_lbl()

    def _update_sel_lbl(self):
        sel  = [i for i in self._all_items if i.get("is_selected", True)]
        sz   = sum(i.get("size_bytes", 0) for i in sel)
        self.sel_lbl.setText(f"Selected: {len(sel)} ({format_size(int(sz))})")
        self.btn_delete.setEnabled(len(sel) > 0 and not self._is_scanning)

    # ── Selection helpers ─────────────────────────────────────
    def _set_all(self, state: bool):
        for row in range(self.table.rowCount()):
            c = self.table.item(row, COL_CHECK)
            if c:
                c.setCheckState(Qt.CheckState.Checked if state else Qt.CheckState.Unchecked)
            d = self._row_data.get(row)
            if d:
                d["is_selected"] = state
        self._update_sel_lbl()

    def _select_safe(self):
        for row in range(self.table.rowCount()):
            d = self._row_data.get(row)
            if d:
                safe = d.get("risk_level") == "Safe"
                d["is_selected"] = safe
                c = self.table.item(row, COL_CHECK)
                if c:
                    c.setCheckState(Qt.CheckState.Checked if safe else Qt.CheckState.Unchecked)
        self._update_sel_lbl()

    # ── Deletion ──────────────────────────────────────────────
    def _confirm_delete(self):
        selected = [i for i in self._all_items if i.get("is_selected", True)]
        if not selected:
            QMessageBox.information(self, "Nothing Selected", "Please select items to delete.")
            return

        total_size = sum(i.get("size_bytes", 0) for i in selected)
        risky = [i for i in selected if i.get("risk_level") == "Risky"]

        dlg = QMessageBox(self)
        dlg.setWindowTitle("Confirm Cleanup")
        dlg.setIcon(QMessageBox.Icon.Warning)
        dlg.setText(
            f"Send <b>{len(selected)} item(s)</b> ({format_size(int(total_size))}) to the Recycle Bin?\n\n"
            f"• All files go to the Recycle Bin — nothing is permanent\n"
            f"• You can restore at any time from the Recycle Bin"
            + (f"\n\n⚠️ {len(risky)} Risky item(s) selected — they will be skipped automatically." if risky else "")
        )
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        dlg.setDefaultButton(QMessageBox.StandardButton.Cancel)

        if dlg.exec() == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(selected)

    @pyqtSlot(dict)
    def remove_deleted_item(self, item: Dict):
        """Called by MainWindow when an item is successfully deleted to remove it from UI."""
        if item in self._all_items:
            self._all_items.remove(item)
        if item in self._filtered:
            self._filtered.remove(item)
            
        for row in range(self.table.rowCount()):
            data = self._row_data.get(row)
            if data == item:
                self.table.setRowHidden(row, True)
                break
                
        self._update_stats()

    # ── Theme ─────────────────────────────────────────────────
    def apply_theme(self):
        root = self.layout()
        if root:
            self._clear_layout(root)
        self._build_ui()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
                item.layout().deleteLater()
