"""
utils/constants.py  — TraceZero
Defines all safe paths, forbidden zones, and application-wide constants.
"""

import os
from pathlib import Path

# ─────────────────────────────────────────────
#  FORBIDDEN PATHS - NEVER SCAN OR DELETE THESE
# ─────────────────────────────────────────────
FORBIDDEN_PATHS = [
    r"C:\Windows",
    r"C:\Windows\System32",
    r"C:\Windows\SysWOW64",
    r"C:\Windows\WinSxS",
    r"C:\Recovery",
    r"C:\Boot",
    r"C:\System Volume Information",
    r"C:\EFI",
    r"C:\$Recycle.Bin",
    r"C:\$WinREAgent",
    r"C:\PerfLogs",
]
FORBIDDEN_PATHS_NORMALIZED = [p.lower() for p in FORBIDDEN_PATHS]

FORBIDDEN_PATH_KEYWORDS = [
    "windows\\system32",
    "windows\\syswow64",
    "windows\\winsxs",
    "system volume information",
    "\\drivers\\",
    "\\driver store\\",
    "\\winsxs\\",
    "\\microsoft.net\\",
    "\\microsoft\\net framework",
    "\\windows\\",
    "\\recovery\\",
    "\\boot\\",
]

PROTECTED_KEYWORDS = [
    "microsoft visual c++",
    "microsoft visual c runtime",
    "vcredist",
    "vc_redist",
    "java runtime",
    "java development kit",
    "jdk",
    "jre",
    "directx",
    ".net framework",
    "dotnet",
    "windows sdk",
    "windows kits",
    "driver",
    "dxsetup",
    "openal",
    "physx",
    "xna framework",
    "windows media player",
    "windows update",
    "windows defender",
    "microsoft edge",
    "microsoft onedrive",
    "wer ",
    "winre",
]

# ─────────────────────────────────────────────
#  SCAN TARGET PATHS
# ─────────────────────────────────────────────
USER_HOME = Path.home()
USERNAME = os.environ.get("USERNAME", "User")

SCAN_PATHS = {
    "program_files": [
        Path(r"C:\Program Files"),
        Path(r"C:\Program Files (x86)"),
    ],
    "appdata": [
        USER_HOME / "AppData" / "Local",
        USER_HOME / "AppData" / "Roaming",
        USER_HOME / "AppData" / "LocalLow",
    ],
    "programdata": [
        Path(r"C:\ProgramData"),
    ],
    "temp": [
        Path(os.environ.get("TEMP", r"C:\Windows\Temp")),
        Path(os.environ.get("TMP", r"C:\Windows\Temp")),
    ],
}

REGISTRY_SCAN_PATHS = {
    "uninstall_hklm":     r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    "uninstall_hklm_wow": r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    "uninstall_hkcu":     r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    "software_hkcu":      r"SOFTWARE",
    "software_hklm":      r"SOFTWARE",
}

CACHE_EXTENSIONS      = {".cache", ".tmp", ".temp", ".bak", ".old", ".crdownload", ".part"}
LOG_EXTENSIONS        = {".log", ".log1", ".log2", ".dmp", ".mdmp", ".wer"}
CRASH_DUMP_EXTENSIONS = {".dmp", ".mdmp", ".hdmp", ".stackdump"}

UPDATE_RESIDUE_PATTERNS = ["$~", "~$", ".old", "_backup", "_old", "uninstall", "uninst"]

SHORTCUT_LOCATIONS = [
    USER_HOME / "Desktop",
    USER_HOME / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs",
    Path(r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs"),
    Path(r"C:\Users\Public\Desktop"),
]

# ─────────────────────────────────────────────
#  DATABASE / LOGGING
# ─────────────────────────────────────────────
APP_DATA_DIR   = USER_HOME / "AppData" / "Local" / "TraceZero"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_PATH  = APP_DATA_DIR / "tracezero.db"
LOG_FILE_PATH  = APP_DATA_DIR / "tracezero.log"

# ─────────────────────────────────────────────
#  RISK LEVELS
# ─────────────────────────────────────────────
RISK_SAFE   = "Safe"
RISK_REVIEW = "Review"
RISK_RISKY  = "Risky"

RISK_COLORS = {
    RISK_SAFE:   "#3fb950",
    RISK_REVIEW: "#e3b341",
    RISK_RISKY:  "#f85149",
}

# ─────────────────────────────────────────────
#  UI THEME COLORS  — Windows 11 Blue (dark defaults)
# ─────────────────────────────────────────────
COLOR_BG_DARK      = "#111111"
COLOR_BG_CARD      = "#1c1c1c"
COLOR_BG_PANEL     = "#242424"
COLOR_ACCENT       = "#0078d4"   # windows blue
COLOR_ACCENT_GREEN = "#107c10"
COLOR_ACCENT_RED   = "#e81123"
COLOR_ACCENT_ORANGE= "#f7630c"
COLOR_TEXT_PRIMARY = "#ffffff"
COLOR_TEXT_SECONDARY="#cccccc"
COLOR_BORDER       = "#333333"
COLOR_HOVER        = "#2d2d2d"

# Risk level color map (used in scanner + UI)
RISK_COLORS = {"Safe": "#107c10", "Review": "#f7630c", "Risky": "#e81123"}

# ─────────────────────────────────────────────
#  SCANNER CONFIG
# ─────────────────────────────────────────────
MAX_SCAN_THREADS     = 4
MAX_SCAN_DEPTH       = 6
LARGE_FILE_THRESHOLD = 100 * 1024 * 1024
OLD_FILE_DAYS        = 90

APP_NAME    = "TraceZero"
APP_VERSION = "1.0.0"
APP_TAGLINE = "Smart TraceZero for Windows"
