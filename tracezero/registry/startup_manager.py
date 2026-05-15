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
        approved_subkey = r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
        
        try:
            with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_READ) as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        
                        # Default is enabled if not found in StartupApproved
                        enabled = True
                        try:
                            with winreg.OpenKey(hkey, approved_subkey, 0, winreg.KEY_READ) as app_key:
                                bin_val, val_type = winreg.QueryValueEx(app_key, name)
                                if val_type == winreg.REG_BINARY and len(bin_val) > 0:
                                    # Even number first byte = Enabled, Odd = Disabled
                                    if bin_val[0] % 2 != 0:
                                        enabled = False
                        except Exception:
                            pass
                            
                        apps.append({
                            "name": name,
                            "command": value,
                            "enabled": enabled,
                            "hkey": hkey,
                            "subkey": subkey,
                            "approved_subkey": approved_subkey
                        })
                        i += 1
                    except OSError:
                        break # No more values
        except Exception as e:
            app_logger.warning(f"Could not read startup key {subkey}: {e}")
            
    # Also support custom Run_Disabled fallback just in case they were moved
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
                            "subkey": subkey,
                            "approved_subkey": r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
                        })
                        i += 1
                    except OSError:
                        break
        except Exception:
            pass
            
    # Sort apps: Enabled first (False evaluates to 0 in sorting), then Disabled, then alphabetically
    apps.sort(key=lambda x: (not x["enabled"], x["name"].lower()))
    return apps

def toggle_startup_app(app: Dict, enable: bool) -> bool:
    """Enable or disable a startup app."""
    hkey = app["hkey"]
    name = app["name"]
    approved_subkey = app["approved_subkey"]
    
    try:
        # Write to StartupApproved/Run
        with winreg.CreateKey(hkey, approved_subkey) as key:
            # We need to read the existing binary or create a new one
            try:
                bin_val, val_type = winreg.QueryValueEx(key, name)
                bin_array = bytearray(bin_val)
            except Exception:
                # Default empty 12-byte array if missing
                # Task manager uses 12 bytes: e.g. 02 00 00 00 00 00 00 00 00 00 00 00
                bin_array = bytearray([0] * 12)
            
            # 0x02 is Enabled, 0x03 is Disabled.
            bin_array[0] = 0x02 if enable else 0x03
            
            winreg.SetValueEx(key, name, 0, winreg.REG_BINARY, bytes(bin_array))
            
        app_logger.info(f"{'Enabled' if enable else 'Disabled'} startup app: {name}")
        return True
    except Exception as e:
        app_logger.error(f"Failed to toggle startup app {name}: {e}")
        return False
