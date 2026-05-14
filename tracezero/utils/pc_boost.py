import os
import shutil
import tempfile
import ctypes
from tracezero.utils.logger import app_logger
import winreg

def empty_recycle_bin():
    """Empty the Windows Recycle Bin."""
    try:
        # SHEmptyRecycleBinW (HWND hwnd, LPCTSTR pszRootPath, DWORD dwFlags)
        # SHERB_NOCONFIRMATION = 1, SHERB_NOPROGRESSUI = 2, SHERB_NOSOUND = 4
        result = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
        if result == 0:
            app_logger.info("Recycle Bin emptied successfully.")
            return True
        else:
            app_logger.info(f"Recycle Bin empty returned code: {result} (likely already empty)")
            return False
    except Exception as e:
        app_logger.error(f"Failed to empty Recycle Bin: {e}")
        return False

def clear_temp_files() -> tuple[int, int]:
    """
    Clears the current user's Temp folder.
    Returns (files_deleted, bytes_freed).
    """
    temp_dir = tempfile.gettempdir()
    deleted_count = 0
    bytes_freed = 0
    
    if not os.path.exists(temp_dir):
        return 0, 0

    for item in os.listdir(temp_dir):
        item_path = os.path.join(temp_dir, item)
        try:
            size = 0
            if os.path.isfile(item_path):
                size = os.path.getsize(item_path)
                os.remove(item_path)
            elif os.path.isdir(item_path):
                size = sum(os.path.getsize(os.path.join(dirpath, filename)) 
                           for dirpath, _, filenames in os.walk(item_path) 
                           for filename in filenames)
                shutil.rmtree(item_path)
            
            bytes_freed += size
            deleted_count += 1
        except Exception:
            # Files in use cannot be deleted, which is normal for Temp
            pass
            
    app_logger.info(f"Cleared {deleted_count} temp files, freeing {bytes_freed} bytes.")
    return deleted_count, bytes_freed

def run_pc_boost() -> dict:
    """
    Executes the PC Boost routine.
    Returns stats about what was cleaned.
    """
    stats = {
        "recycle_bin_emptied": False,
        "temp_files_deleted": 0,
        "temp_bytes_freed": 0
    }
    
    stats["recycle_bin_emptied"] = empty_recycle_bin()
    count, freed = clear_temp_files()
    stats["temp_files_deleted"] = count
    stats["temp_bytes_freed"] = freed
    
    return stats
