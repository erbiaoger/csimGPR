# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['__main__.py'],
    pathex=['csimGPR/csimGPR.py', 'csimGPR/csimGPRGUI.py'],
    binaries=[],
    datas=[('csimGPR/startGUIdat/*', 'csimGPR/startGUIdat/'), ('/Users/zhiyuzhang/miniconda3/lib/python3.10/site-packages/Pmw', 'Pmw')],
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['csimGPR/startGUIdat/AnyConv.com__csimGPR_logo.icns'],
)
app = BUNDLE(
    exe,
    name='csimGPRapp.app',
    icon='csimGPR/startGUIdat/AnyConv.com__csimGPR_logo.icns',
    bundle_identifier=None,
)
