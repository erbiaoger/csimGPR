# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['__main__.py'],
    pathex=['csimGPR/csimGPR.py', 'csimGPR/csimGPRGUI.py'],
    binaries=[],
    datas=[('csimGPR/startGUIdat/*', 'csimGPR/startGUIdat/'), ('c:\\users\\zhangzhiyu\\miniconda3\\lib\\site-packages\\Pmw\\', 'Pmw'), ('examples\\*', 'examples/')],
    hiddenimports=['Pmw'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['__main__'],
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
    name='csimGPRapp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['csimGPR\\startGUIdat\\AnyConv.com__csimGPR_logo.icns'],
)
