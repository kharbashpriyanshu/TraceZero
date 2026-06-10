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

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("TraceZero")
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("TraceZero")
    app.setFont(QFont("Segoe UI", 10))

    # Handle silent background sweep
    if "--silent" in sys.argv:
        app_logger.info("Starting silent background sweep...")
        from tracezero.scanner.scan_engine import ScanEngine
        from tracezero.utils.recycle_bin import RecycleBinManager
        
        engine = ScanEngine()
        manager = RecycleBinManager()
        
        # We need to run the scan synchronously or wait for it.
        # Since it's a QThread, we can start it and run a local event loop.
        from PyQt6.QtCore import QEventLoop
        loop = QEventLoop()
        
        # We'll collect items
        scan_results = []
        def _on_item_found(item):
            scan_results.append(item)
            
        def _on_finished():
            loop.quit()
            
        engine.item_found.connect(_on_item_found)
        engine.scan_finished.connect(_on_finished)
        
        engine.start()
        loop.exec() # Block until scan is done
        
        # Only auto-delete "Safe" items to protect the user
        safe_items = [item for item in scan_results if item.get("risk_level") == "Safe"]
        
        if safe_items:
            app_logger.info(f"Silent sweep found {len(safe_items)} safe items. Deleting to Recycle Bin...")
            manager.session_id = engine._session_id
            manager.delete_items(safe_items)
            app_logger.info("Silent sweep complete.")
        else:
            app_logger.info("Silent sweep found no safe items to clean.")
            
        sys.exit(0)

    from tracezero.ui.main_window import MainWindow
    window = MainWindow()
    
    # Handle context menu launch
    if "--analyze" in sys.argv:
        try:
            idx = sys.argv.index("--analyze")
            if idx + 1 < len(sys.argv):
                target_path = sys.argv[idx + 1]
                window.start_analyzer(target_path)
        except Exception as e:
            app_logger.error(f"Failed to start analyzer from CLI: {e}")
            
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
