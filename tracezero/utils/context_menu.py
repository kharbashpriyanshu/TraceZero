"""
utils/context_menu.py — TraceZero

Manages adding and removing TraceZero from the Windows Explorer right-click context menu.
"""

import sys
import os
import winreg
from tracezero.utils.logger import app_logger


def get_command_string() -> str:
    """Returns the executable command string for the context menu."""
    if getattr(sys, 'frozen', False):
        # Running as compiled PyInstaller executable
        exe_path = f'"{sys.executable}"'
    else:
        # Running as python script
        exe_path = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'
        
    return f'{exe_path} --analyze "%1"'


def is_context_menu_installed() -> bool:
    """Checks if the context menu entry already exists."""
    if sys.platform != "win32":
        return False
        
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\Directory\shell\TraceZero")
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False


def install_context_menu() -> bool:
    """Adds TraceZero to the Windows context menu."""
    if sys.platform != "win32":
        return False
        
    try:
        command_str = get_command_string()
        
        # Determine icon path (use sys.executable if compiled, else use assets/icon.ico)
        if getattr(sys, 'frozen', False):
            icon_path = f'"{sys.executable}"'
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            icon_path = f'"{os.path.join(base_dir, "assets", "icon.ico")}"'

        def add_key(base_path):
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, base_path) as key:
                winreg.SetValue(key, "", winreg.REG_SZ, "Analyze Space with TraceZero")
                if icon_path:
                    winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon_path)
                with winreg.CreateKey(key, "command") as cmd_key:
                    winreg.SetValue(cmd_key, "", winreg.REG_SZ, command_str)

        # Add to folders
        add_key(r"Software\Classes\Directory\shell\TraceZero")
        # Add to folder backgrounds (right click inside a folder window)
        add_key(r"Software\Classes\Directory\Background\shell\TraceZero")
        
        app_logger.info("Windows context menu installed successfully.")
        return True
    except Exception as e:
        app_logger.error(f"Failed to install context menu: {e}")
        return False


def remove_context_menu() -> bool:
    """Removes TraceZero from the Windows context menu."""
    if sys.platform != "win32":
        return False
        
    try:
        def delete_key(base_path):
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, base_path + r"\command")
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, base_path)
            except FileNotFoundError:
                pass

        delete_key(r"Software\Classes\Directory\shell\TraceZero")
        delete_key(r"Software\Classes\Directory\Background\shell\TraceZero")
        
        app_logger.info("Windows context menu removed successfully.")
        return True
    except Exception as e:
        app_logger.error(f"Failed to remove context menu: {e}")
        return False
