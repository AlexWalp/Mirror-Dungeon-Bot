# Burn
TEAMS = {
    "BURN": {
        "checks" : ["Burn", "BurnShop", "BurnStart", "reBurn"],
        "floor1" : ["Outcast", "Gamblers"],
        "floor2" : ["Chicken"],
        "floor3" : [],
        "floor4" : [],
        "floor5" : [], # lcb checkup (optional)
        "uptie1" : ["hellterfly", "fiery"],
        "uptie2" : "glimpse",
        "goal"   : "soothe",
        "fuse1"  : {"stew": 2, "paraffin": 1}, # book
        "fuse2"  : {"book": None, "dust": 3, "ash": 1}, # soothe
        "buy"    : ["glimpse", "wing", "dust", "stew", "paraffin", "ash"], # order is important
        "all"    : ["glimpse", "dust", "stew", "paraffin", "ash", "book", "hellterfly", "fiery", "wing", "soothe"],
        "useless": "stone0",
    },

    # Rupture
    "RUPTURE": {
        "checks" : ["Rupture", "RuptureShop", "RuptureStart", "reRupture"],
        "floor1" : ["Outcast"],
        "floor2" : ["Chicken"],
        "floor3" : [],
        "floor4" : [],
        "floor5" : [], # lcb checkup (optional)
        "uptie1" : ["lamp"], # "thunderbranch" "lasso"
        "uptie2" : "thrill",
        "goal"   : "trance",
        "buy"    : ["thrill", "breast", "battery", "rope", "thunderbranch", "bundle"],
        "all"    : ["thrill", "lasso", "lamp", "breast", "battery", "rope", "thunderbranch", "brooch", "bundle", "trance"],
        "fuse1"  : [],
        "fuse2"  : ["battery", "rope", "bundle"], # trance
        "useless": "stone1",
    },

    # Bleed
    "BLEED": {
        "checks" : ["Bleed", "BleedShop", "BleedStart", "reBleed"],
        "floor1" : ["Outcast"],
        "floor2" : ["Chicken"],
        "floor3" : [],
        "floor4" : [],
        "floor5" : [], # lcb checkup (optional)
        "uptie1" : ["lasso", "lamp", "thunderbranch"],
        "uptie2" : "thrill",
        "goal"   : "soothe",
        "buy"    : ["thrill", "breast", "battery", "rope", "thunderbranch", "bundle"],
        "all"    : ["thrill", "lasso", "lamp", "breast", "battery", "rope", "thunderbranch", "brooch", "bundle", "trance"],
        "fuse1"  : [],
        "fuse2"  : ["battery", "rope", "bundle"], # trance
        "useless": "stone2",
    },

    # Poise
    "POISE": {
        "checks" : ["Poise", "PoiseShop", "PoiseStart", "rePoise"],
        "floor1" : ["Outcast"],
        "floor2" : ["Chicken"],
        "floor3" : [],
        "floor4" : [],
        "floor5" : [], # lcb checkup (optional)
        "uptie1" : ["lasso", "lamp", "thunderbranch"],
        "uptie2" : "thrill",
        "goal"   : "soothe",
        "buy"    : ["thrill", "breast", "battery", "rope", "thunderbranch", "bundle"],
        "all"    : ["thrill", "lasso", "lamp", "breast", "battery", "rope", "thunderbranch", "brooch", "bundle", "trance"],
        "fuse1"  : [],
        "fuse2"  : ["battery", "rope", "bundle"], # trance
        "useless": "stone3",
    },

    # Charge
    "CHARGE": {
        "checks" : ["Charge", "ChargeShop", "ChargeStart", "reCharge"],
        "floor1" : ["Outcast"],
        "floor2" : ["Chicken"],
        "floor3" : [],
        "floor4" : [],
        "floor5" : [], # lcb checkup (optional)
        "uptie1" : ["lasso", "lamp", "thunderbranch"],
        "uptie2" : "thrill",
        "goal"   : "soothe",
        "buy"    : ["thrill", "breast", "battery", "rope", "thunderbranch", "bundle"],
        "all"    : ["thrill", "lasso", "lamp", "breast", "battery", "rope", "thunderbranch", "brooch", "bundle", "trance"],
        "fuse1"  : [],
        "fuse2"  : ["battery", "rope", "bundle"], # trance
        "useless": "stone4",
    },

    # Sinking
    "SINKING": {
        "checks" : ["Sinking", "SinkingShop", "SinkingStart", "reSinking"],
        "floor1" : ["Outcast"],
        "floor2" : ["Chicken"],
        "floor3" : [],
        "floor4" : [],
        "floor5" : [], # lcb checkup (optional)
        "uptie1" : ["lasso", "lamp", "thunderbranch"],
        "uptie2" : "thrill",
        "goal"   : "soothe",
        "buy"    : ["thrill", "breast", "battery", "rope", "thunderbranch", "bundle"],
        "all"    : ["thrill", "lasso", "lamp", "breast", "battery", "rope", "thunderbranch", "brooch", "bundle", "trance"],
        "fuse1"  : [],
        "fuse2"  : ["battery", "rope", "bundle"], # trance
        "useless": "stone5",
    },

    # Tremor
    "TREMOR": {
        "checks" : ["Tremor", "TremorShop", "TremorStart", "reTremor"],
        "floor1" : ["Outcast"],
        "floor2" : ["Chicken"],
        "floor3" : [],
        "floor4" : [],
        "floor5" : [], # lcb checkup (optional)
        "uptie1" : ["lasso", "lamp", "thunderbranch"],
        "uptie2" : "thrill",
        "goal"   : "soothe",
        "buy"    : ["thrill", "breast", "battery", "rope", "thunderbranch", "bundle"],
        "all"    : ["thrill", "lasso", "lamp", "breast", "battery", "rope", "thunderbranch", "brooch", "bundle", "trance"],
        "fuse1"  : [],
        "fuse2"  : ["battery", "rope", "bundle"], # trance
        "useless": "stone6",
    }
}