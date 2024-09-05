# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/tel', 'tel'),
        ('src/ui', 'ui'),
        ('src/backend', 'backend'),
        ('src/util.py', '.'),
    ],
    hiddenimports=[
        'ujson',
        'pytz',
        'tzlocal',
        'PySide6.QtWidgets',
        'PySide6.QtGui',
        'PySide6.QtCore',
        'PySide6.QtUiTools',
        'telethon',
        'telethon.errors',
        'telethon.tl.types',
        'telethon.utils',
        'sqlalchemy.orm',
        'tel',
        'backend',
        'ui.page',
        'ui.signal.Signal',
        'ui.component',
        'backend.models',
        'backend.views',
        'backend.db',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TgiTol',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # 如果是纯GUI应用，可以设置为False
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TgiTol',
)
