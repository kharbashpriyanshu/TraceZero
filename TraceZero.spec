# TraceZero.spec
# PyInstaller spec file for packaging TraceZero v1.0.0 as a standalone EXE
#
# Usage:
#   pyinstaller TraceZero.spec --clean

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # Include the entire tracezero package
        ('tracezero', 'tracezero'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
        # PyQt6
        'PyQt6',
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.sip',
        # SQLAlchemy
        'sqlalchemy',
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.dialects.sqlite.pysqlite',
        'sqlalchemy.orm',
        'sqlalchemy.pool',
        'sqlalchemy.event',
        'sqlalchemy.sql.default_comparator',
        # Windows
        'win32com.client',
        'win32com',
        'win32api',
        'win32con',
        'winreg',
        'pywintypes',
        # Other deps
        'send2trash',
        'psutil',
        'colorlog',
        'humanize',
        # TraceZero internal
        'tracezero.utils.config',
        'tracezero.utils.constants',
        'tracezero.utils.helpers',
        'tracezero.utils.logger',
        'tracezero.utils.recycle_bin',
        'tracezero.utils.pc_boost',
        'tracezero.ui.styles',
        'tracezero.ui.main_window',
        'tracezero.ui.dashboard_page',
        'tracezero.ui.scan_page',
        'tracezero.ui.settings_page',
        'tracezero.ui.history_page',
        'tracezero.ui.startup_page',
        'tracezero.scanner.scan_engine',
        'tracezero.scanner.file_scanner',
        'tracezero.registry.registry_reader',
        'tracezero.registry.package_managers',
        'tracezero.registry.startup_manager',
        'tracezero.analyzer.risk_analyzer',
        'tracezero.database.db_manager',
        'tracezero.database.models',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter', 'matplotlib', 'numpy', 'scipy',
        'PIL', 'cv2', 'tensorflow', 'torch',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TraceZero',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # No console window — windowed GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
    version_info={
        'version': (1, 0, 0, 0),
        'description': 'TraceZero — Safe Windows Trace Cleaner',
        'company': '',
        'product': 'TraceZero',
        'copyright': '2025 TraceZero',
    } if False else None,   # Set to True and fill in to embed version info
)
