"""
registry/startup_manager.py — TraceZero

Handles reading, disabling, and enabling Windows Startup Applications.
Mimics the Startup Apps tab in Task Manager / PC Manager.
"""

import winreg
from typing import List, Dict
from tracezero.utils.logger import app_logger

# Standard startup locations
STARTUP_KEYS = [
    (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
    (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
]

def get_startup_apps() -> List[Dict]:
    """Retrieve all standard startup apps from the registry."""
    apps = []
    
    for hkey, subkey in STARTUP_KEYS:
        try:
            with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_READ) as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        apps.append({
                            "name": name,
                            "command": value,
                            "enabled": True,
                            "hkey": hkey,
                            "subkey": subkey
                        })
                        i += 1
                    except OSError:
                        break # No more values
        except Exception as e:
            app_logger.warning(f"Could not read startup key {subkey}: {e}")
            
    # Also read "Disabled" keys if we implemented custom tracking, but for now we will 
    # use a common trick: moving the disabled ones to a "Run_Disabled" key or similar,
    # or just checking the Task Manager's ApprovedStartupPage list.
    # To keep it safe and straightforward like PC Manager, we will just read/write from 
    # a custom "Run_Disabled" registry path if they disable it via TraceZero.
    
    for hkey, subkey in STARTUP_KEYS:
        disabled_subkey = subkey + "_Disabled"
        try:
            with winreg.OpenKey(hkey, disabled_subkey, 0, winreg.KEY_READ) as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        apps.append({
                            "name": name,
                            "command": value,
                            "enabled": False,
                            "hkey": hkey,
                            "subkey": subkey # Original subkey
                        })
                        i += 1
                    except OSError:
                        break
        except FileNotFoundError:
            pass # No disabled key exists yet
            
    return apps

def toggle_startup_app(app: Dict, enable: bool) -> bool:
    """Enable or disable a startup app."""
    hkey = app["hkey"]
    orig_subkey = app["subkey"]
    disabled_subkey = orig_subkey + "_Disabled"
    name = app["name"]
    command = app["command"]
    
    try:
        if enable:
            # Move from disabled to enabled
            with winreg.CreateKey(hkey, orig_subkey) as key:
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, command)
                
            try:
                with winreg.OpenKey(hkey, disabled_subkey, 0, winreg.KEY_SET_VALUE) as dkey:
                    winreg.DeleteValue(dkey, name)
            except Exception:
                pass
        else:
            # Move from enabled to disabled
            with winreg.CreateKey(hkey, disabled_subkey) as key:
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, command)
                
            try:
                with winreg.OpenKey(hkey, orig_subkey, 0, winreg.KEY_SET_VALUE) as ekey:
                    winreg.DeleteValue(ekey, name)
            except Exception:
                pass
                
        app_logger.info(f"{'Enabled' if enable else 'Disabled'} startup app: {name}")
        return True
    except Exception as e:
        app_logger.error(f"Failed to toggle startup app {name}: {e}")
        return False
