# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Centralizador_links_youtube.py'],
    pathex=[],
    binaries=[],
    datas=[('icone/icone.ico', 'icone')],
    hiddenimports=[
        'kivymd.icon_definitions',
        'kivymd.uix.spinner',
        'kivymd.uix.spinner.spinner',
        'kivymd.uix.card',
        'kivymd.uix.button',
        'kivymd.uix.textfield',
        'kivymd.uix.dialog',
        'kivymd.app',
    ],
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
    a.binaries,
    a.datas,
    [],
    name='Centralizador_links_youtube',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icone/icone.ico',
    onefile=True 
)

coll = COLLECT(
    exe,
    Tree('icone'),
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Centralizador_links_youtube'
)
