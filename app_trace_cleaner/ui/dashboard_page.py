"""
ui/dashboard_page.py — TraceZero

Redesigned dashboard with:
- Animated gradient stat cards
- Feature highlights with icons
- Recent scan summary
- Big CTA scan button
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor

from app_trace_cleaner.utils.helpers import format_size
from app_trace_cleaner.database.db_manager import get_db
from app_trace_cleaner.utils.constants import APP_VERSION, COLOR_ACCENT


# ─────────────────────────────────────────────────────────────
#  STAT CARD
# ─────────────────────────────────────────────────────────────
class StatCard(QFrame):
    """Premium animated stat card."""

    def __init__(self, title: str, value: str, accent: str, icon: str):
        super().__init__()
        self.accent = accent
        self.setObjectName("stat_card")
        self.setMinimumHeight(120)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(4)

        # Top: icon right-aligned
        top = QHBoxLayout()
        top.addStretch()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 22px; background: transparent; color: {accent}44;")
        top.addWidget(icon_lbl)
        layout.addLayout(top)

        # Value
        self._val_lbl = QLabel(value)
        self._val_lbl.setStyleSheet(
            f"font-size: 32px; font-weight: 900; color: {accent}; "
            "background: transparent; letter-spacing: -1px;"
        )
        layout.addWidget(self._val_lbl)

        # Title
        t = QLabel(title)
        t.setStyleSheet("font-size: 12px; color: #8b949e; background: transparent; font-weight: 600;")
        layout.addWidget(t)

        # Bottom accent bar
        bar = QFrame()
        bar.setFixedHeight(2)
        bar.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {accent}, stop:1 transparent);"
            "border: none; border-radius: 1px; margin-top: 6px;"
        )
        layout.addWidget(bar)

        # Card style
        self.setStyleSheet(f"""
            QFrame#stat_card {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #161b22, stop:1 #1a2030);
                border: 1px solid #30363d;
                border-radius: 14px;
            }}
            QFrame#stat_card:hover {{
                border: 1px solid {accent}55;
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #1c2230, stop:1 #1e2840);
            }}
        """)

    def set_value(self, v: str):
        self._val_lbl.setText(v)


# ─────────────────────────────────────────────────────────────
#  FEATURE PILL
# ─────────────────────────────────────────────────────────────
class FeaturePill(QFrame):
    """Small horizontal feature item."""

    def __init__(self, icon: str, text: str, color: str = "#58a6ff"):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background: {color}11;
                border: 1px solid {color}33;
                border-radius: 8px;
            }}
        """)
        row = QHBoxLayout(self)
        row.setContentsMargins(12, 8, 14, 8)
        row.setSpacing(8)

        ic = QLabel(icon)
        ic.setStyleSheet(f"font-size: 16px; background: transparent; color: {color};")
        row.addWidget(ic)

        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-size: 12px; color: #c9d1d9; background: transparent; font-weight: 500;")
        row.addWidget(lbl, 1)


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

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Hero Banner ───────────────────────────────────────────
        hero = QFrame()
        hero.setFixedHeight(160)
        hero.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #0d1117, stop:0.4 #111827, stop:1 #0d1a2e);
                border-bottom: 1px solid #1e2d45;
            }
        """)
        hero_row = QHBoxLayout(hero)
        hero_row.setContentsMargins(36, 28, 36, 28)
        hero_row.setSpacing(0)

        # Left: title + subtitle
        left = QVBoxLayout()
        left.setSpacing(6)

        welcome = QLabel("Welcome to")
        welcome.setStyleSheet("font-size: 13px; color: #8b949e; background: transparent; font-weight: 500;")
        left.addWidget(welcome)

        brand = QLabel("TraceZero ⚡")
        brand.setStyleSheet(
            "font-size: 32px; font-weight: 900; "
            "color: #e6edf3; background: transparent; letter-spacing: -1px;"
        )
        left.addWidget(brand)

        sub = QLabel("Detect and safely remove leftover application traces from Windows")
        sub.setStyleSheet("font-size: 13px; color: #8b949e; background: transparent;")
        left.addWidget(sub)

        hero_row.addLayout(left, 1)

        # Right: big scan button
        self.scan_btn = QPushButton("  ⚡  Start Scan")
        self.scan_btn.setObjectName("btn_primary")
        self.scan_btn.setFixedSize(160, 46)
        self.scan_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.scan_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #1f6feb, stop:1 #58a6ff);
                color: #fff;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 800;
                letter-spacing: 0.3px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #388bfd, stop:1 #79b8ff);
            }
            QPushButton:pressed { background: #1158c7; }
        """)
        self.scan_btn.clicked.connect(self.scan_requested.emit)
        hero_row.addWidget(self.scan_btn, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        outer.addWidget(hero)

        # ── Scroll area body ──────────────────────────────────────
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(36, 28, 36, 28)
        body_layout.setSpacing(28)

        # ── Stat Cards ─────────────────────────────────────────
        grid = QGridLayout()
        grid.setSpacing(16)

        self.card_scans   = StatCard("Total Scans",      "0",   "#58a6ff", "📊")
        self.card_items   = StatCard("Items Found",      "0",   "#e3b341", "🗑")
        self.card_freed   = StatCard("Space Freed",      "0 B", "#3fb950", "💾")
        self.card_cleaned = StatCard("Items Cleaned",    "0",   "#f85149", "✅")

        grid.addWidget(self.card_scans,   0, 0)
        grid.addWidget(self.card_items,   0, 1)
        grid.addWidget(self.card_freed,   0, 2)
        grid.addWidget(self.card_cleaned, 0, 3)
        body_layout.addLayout(grid)

        # ── Feature Grid ───────────────────────────────────────
        feat_header = QLabel("What TraceZero Does")
        feat_header.setStyleSheet(
            "font-size: 15px; font-weight: 800; color: #e6edf3; background: transparent;"
        )
        body_layout.addWidget(feat_header)

        feat_grid = QGridLayout()
        feat_grid.setSpacing(12)

        features = [
            ("🔍", "Deep Filesystem Scan",      "Scans AppData, Program Files, ProgramData, TEMP and more", "#58a6ff"),
            ("🗝", "Registry Analysis",          "Detects orphaned registry keys left by removed apps",      "#a371f7"),
            ("🔗", "Dead Shortcut Finder",       "Finds broken .lnk files on Desktop and Start Menu",       "#3fb950"),
            ("🧠", "Smart Risk Classification", "Labels every item Safe / Review / Risky automatically",    "#e3b341"),
            ("🛡", "Recycle Bin Protection",     "All deletions go to Recycle Bin — nothing is permanent",   "#3fb950"),
            ("🎮", "Game Store Detection",       "Detects Steam, Epic Games, Winget and Chocolatey apps",    "#f78166"),
        ]

        for i, (icon, title, desc, color) in enumerate(features):
            card = self._feature_card(icon, title, desc, color)
            feat_grid.addWidget(card, i // 3, i % 3)

        body_layout.addLayout(feat_grid)

        # ── Safety Notice ──────────────────────────────────────
        notice = QFrame()
        notice.setStyleSheet("""
            QFrame {
                background: #0d1f0d;
                border: 1px solid #1a7f3722;
                border-left: 3px solid #3fb950;
                border-radius: 10px;
            }
        """)
        n_row = QHBoxLayout(notice)
        n_row.setContentsMargins(16, 12, 16, 12)
        n_row.setSpacing(12)

        shield = QLabel("🛡")
        shield.setStyleSheet("font-size: 20px; background: transparent;")
        n_row.addWidget(shield)

        n_text = QLabel(
            "<b style='color:#3fb950;'>Safety Guarantee:</b> "
            "<span style='color:#8b949e;'>"
            "TraceZero never deletes Windows system files, drivers, Visual C++ Redistributables, "
            ".NET Framework, DirectX, or Java Runtime. Every deletion uses the "
            "<b style='color:#e6edf3;'>Recycle Bin</b> — fully recoverable at any time."
            "</span>"
        )
        n_text.setWordWrap(True)
        n_text.setStyleSheet("background: transparent; font-size: 12px; line-height: 1.5;")
        n_row.addWidget(n_text, 1)

        body_layout.addWidget(notice)
        body_layout.addStretch()

        outer.addWidget(body, 1)

    def _feature_card(self, icon, title, desc, color) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: #161b22;
                border: 1px solid #30363d;
                border-radius: 12px;
            }}
            QFrame:hover {{
                border-color: {color}44;
                background: #1a2030;
            }}
        """)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(6)

        top = QHBoxLayout()
        ic = QLabel(icon)
        ic.setStyleSheet(f"font-size: 20px; background: transparent; color: {color};")
        top.addWidget(ic)
        top.addStretch()
        lay.addLayout(top)

        t = QLabel(title)
        t.setStyleSheet(f"font-size: 13px; font-weight: 700; color: #e6edf3; background: transparent;")
        lay.addWidget(t)

        d = QLabel(desc)
        d.setStyleSheet("font-size: 11px; color: #8b949e; background: transparent;")
        d.setWordWrap(True)
        lay.addWidget(d)

        return card

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
