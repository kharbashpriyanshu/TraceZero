"""
ui/styles.py

Global stylesheet for the App Trace Cleaner UI.
Dark theme with modern GitHub-inspired aesthetics — upgraded version.
"""

from app_trace_cleaner.utils.constants import (
    COLOR_BG_DARK, COLOR_BG_CARD, COLOR_BG_PANEL,
    COLOR_ACCENT, COLOR_ACCENT_GREEN, COLOR_ACCENT_RED, COLOR_ACCENT_ORANGE,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_BORDER, COLOR_HOVER,
    RISK_COLORS
)

MAIN_STYLESHEET = f"""
/* ════════════════════════════════════════════════
   APP TRACE CLEANER — DARK PREMIUM THEME
   ════════════════════════════════════════════════ */

* {{
    font-family: 'Segoe UI', 'Inter', 'Arial', sans-serif;
    font-size: 13px;
    color: {COLOR_TEXT_PRIMARY};
    outline: none;
    box-sizing: border-box;
}}

QMainWindow, QDialog {{
    background-color: {COLOR_BG_DARK};
}}

QWidget {{
    background-color: {COLOR_BG_DARK};
    color: {COLOR_TEXT_PRIMARY};
}}

/* ── SCROLL BARS ─────────────────────────────── */
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 0;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: #30363d;
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {COLOR_ACCENT}88;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    height: 0; background: transparent;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:horizontal {{
    background: #30363d;
    border-radius: 3px;
    min-width: 30px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {COLOR_ACCENT}88;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ── SIDEBAR ─────────────────────────────────── */
#sidebar {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #0d1117, stop:1 #0a0e14);
    border-right: 1px solid {COLOR_BORDER};
}}

#sidebar_btn {{
    background: transparent;
    color: {COLOR_TEXT_SECONDARY};
    border: none;
    padding: 9px 14px;
    text-align: left;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
    margin: 2px 10px;
}}
#sidebar_btn:hover {{
    background-color: {COLOR_HOVER};
    color: {COLOR_TEXT_PRIMARY};
}}
#sidebar_btn_active {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {COLOR_ACCENT}22, stop:1 transparent);
    color: {COLOR_ACCENT};
    border: none;
    border-left: 3px solid {COLOR_ACCENT};
    border-radius: 0px;
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
    padding: 9px 11px;
    margin: 2px 0px 2px 0px;
    font-weight: 700;
}}

/* ── CARDS ───────────────────────────────────── */
#card {{
    background-color: {COLOR_BG_CARD};
    border: 1px solid {COLOR_BORDER};
    border-radius: 12px;
}}
#card:hover {{
    border-color: #3d444d;
}}

#stat_card {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {COLOR_BG_CARD}, stop:1 #1a2030);
    border: 1px solid {COLOR_BORDER};
    border-radius: 14px;
}}
#stat_card:hover {{
    border-color: {COLOR_ACCENT}55;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #1c2230, stop:1 #1e2535);
}}

/* ── BUTTONS ─────────────────────────────────── */
QPushButton {{
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 600;
    font-size: 13px;
}}

#btn_primary {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #1f6feb, stop:1 {COLOR_ACCENT});
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 9px 22px;
    font-size: 13px;
    font-weight: 700;
}}
#btn_primary:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {COLOR_ACCENT}, stop:1 #79b8ff);
}}
#btn_primary:pressed {{
    background: #1158c7;
}}
#btn_primary:disabled {{
    background: #21262d;
    color: {COLOR_TEXT_SECONDARY};
}}

#btn_danger {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #b91c1c, stop:1 {COLOR_ACCENT_RED});
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 9px 22px;
    font-weight: 700;
}}
#btn_danger:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {COLOR_ACCENT_RED}, stop:1 #ff7b7b);
}}
#btn_danger:pressed {{
    background: #9b1111;
}}
#btn_danger:disabled {{
    background: #21262d;
    color: {COLOR_TEXT_SECONDARY};
}}

#btn_secondary {{
    background: {COLOR_BG_PANEL};
    color: {COLOR_TEXT_PRIMARY};
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    padding: 8px 18px;
}}
#btn_secondary:hover {{
    background: {COLOR_HOVER};
    border-color: #4d5566;
    color: #ffffff;
}}
#btn_secondary:pressed {{
    background: #0d1117;
}}

#btn_success {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #1a7f37, stop:1 {COLOR_ACCENT_GREEN});
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 9px 20px;
    font-weight: 700;
}}
#btn_success:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {COLOR_ACCENT_GREEN}, stop:1 #56d364);
}}

/* ── PROGRESS BAR ────────────────────────────── */
QProgressBar {{
    background-color: #21262d;
    border-radius: 3px;
    height: 5px;
    text-align: center;
    color: transparent;
    border: none;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {COLOR_ACCENT}, stop:0.5 #79b8ff, stop:1 {COLOR_ACCENT_GREEN});
    border-radius: 3px;
}}

/* ── TABLE ───────────────────────────────────── */
QTableWidget {{
    background-color: {COLOR_BG_CARD};
    border: 1px solid {COLOR_BORDER};
    border-radius: 10px;
    gridline-color: transparent;
    selection-background-color: transparent;
    outline: none;
}}
QTableWidget::item {{
    padding: 5px 12px;
    border-bottom: 1px solid #1c2128;
    color: {COLOR_TEXT_PRIMARY};
    background: transparent;
}}
QTableWidget::item:selected {{
    background-color: {COLOR_ACCENT}18;
    color: {COLOR_TEXT_PRIMARY};
}}
QTableWidget::item:hover {{
    background-color: {COLOR_HOVER};
}}
QHeaderView {{
    background: transparent;
}}
QHeaderView::section {{
    background: #0d1117;
    color: {COLOR_TEXT_SECONDARY};
    padding: 9px 12px;
    border: none;
    border-bottom: 1px solid {COLOR_BORDER};
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}}
QHeaderView::section:first {{
    border-top-left-radius: 10px;
}}
QHeaderView::section:last {{
    border-top-right-radius: 10px;
}}

/* ── STATUS BAR ──────────────────────────────── */
QStatusBar {{
    background: #0a0e14;
    border-top: 1px solid {COLOR_BORDER};
    color: {COLOR_TEXT_SECONDARY};
    padding: 4px 16px;
    font-size: 12px;
}}
QStatusBar::item {{
    border: none;
}}

/* ── CHECKBOX ────────────────────────────────── */
QCheckBox {{
    color: {COLOR_TEXT_PRIMARY};
    spacing: 8px;
    background: transparent;
}}
QCheckBox::indicator {{
    width: 15px;
    height: 15px;
    border-radius: 4px;
    border: 1.5px solid {COLOR_BORDER};
    background: transparent;
}}
QCheckBox::indicator:checked {{
    background: {COLOR_ACCENT};
    border-color: {COLOR_ACCENT};
}}
QCheckBox::indicator:hover {{
    border-color: {COLOR_ACCENT};
}}

/* ── COMBOBOX ────────────────────────────────── */
QComboBox {{
    background: {COLOR_BG_PANEL};
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    padding: 7px 12px;
    color: {COLOR_TEXT_PRIMARY};
    min-width: 130px;
}}
QComboBox:hover {{
    border-color: {COLOR_ACCENT}88;
    background: {COLOR_HOVER};
}}
QComboBox:focus {{
    border-color: {COLOR_ACCENT};
}}
QComboBox::drop-down {{
    border: none;
    padding-right: 10px;
}}
QComboBox::down-arrow {{
    image: none;
    width: 0;
}}
QComboBox QAbstractItemView {{
    background: #1c2128;
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    selection-background-color: {COLOR_ACCENT}33;
    selection-color: {COLOR_TEXT_PRIMARY};
    padding: 4px;
    outline: none;
}}
QComboBox QAbstractItemView::item {{
    padding: 6px 12px;
    border-radius: 4px;
}}

/* ── LINE EDIT ───────────────────────────────── */
QLineEdit {{
    background: {COLOR_BG_PANEL};
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    padding: 7px 12px;
    color: {COLOR_TEXT_PRIMARY};
    selection-background-color: {COLOR_ACCENT}55;
}}
QLineEdit:hover {{
    border-color: #4d5566;
    background: {COLOR_HOVER};
}}
QLineEdit:focus {{
    border-color: {COLOR_ACCENT};
    background: #161b22;
}}
QLineEdit::placeholder {{
    color: {COLOR_TEXT_SECONDARY};
}}

/* ── TAB WIDGET ──────────────────────────────── */
QTabWidget::pane {{
    border: 1px solid {COLOR_BORDER};
    background: {COLOR_BG_CARD};
    border-radius: 10px;
    top: -1px;
}}
QTabBar {{
    background: transparent;
}}
QTabBar::tab {{
    background: transparent;
    color: {COLOR_TEXT_SECONDARY};
    padding: 9px 20px;
    border: none;
    border-bottom: 2px solid transparent;
    font-weight: 600;
    margin-right: 4px;
}}
QTabBar::tab:selected {{
    color: {COLOR_ACCENT};
    border-bottom: 2px solid {COLOR_ACCENT};
}}
QTabBar::tab:hover:!selected {{
    color: {COLOR_TEXT_PRIMARY};
    background: {COLOR_HOVER};
    border-radius: 6px 6px 0 0;
}}

/* ── TOOLTIP ─────────────────────────────────── */
QToolTip {{
    background: #1c2128;
    border: 1px solid {COLOR_BORDER};
    color: {COLOR_TEXT_PRIMARY};
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 12px;
}}

/* ── MESSAGE BOX ─────────────────────────────── */
QMessageBox {{
    background: #161b22;
}}
QMessageBox QLabel {{
    color: {COLOR_TEXT_PRIMARY};
    background: transparent;
}}
QMessageBox QPushButton {{
    background: {COLOR_BG_PANEL};
    border: 1px solid {COLOR_BORDER};
    color: {COLOR_TEXT_PRIMARY};
    padding: 7px 22px;
    border-radius: 7px;
    min-width: 85px;
    font-weight: 600;
}}
QMessageBox QPushButton:hover {{
    background: {COLOR_HOVER};
    border-color: {COLOR_ACCENT}66;
}}
QMessageBox QPushButton:default {{
    background: {COLOR_ACCENT};
    color: #fff;
    border: none;
}}

/* ── SPINBOX ─────────────────────────────────── */
QSpinBox {{
    background: {COLOR_BG_PANEL};
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    padding: 6px 10px;
    color: {COLOR_TEXT_PRIMARY};
}}
QSpinBox:focus {{
    border-color: {COLOR_ACCENT};
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background: transparent;
    border: none;
    width: 18px;
}}

/* ── GROUP BOX ───────────────────────────────── */
QGroupBox {{
    color: {COLOR_ACCENT};
    font-weight: 700;
    font-size: 13px;
    border: 1px solid {COLOR_BORDER};
    border-radius: 10px;
    margin-top: 14px;
    padding-top: 16px;
    background: {COLOR_BG_CARD};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 10px 0 6px;
    color: {COLOR_ACCENT};
    background: {COLOR_BG_DARK};
    border-radius: 4px;
}}

/* ── SPLITTER ────────────────────────────────── */
QSplitter::handle {{
    background: {COLOR_BORDER};
    width: 1px;
    height: 1px;
}}

/* ── FRAME ───────────────────────────────────── */
QFrame[frameShape="4"] {{ /* HLine */
    background: {COLOR_BORDER};
    border: none;
    max-height: 1px;
    margin: 0;
}}
"""

RISK_BADGE_STYLES = {
    "Safe":   "background:#0d3e22; color:#3fb950; border:1px solid #1a7f37; border-radius:5px; padding:2px 9px; font-weight:800; font-size:11px; letter-spacing:0.5px;",
    "Review": "background:#3d2a00; color:#e3b341; border:1px solid #9e6a03; border-radius:5px; padding:2px 9px; font-weight:800; font-size:11px; letter-spacing:0.5px;",
    "Risky":  "background:#3d0c0c; color:#f85149; border:1px solid #b91c1c; border-radius:5px; padding:2px 9px; font-weight:800; font-size:11px; letter-spacing:0.5px;",
}

CATEGORY_ICONS = {
    "cache":         "🗃",
    "log":           "📋",
    "crash_dump":    "💥",
    "temp":          "⏳",
    "leftover":      "🗑",
    "dead_shortcut": "🔗",
    "registry":      "🗝",
    "unknown":       "❓",
}
