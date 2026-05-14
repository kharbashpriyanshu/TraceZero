"""
ui/styles.py — TraceZero
Unique "Carbon Violet" theme with full Dark / Light mode support.
"""

# ── Palette definitions ───────────────────────────────────────
DARK = {
    "bg":       "#0f0e17",  "card":    "#16151f",
    "panel":    "#1d1c2a",  "hover":   "#23222f",
    "accent":   "#7c3aed",  "accent2": "#a78bfa",
    "green":    "#10b981",  "red":     "#ef4444",
    "orange":   "#f59e0b",
    "t1":       "#ede9fe",  "t2":      "#8876a8",
    "border":   "#2d2a45",
}

LIGHT = {
    "bg":       "#f7f6fb",  "card":    "#ffffff",
    "panel":    "#eeeaf8",  "hover":   "#e8e3f5",
    "accent":   "#6d28d9",  "accent2": "#7c3aed",
    "green":    "#059669",  "red":     "#dc2626",
    "orange":   "#d97706",
    "t1":       "#1a1033",  "t2":      "#6b5e8a",
    "border":   "#d4cfe8",
}


def _build(t: dict) -> str:
    return f"""
* {{
    font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
    font-size: 13px; color: {t['t1']}; outline: none;
}}
QMainWindow, QDialog, QWidget {{ background-color: {t['bg']}; color: {t['t1']}; }}

/* Explicitly clear QLabel borders — QLabel extends QFrame and can inherit borders */
QLabel {{
    border: none;
    background: transparent;
    padding: 0;
}}

QScrollBar:vertical {{ background:transparent; width:5px; border-radius:3px; }}
QScrollBar::handle:vertical {{ background:{t['border']}; border-radius:3px; min-height:28px; }}
QScrollBar::handle:vertical:hover {{ background:{t['accent']}88; }}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,QScrollBar::sub-page:vertical {{ height:0; background:transparent; }}
QScrollBar:horizontal {{ background:transparent; height:5px; border-radius:3px; }}
QScrollBar::handle:horizontal {{ background:{t['border']}; border-radius:3px; min-width:28px; }}
QScrollBar::handle:horizontal:hover {{ background:{t['accent']}88; }}
QScrollBar::add-line:horizontal,QScrollBar::sub-line:horizontal {{ width:0; }}

#sidebar {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 {t['card']}, stop:1 {t['bg']});
    border-right: 1px solid {t['border']};
}}
#sidebar_btn {{
    background:transparent; color:{t['t2']}; border:none;
    padding:10px 14px; text-align:left; border-radius:8px;
    font-size:13px; font-weight:500; margin:2px 10px;
}}
#sidebar_btn:hover {{ background:rgba(124,58,237,0.10); color:{t['t1']}; }}
#sidebar_btn_active {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {t['accent']}28, stop:1 {t['accent']}08);
    color:{t['accent2']}; border:none;
    border-left:3px solid {t['accent']};
    border-top-right-radius:8px; border-bottom-right-radius:8px;
    border-top-left-radius:0; border-bottom-left-radius:0;
    padding:10px 11px; margin:2px 0; font-weight:700;
}}

#card {{
    background:{t['card']}; border:1px solid {t['border']}; border-radius:12px;
}}
#card:hover {{ border-color:{t['accent']}44; }}

#stat_card {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 {t['card']}, stop:1 {t['panel']});
    border:1px solid {t['border']}; border-radius:14px;
}}
#stat_card:hover {{
    border-color:{t['accent']}55;
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 {t['panel']}, stop:1 {t['hover']});
}}

QPushButton {{ border-radius:8px; padding:8px 18px; font-weight:600; font-size:13px; }}
#btn_primary {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {t['accent']}, stop:1 {t['accent2']});
    color:#fff; border:none; border-radius:9px;
    padding:9px 22px; font-size:13px; font-weight:700;
}}
#btn_primary:hover {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {t['accent2']}, stop:1 #c4b5fd);
}}
#btn_primary:pressed {{ background:{t['accent']}; }}
#btn_primary:disabled {{ background:{t['hover']}; color:{t['t2']}; }}

#btn_danger {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #991b1b, stop:1 {t['red']});
    color:#fff; border:none; border-radius:9px; padding:9px 22px; font-weight:700;
}}
#btn_danger:hover {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {t['red']}, stop:1 #fca5a5);
}}
#btn_danger:pressed {{ background:#7f1d1d; }}
#btn_danger:disabled {{ background:{t['hover']}; color:{t['t2']}; }}

#btn_secondary {{
    background:{t['panel']}; color:{t['t1']}; border:1px solid {t['border']}; border-radius:8px; padding:8px 18px;
}}
#btn_secondary:hover {{ background:{t['hover']}; border-color:{t['accent']}66; }}
#btn_secondary:pressed {{ background:{t['bg']}; }}

#btn_success {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #065f46, stop:1 {t['green']});
    color:#fff; border:none; border-radius:9px; padding:9px 20px; font-weight:700;
}}
#btn_success:hover {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {t['green']}, stop:1 #34d399);
}}

#btn_theme {{
    background:{t['panel']}; color:{t['t1']};
    border:1px solid {t['border']}; border-radius:20px;
    padding:5px 14px; font-size:12px; font-weight:600; margin:4px 10px;
}}
#btn_theme:hover {{ background:{t['hover']}; border-color:{t['accent']}66; }}

QProgressBar {{
    background:{t['hover']}; border-radius:3px; height:4px;
    text-align:center; color:transparent; border:none;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {t['accent']}, stop:0.6 {t['accent2']}, stop:1 {t['green']});
    border-radius:3px;
}}

QTableWidget {{
    background:{t['card']}; border:1px solid {t['border']}; border-radius:12px;
    gridline-color:transparent; selection-background-color:transparent; outline:none;
}}
QTableWidget::item {{
    padding:5px 12px; border-bottom:1px solid {t['border']};
    color:{t['t1']}; background:transparent;
}}
QTableWidget::item:selected {{ background:{t['accent']}14; color:{t['t1']}; }}
QTableWidget::item:hover {{ background:{t['hover']}; }}
QHeaderView {{ background:transparent; }}
QHeaderView::section {{
    background:{t['bg']}; color:{t['t2']};
    padding:9px 12px; border:none; border-bottom:1px solid {t['border']};
    font-weight:700; font-size:11px; letter-spacing:0.8px;
}}
QHeaderView::section:first {{ border-top-left-radius:12px; }}
QHeaderView::section:last  {{ border-top-right-radius:12px; }}

QStatusBar {{
    background:{t['bg']}; border-top:1px solid {t['border']};
    color:{t['t2']}; padding:4px 18px; font-size:12px;
}}
QStatusBar::item {{ border:none; }}

QCheckBox {{ color:{t['t1']}; spacing:8px; background:transparent; }}
QCheckBox::indicator {{
    width:15px; height:15px; border-radius:4px;
    border:1.5px solid {t['border']}; background:transparent;
}}
QCheckBox::indicator:checked {{ background:{t['accent']}; border-color:{t['accent']}; }}
QCheckBox::indicator:hover {{ border-color:{t['accent']}; }}

QComboBox {{
    background:{t['panel']}; border:1px solid {t['border']}; border-radius:8px;
    padding:7px 12px; color:{t['t1']}; min-width:130px;
}}
QComboBox:hover {{ border-color:{t['accent']}66; background:{t['hover']}; }}
QComboBox:focus {{ border-color:{t['accent']}; }}
QComboBox::drop-down {{ border:none; padding-right:10px; }}
QComboBox::down-arrow {{ image:none; width:0; }}
QComboBox QAbstractItemView {{
    background:{t['panel']}; border:1px solid {t['border']}; border-radius:8px;
    selection-background-color:{t['accent']}22; selection-color:{t['t1']};
    padding:4px; outline:none;
}}
QComboBox QAbstractItemView::item {{ padding:6px 12px; border-radius:4px; }}

QLineEdit {{
    background:{t['panel']}; border:1px solid {t['border']}; border-radius:8px;
    padding:7px 12px; color:{t['t1']};
    selection-background-color:{t['accent']}44;
}}
QLineEdit:hover {{ border-color:{t['accent']}55; background:{t['hover']}; }}
QLineEdit:focus {{ border-color:{t['accent']}; }}

QTabWidget::pane {{ border:1px solid {t['border']}; background:{t['card']}; border-radius:10px; top:-1px; }}
QTabBar {{ background:transparent; }}
QTabBar::tab {{
    background:transparent; color:{t['t2']};
    padding:9px 20px; border:none; border-bottom:2px solid transparent;
    font-weight:600; margin-right:4px;
}}
QTabBar::tab:selected {{ color:{t['accent2']}; border-bottom:2px solid {t['accent']}; }}
QTabBar::tab:hover:!selected {{ color:{t['t1']}; background:{t['accent']}0d; border-radius:6px 6px 0 0; }}

QToolTip {{
    background:{t['panel']}; border:1px solid {t['border']};
    color:{t['t1']}; padding:7px 11px; border-radius:7px; font-size:12px;
}}
QMessageBox {{ background:{t['card']}; }}
QMessageBox QLabel {{ color:{t['t1']}; background:transparent; }}
QMessageBox QPushButton {{
    background:{t['panel']}; border:1px solid {t['border']};
    color:{t['t1']}; padding:7px 22px; border-radius:8px; min-width:85px; font-weight:600;
}}
QMessageBox QPushButton:hover {{ background:{t['hover']}; border-color:{t['accent']}66; }}
QMessageBox QPushButton:default {{ background:{t['accent']}; color:#fff; border:none; font-weight:700; }}

QSpinBox {{
    background:{t['panel']}; border:1px solid {t['border']}; border-radius:8px;
    padding:6px 10px; color:{t['t1']};
}}
QSpinBox:focus {{ border-color:{t['accent']}; }}
QSpinBox::up-button, QSpinBox::down-button {{ background:transparent; border:none; width:18px; }}

QGroupBox {{
    color:{t['accent2']}; font-weight:700; font-size:13px;
    border:1px solid {t['border']}; border-radius:12px;
    margin-top:14px; padding-top:16px; background:{t['card']};
}}
QGroupBox::title {{
    subcontrol-origin:margin; subcontrol-position:top left;
    padding:0 10px 0 6px; color:{t['accent2']};
    background:{t['bg']}; border-radius:4px;
}}
QSplitter::handle {{ background:{t['border']}; width:1px; height:1px; }}
QFrame[frameShape="4"] {{ background:{t['border']}; border:none; max-height:1px; margin:0; }}
"""


