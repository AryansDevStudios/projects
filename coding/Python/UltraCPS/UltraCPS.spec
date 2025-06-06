# -*- mode: python ; coding: utf-8 -*-
import os

project_path = os.path.abspath(os.getcwd())

a = Analysis(
    ['main.py'],
    pathex=[project_path],
    binaries=[],
    datas=[
        (r"D:\coding\Python\UltraCPS\assets", "assets"),
        (r"D:\coding\Python\UltraCPS\LICENSE.txt", "."),
        (r"D:\coding\Python\UltraCPS\README.md", "."),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries + a.datas,  # include all assets inside exe
    exclude_binaries=False,  # now include binaries
    name='UltraCPS',
    icon=os.path.join(project_path, "assets", "iconMain.ico"),
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='UltraCPS.ver',
)
