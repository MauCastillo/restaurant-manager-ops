# -*- mode: python ; coding: utf-8 -*-
"""
HexOPS Manager - PyInstaller Specification for Windows 11
=========================================================
Para compilar en Windows 11, ejecuta:
    pyinstaller HexOPS.spec --clean
"""

import os
from pathlib import Path

block_cipher = None

a = Analysis(
    ['desktop_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('.env.example', '.'),
    ],
    hiddenimports=[
        'certifi',
        'ssl',
        'sqlite3',
        'urllib.request',
        'urllib.parse',
        'json',
        'base64',
        'flask',
        'dotenv',
        'webview',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='HexOPS_Manager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='static/img/icon.ico' if os.path.exists('static/img/icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='HexOPS_Manager',
)
