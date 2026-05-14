"""
ui/dashboard_page.py — TraceZero
Premium dashboard with Carbon Violet theme + light/dark support.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout, QSizePolicy,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor

from tracezero.utils.helpers import format_size
from tracezero.database.db_manager import get_db
from tracezero.utils.constants import APP_VERSION
from tracezero.ui.styles import ThemeManager


# ─────────────────────────────────────────────────────────────
#  STAT CARD
# ─────────────────────────────────────────────────────────────
class StatCard(QFrame):
    """Animated stat card — theme-aware."""

    def __init__(self, title: str, value: str, accent: str, icon: str):
        super().__init__()
        self.accent = accent
        self._title = title
        self.setObjectName("stat_card")
        self.setMinimumHeight(130)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(4)

        top = QHBoxLayout()
        top.addStretch()
        self._icon_lbl = QLabel(icon)
        self._icon_lbl.setStyleSheet(f"font-size: 22px; background: transparent; color: {accent}66;")
        top.addWidget(self._icon_lbl)
        layout.addLayout(top)

        self._val_lbl = QLabel(value)
        self._val_lbl.setStyleSheet(
            f"font-size: 32px; font-weight: 900; color: {accent}; "
            "background: transparent; letter-spacing: -1px;"
        )
        layout.addWidget(self._val_lbl)

        self._title_lbl = QLabel(title)
        layout.addWidget(self._title_lbl)

        self._bar = QFrame()
        self._bar.setFixedHeight(2)
        layout.addWidget(self._bar)

        self.refresh_theme()

    def refresh_theme(self):
        p = ThemeManager.palette()
        self._title_lbl.setStyleSheet(
            f"font-size: 12px; color: {p['t2']}; background: transparent; font-weight: 600;"
        )
        self._bar.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {self.accent}, stop:0.6 {self.accent}44, stop:1 transparent);"
            "border: none; border-radius: 1px; margin-top: 8px;"
        )
        self.setStyleSheet(f"""
            QFrame#stat_card {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {p['card']}, stop:1 {p['panel']});
                border: 1px solid {p['border']};
                border-radius: 14px;
            }}
            QFrame#stat_card:hover {{
                border: 1px solid {self.accent}55;
            }}
        """)

    def set_value(self, v: str):
        self._val_lbl.setText(v)


# ─────────────────────────────────────────────────────────────
#  FEATURE CARD  (full-box glow on hover)
# ─────────────────────────────────────────────────────────────
class FeatureCard(QFrame):
    """Feature card that glows as a complete box on hover."""

    def __init__(self, icon: str, title: str, desc: str, color: str):
        super().__init__()
        self._color = color
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(7)

        top = QHBoxLayout()
        ic = QLabel(icon)
        ic.setStyleSheet(f"font-size: 22px; border: none; color: {color};")
        top.addWidget(ic)
        top.addStretch()
        lay.addLayout(top)

        self._title_lbl = QLabel(title)
        lay.addWidget(self._title_lbl)

        self._desc_lbl = QLabel(desc)
        self._desc_lbl.setTextFormat(Qt.TextFormat.PlainText)
        self._desc_lbl.setWordWrap(True)
        lay.addWidget(self._desc_lbl)

        # Apply styles AFTER labels exist
        self._set_default_style()

    def _set_default_style(self):
        p = ThemeManager.palette()
        self.setStyleSheet(f"""
            QFrame {{
                background: {p['card']};
                border: 1px solid {p['border']};
                border-radius: 13px;
            }}
        """)
        if hasattr(self, '_title_lbl'):
            self._title_lbl.setStyleSheet(
                f"font-size: 13px; font-weight: 700; border: none; color: {p['t1']};"
            )
        if hasattr(self, '_desc_lbl'):
            self._desc_lbl.setStyleSheet(
                f"font-size: 11px; border: none; color: {p['t2']};"
            )

    def enterEvent(self, event):
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(28)
        effect.setOffset(0, 0)
        effect.setColor(QColor(self._color))
        self.setGraphicsEffect(effect)
        p = ThemeManager.palette()
        self.setStyleSheet(f"""
            QFrame {{
                background: {p['hover']};
                border: 1px solid {self._color}66;
                border-radius: 13px;
            }}
        """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setGraphicsEffect(None)
        self._set_default_style()
        super().leaveEvent(event)


# ─────────────────────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────────────────────
class DashboardPage(QWidget):
    scan_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db()
        self._build_ui()
        self._refresh_stats()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh_stats)
        self._timer.start(6000)

    # ── Build ─────────────────────────────────────────────────
    def _build_ui(self):
        p = ThemeManager.palette()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Hero Banner ───────────────────────────────────────
        self.hero = QFrame()
        self.hero.setObjectName("_hero")
        self.hero.setFixedHeight(180)
        self._apply_hero_style(p)
        hero_row = QHBoxLayout(self.hero)
        hero_row.setContentsMargins(40, 32, 40, 32)
        hero_row.setSpacing(0)

        left = QVBoxLayout()
        left.setSpacing(6)

        self.welcome_lbl = QLabel("Welcome to")
        self.welcome_lbl.setStyleSheet(
            f"font-size: 13px; color: {p['t2']}; background: transparent; font-weight: 500;"
        )
        left.addWidget(self.welcome_lbl)

        self.brand_lbl = QLabel("TraceZero ⚡")
        self.brand_lbl.setStyleSheet(
            f"font-size: 34px; font-weight: 900; border: none;"
            f" color: {p['t1']}; letter-spacing: -1.5px;"
        )
        left.addWidget(self.brand_lbl)

        self.sub_lbl = QLabel("Detect and safely remove leftover application traces from Windows")
        self.sub_lbl.setStyleSheet(
            f"font-size: 13px; color: {p['t2']}; background: transparent;"
        )
        left.addWidget(self.sub_lbl)
        hero_row.addLayout(left, 1)

        self.scan_btn = QPushButton("  ⚡  Start Scan")
        self.scan_btn.setObjectName("btn_primary")
        self.scan_btn.setFixedSize(170, 50)
        self.scan_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.scan_btn.setStyleSheet(self._build_scan_btn_style(p))
        self.scan_btn.clicked.connect(self.scan_requested.emit)
        hero_row.addWidget(self.scan_btn, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        outer.addWidget(self.hero)

        # ── Scroll body ───────────────────────────────────────
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(36, 28, 36, 28)
        body_layout.setSpacing(28)

        # ── Stat Cards ────────────────────────────────────────
        grid = QGridLayout()
        grid.setSpacing(16)
        self.card_scans   = StatCard("Total Scans",   "0",   p['accent'],  "📊")
        self.card_items   = StatCard("Items Found",   "0",   p['orange'],  "🗑")
        self.card_freed   = StatCard("Space Freed",   "0 B", p['green'],   "💾")
        self.card_cleaned = StatCard("Items Cleaned", "0",   p['red'],     "✅")
        grid.addWidget(self.card_scans,   0, 0)
        grid.addWidget(self.card_items,   0, 1)
        grid.addWidget(self.card_freed,   0, 2)
        grid.addWidget(self.card_cleaned, 0, 3)
        body_layout.addLayout(grid)

        # ── Feature grid ──────────────────────────────────────
        self.feat_header = QLabel("What TraceZero Does")
        self.feat_header.setStyleSheet(
            f"font-size: 15px; font-weight: 800; color: {p['t1']}; background: transparent;"
        )
        body_layout.addWidget(self.feat_header)

        feat_grid = QGridLayout()
        feat_grid.setSpacing(12)
        features = [
            ("🔍", "Deep Filesystem Scan",     "Scans AppData, Program Files, ProgramData, TEMP and more", p['accent']),
            ("🗝", "Registry Analysis",         "Detects orphaned registry keys left by removed apps",      p['accent2']),
            ("🔗", "Dead Shortcut Finder",      "Finds broken .lnk files on Desktop and Start Menu",       p['green']),
            ("🧠", "Smart Risk Classification", "Labels every item Safe / Review / Risky automatically",   p['orange']),
            ("🛡", "Recycle Bin Protection",    "All deletions go to Recycle Bin — nothing is permanent",  p['green']),
            ("🎮", "Game Store Detection",      "Detects Steam, Epic Games, Winget and Chocolatey apps",   p['red']),
        ]
        self.feature_cards = []
        for i, (icon, title, desc, color) in enumerate(features):
            card = FeatureCard(icon, title, desc, color)
            self.feature_cards.append(card)
            feat_grid.addWidget(card, i // 3, i % 3)
        body_layout.addLayout(feat_grid)

        # ── Safety notice ─────────────────────────────────────
        self.notice = QFrame()
        self._apply_notice_style(p)
        n_row = QHBoxLayout(self.notice)
        n_row.setContentsMargins(16, 12, 16, 12)
        n_row.setSpacing(12)

        shield = QLabel("🛡")
        shield.setStyleSheet("font-size: 20px; background: transparent;")
        n_row.addWidget(shield)

        n_text = QLabel(
            f"<b style='color:{p['green']};'>Safety Guarantee:</b> "
            f"<span style='color:{p['t2']};'>"
            "TraceZero never deletes Windows system files, drivers, Visual C++ Redistributables, "
            ".NET Framework, DirectX, or Java Runtime. Every deletion uses the "
            f"<b style='color:{p['t1']};'>Recycle Bin</b> — fully recoverable at any time."
            "</span>"
        )
        n_text.setWordWrap(True)
        n_text.setStyleSheet("background: transparent; font-size: 12px;")
        n_row.addWidget(n_text, 1)
        body_layout.addWidget(self.notice)
        body_layout.addStretch()
        outer.addWidget(body, 1)

    # ── Theme helpers ─────────────────────────────────────────
    def _apply_hero_style(self, p):
        self.hero.setStyleSheet(f"""
            QFrame#_hero {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {p['bg']}, stop:0.5 {p['panel']}, stop:1 {p['card']});
                border-bottom: 1px solid {p['border']};
            }}
        """)

    def _apply_notice_style(self, p):
        self.notice.setStyleSheet(f"""
            QFrame {{
                background: {p['accent']}0d;
                border: 1px solid {p['accent']}22;
                border-left: 3px solid {p['green']};
                border-radius: 10px;
            }}
        """)

    def _build_scan_btn_style(self, p) -> str:
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {p['accent']}, stop:1 {p['accent2']});
                color: #fff; border: none; border-radius: 11px;
                font-size: 15px; font-weight: 800;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {p['accent2']}, stop:1 #c4b5fd);
            }}
            QPushButton:pressed {{ background: {p['accent']}; }}
        """

    def apply_theme(self):
        """Called by MainWindow when theme is toggled."""
        p = ThemeManager.palette()
        self._apply_hero_style(p)
        self._apply_notice_style(p)
        self.scan_btn.setStyleSheet(self._build_scan_btn_style(p))
        self.brand_lbl.setStyleSheet(
            f"font-size: 34px; font-weight: 900; border: none;"
            f" color: {p['t1']}; letter-spacing: -1.5px;"
        )
        self.welcome_lbl.setStyleSheet(
            f"font-size: 13px; border: none; color: {p['t2']}; font-weight: 500;"
        )
        self.sub_lbl.setStyleSheet(
            f"font-size: 13px; border: none; color: {p['t2']};"
        )
        self.feat_header.setStyleSheet(
            f"font-size: 15px; font-weight: 800; border: none; color: {p['t1']};"
        )
        for card in [self.card_scans, self.card_items, self.card_freed, self.card_cleaned]:
            card.refresh_theme()
        for fc in self.feature_cards:
            fc._set_default_style()

    # ── Stats ─────────────────────────────────────────────────
    def _refresh_stats(self):
        try:
            stats = self.db.get_stats()
            self.card_scans.set_value(str(stats.get("total_scans", 0)))
            self.card_cleaned.set_value(str(stats.get("total_deleted_items", 0)))
            self.card_freed.set_value(format_size(int(stats.get("total_space_freed", 0))))
        except Exception:
            pass

    def update_scan_results(self, item_count: int, total_size: int):
        self.card_items.set_value(str(item_count))
        self._refresh_stats()