# ── Theme Manager ─────────────────────────────────────────────
class ThemeManager:
    _mode = "dark"

    @classmethod
    def mode(cls) -> str:
        return cls._mode

    @classmethod
    def is_dark(cls) -> bool:
        return cls._mode == "dark"

    @classmethod
    def toggle(cls):
        cls._mode = "light" if cls._mode == "dark" else "dark"

    @classmethod
    def set(cls, mode: str):
        cls._mode = mode

    @classmethod
    def palette(cls) -> dict:
        return DARK if cls._mode == "dark" else LIGHT

    @classmethod
    def stylesheet(cls) -> str:
        return _build(cls.palette())

    @classmethod
    def icon(cls) -> str:
        return "☀️" if cls._mode == "dark" else "🌙"

    @classmethod
    def label(cls) -> str:
        return "Light Mode" if cls._mode == "dark" else "Dark Mode"


# Keep backward compat
MAIN_STYLESHEET = ThemeManager.stylesheet()

RISK_BADGE_STYLES = {
    "Safe":   "background:#052e16; color:#4ade80; border:1px solid #166534; border-radius:6px; padding:2px 10px; font-weight:800; font-size:11px;",
    "Review": "background:#1c1400; color:#fbbf24; border:1px solid #92400e; border-radius:6px; padding:2px 10px; font-weight:800; font-size:11px;",
    "Risky":  "background:#1c0505; color:#f87171; border:1px solid #7f1d1d; border-radius:6px; padding:2px 10px; font-weight:800; font-size:11px;",
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
