# TraceZero ⚡

> **Smart TraceZero for Windows**

TraceZero detects and safely removes leftover files, folders, cache, logs, registry traces, and temporary files left behind by uninstalled or unused applications — all with a beautiful dark-themed desktop UI.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)
![PyQt6](https://img.shields.io/badge/UI-PyQt6-41CD52?style=flat-square&logo=qt)
![SQLite](https://img.shields.io/badge/DB-SQLite-003B57?style=flat-square&logo=sqlite)
![Windows](https://img.shields.io/badge/Platform-Windows-0078D6?style=flat-square&logo=windows)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Deep Scan** | AppData, Program Files, ProgramData, TEMP, Registry |
| 🛡 **100% Safe** | All deletions go to Recycle Bin — never permanent |
| 🧠 **Risk Analysis** | Classifies every item as Safe / Review / Risky |
| 🗝 **Registry Scanner** | Detects orphaned registry keys from removed apps |
| 🔗 **Shortcut Finder** | Finds dead .lnk files on Desktop & Start Menu |
| 🎮 **Game Stores** | Steam, Epic Games, Winget, Chocolatey detection |
| 📋 **Audit Trail** | Full scan + deletion history in SQLite database |
| ⏸ **Pause/Resume** | Scan can be paused and resumed mid-flight |
| ↩ **Undo** | Restore deleted items from Recycle Bin anytime |

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/kharbashpriyanshu/TraceZero.git
cd TraceZero

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python main.py
```

---

## 🏗 Project Structure

```
TraceZero/
├── tracezero/
│   ├── scanner/
│   │   ├── file_scanner.py       # Multithreaded filesystem scanner
│   │   └── scan_engine.py        # Orchestrates entire scan pipeline
│   ├── analyzer/
│   │   └── risk_analyzer.py      # AI-like risk classification engine
│   ├── registry/
│   │   ├── registry_reader.py    # Windows Registry reader
│   │   └── package_managers.py   # Winget/Chocolatey/Steam/Epic detection
│   ├── database/
│   │   ├── models.py             # SQLAlchemy ORM models
│   │   └── db_manager.py         # All CRUD operations
│   ├── ui/
│   │   ├── main_window.py        # Main application window
│   │   ├── dashboard_page.py     # Dashboard with stats + hero
│   │   ├── scan_page.py          # Scan, filter, delete UI
│   │   ├── history_page.py       # Scan & deletion history
│   │   ├── settings_page.py      # Config page
│   │   └── styles.py             # Dark premium stylesheet
│   └── utils/
│       ├── constants.py          # All safe/forbidden paths
│       ├── helpers.py            # Utility functions
│       ├── logger.py             # Rotating file logger
│       └── recycle_bin.py        # Safe deletion manager
├── tests/
│   └── test_safety.py            # Safety & unit tests
├── main.py                       # Entry point
├── requirements.txt
├── AppTraceCleaner.spec          # PyInstaller EXE config
└── README.md
```

---

## 🔒 Safety Design

### Protected System Paths (NEVER touched)

| Path | Reason |
|------|--------|
| `C:\Windows\*` | Core Windows OS |
| `C:\Windows\System32` | Critical system binaries |
| `C:\Windows\SysWOW64` | 32-bit compatibility layer |
| `C:\Windows\WinSxS` | Side-by-side component store |
| `C:\Recovery` | System recovery |
| `C:\Boot` | Bootloader |

### Protected Packages (NEVER deleted)

- ✅ Microsoft Visual C++ Redistributables
- ✅ .NET Framework / .NET Runtime
- ✅ Java Runtime Environment
- ✅ DirectX Runtime
- ✅ Windows Drivers & Driver Store
- ✅ OpenAL / PhysX / XNA

### Deletion Method

```python
import send2trash
send2trash.send2trash(path)   # Always uses Recycle Bin
```

No file is ever permanently deleted. Everything is recoverable.

---

## 📊 Scan Targets

| Category | Paths |
|----------|-------|
| Program Files | `C:\Program Files`, `C:\Program Files (x86)` |
| AppData | `%LOCALAPPDATA%`, `%APPDATA%`, `LocalLow` |
| Shared | `C:\ProgramData` |
| Temp | `%TEMP%`, `%TMP%` |
| Registry | `HKCU\SOFTWARE`, `HKLM\...\Uninstall` |
| Shortcuts | Desktop, Start Menu Programs |

---

## 🏷 Risk Levels

| Level | Indicator | Meaning |
|-------|-----------|---------|
| ✅ Safe | 🟢 Green | Cache, logs, temp — safe to remove |
| ⚠️ Review | 🟡 Amber | Needs manual check before deletion |
| ❌ Risky | 🔴 Red | Active app file / protected package — skip |

---

## 🗃 Database Schema

Stored at `%LOCALAPPDATA%\TraceZero\tracezero.db`

| Table | Purpose |
|-------|---------|
| `scan_sessions` | Each scan run with timestamps |
| `detected_items` | All leftover items per scan |
| `deleted_items` | Full deletion audit trail |
| `installed_apps` | Cached installed app list |

---

## 📦 Build Standalone EXE

```bash
pip install pyinstaller
pyinstaller AppTraceCleaner.spec
# Output: dist/AppTraceCleaner.exe
```

---

## 🧪 Run Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

---

## 🔄 Roadmap

- [x] Browser cache cleaning (Chrome, Firefox, Edge, Brave)
- [x] Startup apps manager
- [x] Duplicate file finder
- [x] Windows Core Cleanup (Deep OS cache: Prefetch, Windows Update)
- [x] Smart Uninstaller Module
- [x] Disk Space Visualizer (TreeSize / SpaceSniffer view)
- [x] Windows context menu integration
- [ ] Scheduled automatic background scans
- [ ] Multi-language support

---

## ⚠️ Disclaimer

TraceZero modifies your filesystem. Always review items before deleting. The author is not responsible for accidental removals — use the Recycle Bin restore feature if needed.

---

## 📄 License

MIT License — Free to use, modify, and distribute.

---

<p align="center">Made with ⚡ by <a href="https://github.com/kharbashpriyanshu">kharbashpriyanshu</a></p>
