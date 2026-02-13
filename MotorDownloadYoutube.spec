# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['MotorDownloadYoutube.py'],
    pathex=[],
    binaries=[],
    datas=[('icone/youtube.ico', 'icone')],  
    hiddenimports=['yt_dlp', 'yt_dlp.extractor', 'yt_dlp.postprocessor'],  
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MotorDownloadYoutube',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='icone/youtube.ico'
)
