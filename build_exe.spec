# -*- mode: python ; coding: utf-8 -*-

import os
from glob import glob

def collect(src_dir, dst_dir, patterns=("*.png", "*.ttf", "*.ico")):
    files = []
    for pat in patterns:
        files += [(f, dst_dir) for f in glob(os.path.join(src_dir, pat))]
    return files


datas = []
datas += [('app_icon.ico', '.')]

datas += collect('ImageAssets/UI', 'ImageAssets/UI')

datas += collect('ImageAssets/UI/lux', 'ImageAssets/UI/lux')
datas += collect('ImageAssets/UI/lux/select', 'ImageAssets/UI/lux/select')

datas += collect('ImageAssets/UI/pack', 'ImageAssets/UI/pack')
datas += collect('ImageAssets/UI/pack/easy', 'ImageAssets/UI/pack/easy')
datas += collect('ImageAssets/UI/pack/hard', 'ImageAssets/UI/pack/hard')
datas += collect('ImageAssets/UI/pack/level', 'ImageAssets/UI/pack/level')

datas += collect('ImageAssets/UI/battle', 'ImageAssets/UI/battle')
datas += collect('ImageAssets/UI/battle/ego', 'ImageAssets/UI/battle/ego')
datas += collect('ImageAssets/UI/battle/sins', 'ImageAssets/UI/battle/sins')

datas += collect('ImageAssets/UI/end', 'ImageAssets/UI/end')
datas += collect('ImageAssets/UI/event', 'ImageAssets/UI/event')
datas += collect('ImageAssets/UI/event/sinprob', 'ImageAssets/UI/event/sinprob')
datas += collect('ImageAssets/UI/event/favorite', 'ImageAssets/UI/event/favorite')
datas += collect('ImageAssets/UI/event/teams', 'ImageAssets/UI/event/teams')

datas += collect('ImageAssets/UI/grab', 'ImageAssets/UI/grab')
datas += collect('ImageAssets/UI/grab/card', 'ImageAssets/UI/grab/card')
datas += collect('ImageAssets/UI/grab/levels', 'ImageAssets/UI/grab/levels')
datas += collect('ImageAssets/UI/grab/buffs', 'ImageAssets/UI/grab/buffs')

datas += collect('ImageAssets/UI/move', 'ImageAssets/UI/move')
datas += collect('ImageAssets/UI/shop', 'ImageAssets/UI/shop')
datas += collect('ImageAssets/UI/start', 'ImageAssets/UI/start')

datas += collect('ImageAssets/UI/shop/buy', 'ImageAssets/UI/shop/buy')
datas += collect('ImageAssets/UI/shop/fuse', 'ImageAssets/UI/shop/fuse')
datas += collect('ImageAssets/UI/shop/cost', 'ImageAssets/UI/shop/cost')
datas += collect('ImageAssets/UI/shop/skill3', 'ImageAssets/UI/shop/skill3')

teams = [
    "Keywordless", "Bleed", "Burn", "Charge", "Poise",
    "Rupture", "Sinking", "Tremor", "Slash", "Pierce", "Blunt"
]

for team in teams:
    base = f"ImageAssets/UI/teams/{team}"
    datas += collect(base, base)
    datas += collect(f"{base}/gifts", f"{base}/gifts")
    datas += collect(f"{base}/select", f"{base}/select")

datas += collect('ImageAssets/AppUI', 'ImageAssets/AppUI')
datas += collect('ImageAssets/AppUI/font', 'ImageAssets/AppUI/font', patterns=("*.ttf",))
datas += collect('ImageAssets/AppUI/affinity', 'ImageAssets/AppUI/affinity')
datas += collect('ImageAssets/AppUI/selected', 'ImageAssets/AppUI/selected')


a = Analysis(
    ['App.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["source.utils.os_x11_backend"],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['app_icon.ico'],
)
