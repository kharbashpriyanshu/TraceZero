"""
main.py — TraceZero
Smart TraceZero for Windows.

Usage:
    python main.py

Build EXE:
    pyinstaller AppTraceCleaner.spec
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from tracezero.utils.logger import app_logger
from tracezero.utils.constants import APP_NAME, APP_VERSION


def check_dependencies() -> bool:
    missing = []
    for module, pip_name in [
        ("PyQt6",     "PyQt6"),
        ("send2trash","send2trash"),
        ("sqlalchemy","SQLAlchemy"),
    ]:
        try:
            __import__(module)
        except ImportError:
            missing.append(pip_name)

    if missing:
        print(f"\n❌ Missing: {', '.join(missing)}")
        print(f"Install:  pip install {' '.join(missing)}\n")
        return False
    return True


def main():
    app_logger.info(f"Starting {APP_NAME} v{APP_VERSION}")

    if not check_dependencies():
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName("TraceZero")
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("TraceZero")

    app.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app.setFont(QFont("Segoe UI", 10))

    from tracezero.ui.main_window import MainWindow
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
