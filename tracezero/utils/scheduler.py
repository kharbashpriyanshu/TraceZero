"""
utils/scheduler.py — TraceZero

Manages automatic background scans by integrating with Windows Task Scheduler.
"""

import sys
import os
import subprocess
from tracezero.utils.logger import app_logger

TASK_NAME = r"TraceZero\WeeklyCleanup"

def get_executable_command() -> str:
    """Returns the executable command for the scheduled task."""
    if getattr(sys, 'frozen', False):
        # Running as compiled PyInstaller executable
        return f'"{sys.executable}" --silent'
    else:
        # Running as python script
        return f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}" --silent'

def is_task_scheduled() -> bool:
    """Checks if the TraceZero task is registered in Windows Task Scheduler."""
    if sys.platform != "win32":
        return False
        
    try:
        cmd = f'schtasks /query /tn "{TASK_NAME}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

def schedule_weekly_cleanup() -> bool:
    """Creates a weekly Windows Scheduled Task."""
    if sys.platform != "win32":
        return False
        
    try:
        command = get_executable_command()
        # Schedule for Sunday at 12:00 (Noon)
        cmd = f'schtasks /create /tn "{TASK_NAME}" /tr "{command}" /sc weekly /d SUN /st 12:00 /f'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            app_logger.info("Weekly scheduled task created successfully.")
            return True
        else:
            app_logger.error(f"Failed to create scheduled task: {result.stderr}")
            return False
    except Exception as e:
        app_logger.error(f"Exception creating scheduled task: {e}")
        return False

def remove_scheduled_cleanup() -> bool:
    """Removes the TraceZero task from Windows Task Scheduler."""
    if sys.platform != "win32":
        return False
        
    try:
        cmd = f'schtasks /delete /tn "{TASK_NAME}" /f'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            app_logger.info("Weekly scheduled task removed successfully.")
            return True
        else:
            app_logger.warning(f"Task removal failed (might not exist): {result.stderr}")
            return False
    except Exception as e:
        app_logger.error(f"Exception removing scheduled task: {e}")
        return False
