# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Bot.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('ImageAssets\\UI\\*.png', 'ImageAssets\\UI'),
        ('ImageAssets\\UI\\battle\\*.png', 'ImageAssets\\UI\\battle'),
        ('ImageAssets\\UI\\battle\\sins\\*.png', 'ImageAssets\\UI\\battle\\sins'),
        ('ImageAssets\\UI\\end\\*.png', 'ImageAssets\\UI\\end'),
        ('ImageAssets\\UI\\event\\*.png', 'ImageAssets\\UI\\event'),
        ('ImageAssets\\UI\\event\\sinprob\\*.png', 'ImageAssets\\UI\\event\\sinprob'),
        ('ImageAssets\\UI\\grab\\*.png', 'ImageAssets\\UI\\grab'),
        ('ImageAssets\\UI\\grab\\card\\*.png', 'ImageAssets\\UI\\grab\\card'),
        ('ImageAssets\\UI\\grab\\levels\\*.png', 'ImageAssets\\UI\\grab\\levels'),
        ('ImageAssets\\UI\\pack\\*.png', 'ImageAssets\\UI\\pack'),
        ('ImageAssets\\UI\\move\\*.png', 'ImageAssets\\UI\\move'),
        ('ImageAssets\\UI\\shop\\*.png', 'ImageAssets\\UI\\shop'),
        ('ImageAssets\\UI\\start\\*.png', 'ImageAssets\\UI\\start'),
        ('ImageAssets\\UI\\teams\\Burn\\*.png', 'ImageAssets\\UI\\teams\\Burn'),
        ('ImageAssets\\UI\\teams\\Burn\\buy\\*.png', 'ImageAssets\\UI\\teams\\Burn\\buy'),
        ('ImageAssets\\UI\\teams\\Burn\\gifts\\*.png', 'ImageAssets\\UI\\teams\\Burn\\gifts')
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
    a.binaries,
    a.datas,
    [],
    name='CGrinder',
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
    icon=['app_icon.ico'],
)
