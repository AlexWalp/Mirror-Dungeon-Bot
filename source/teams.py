# Burn
TEAMS = {
    "BURN": {
        "checks" : ["Burn", "smallBurn", "BurnStart", "reBurn"],
        "floor1" : ["TheOutcast", "FlatbrokeGamblers"],
        "floor2" : ["HellsChicken"],
        "floor3" : [],
        "floor4" : [],
        "floor5" : ["LCBRegularCheckup"],
        "uptie1" : ["hellterfly", "fiery"],
        "uptie2" : "glimpse",
        "goal"   : "soothe",
        "fuse1"  : {"stew": 2, "paraffin": 1}, # book
        "fuse2"  : {"book": None, "dust": 3, "ash": 1}, # soothe
        "buy"    : ["glimpse", "wing", "dust", "stew", "paraffin", "ash"], # order is important
        "all"    : ["glimpse", "dust", "stew", "paraffin", "ash", "book", "hellterfly", "fiery", "wing", "soothe"],
    },

    # Bleed
    "BLEED": {
        "checks" : ["Bleed", "smallBleed", "BleedStart", "reBleed"],
        "floor1" : ["FaithErosion", "TheOutcast"],
        "floor2" : ["HellsChicken", "FaithErosion"],
        "floor3" : [],
        "floor4" : ["YieldMyFleshtoClaimTheirBones"],
        "floor5" : ["YieldMyFleshtoClaimTheirBones"],
        "uptie1" : ["clerid"], # wolf
        "uptie2" : "redstained",
        "goal"   : "redmist",
        "fuse1"  : {"millarca": 2, "hymn": 1}, # devotion
        "fuse2"  : {"devotion": None, "smokeswires": 3, "muzzle": 1}, # redmist  
        "buy"    : ["redstained", "gossypium", "smokeswires", "millarca", "muzzle", "hymn", "contaminatedneedle", "fracturedblade", "scripture", "rustedknife"],
        "all"    : ["clerid", "wolf", "devotion", "redmist", "redstained", "gossypium", "smokeswires", "millarca", "muzzle", "hymn", "contaminatedneedle", "fracturedblade", "scripture", "rustedknife"],
    },

    # Tremor
    "TREMOR": {
        "checks" : ["Tremor", "smallTremor", "TremorStart", "reTremor"],
        "floor1" : [],
        "floor2" : ["SEA"],
        "floor3" : [],
        "floor4" : ["ACertainWorld"],
        "floor5" : ["ACertainWorld"],
        "uptie1" : ["bracelet", "reverberation"],
        "uptie2" : "downpour",
        "goal"   : "oscillation",
        "fuse1"  : {},
        "fuse2"  : {"truthbell": 3, "cogs": 2, "nixie": 1}, # oscillation    
        "buy"    : ["downpour", "truthbell", "cogs", "nixie", "synaesthesia", "spanner", "clockwork", "biovial", "eyeball"],
        "all"    : ["oscillation", "bracelet", "reverberation", "downpour", "truthbell", "cogs", "nixie", "synaesthesia", "spanner", "clockwork", "biovial", "eyeball"],
    },

    # Rupture
    "RUPTURE": {
        "checks" : ["Rupture", "smallRupture", "RuptureStart", "reRupture"],
        "floor1" : ["TheOutcast"],
        "floor2" : ["HellsChicken"],
        "floor3" : [],
        "floor4" : [],
        "floor5" : ["LCBRegularCheckup"],
        "uptie1" : ["lamp"], # "thunderbranch" "lasso"
        "uptie2" : "thrill",
        "goal"   : "trance",
        "fuse1"  : {},
        "fuse2"  : {"battery": 3, "rope": 2, "bundle": 1}, # trance        
        "buy"    : ["thrill", "breast", "battery", "rope", "thunderbranch", "bundle"],
        "all"    : ["thrill", "lasso", "lamp", "breast", "battery", "rope", "thunderbranch", "brooch", "bundle", "trance"],
    },

    # Sinking
    "SINKING": {
        "checks" : ["Sinking", "smallSinking", "SinkingStart", "reSinking"],
        "floor1" : [],
        "floor2" : [],
        "floor3" : ["DregsoftheManor"],
        "floor4" : ["ACertainWorld"],
        "floor5" : ["ACertainWorld"],
        "uptie1" : ["redorder"],
        "uptie2" : "artisticsense",
        "goal"   : "musicsheet",
        "fuse1"  : {},
        "fuse2"  : {"midwinter": 3, "tangledbones": 2, "headlessportrait": 1}, # musicsheet    
        "buy"    : ["musicsheet", "midwinter", "tangledbones", "headlessportrait", "compass", "crumbs"],
        "all"    : ["redorder", "meltedspring", "artisticsense", "musicsheet", "midwinter", "tangledbones", "headlessportrait", "compass", "crumbs"],
    },

    # Poise
    "POISE": {
        "checks" : ["Poise", "smallPoise", "PoiseStart", "rePoise"],
        "floor1" : [],
        "floor2" : [],
        "floor3" : [],
        "floor4" : ["YieldMyFleshtoClaimTheirBones"],
        "floor5" : ["YieldMyFleshtoClaimTheirBones"],
        "uptie1" : ["stonetomb"], # holder
        "uptie2" : "clearmirror",
        "goal"   : "luckypouch",
        "fuse1"  : {"recollection": 2, "pendant": 1},
        "fuse2"  : {"reminiscence": None, "clover": 3, "horseshoe": 1}, # luckypouch  
        "buy"    : ["clearmirror", "nebulizer", "clover", "recollection", "pendant", "horseshoe", "bamboohat", "brokenblade", "finifugality"],
        "all"    : ["luckypouch", "stonetomb", "holder", "reminiscence", "clearmirror", "nebulizer", "clover", "recollection", "pendant", "horseshoe", "bamboohat", "brokenblade", "finifugality"],
    },

    # Charge
    "CHARGE": {
        "checks" : ["Charge", "smallCharge", "ChargeStart", "reCharge"],
        "floor1" : [],
        "floor2" : ["HellsChicken"],
        "floor3" : [],
        "floor4" : [],
        "floor5" : [],
        "uptie1" : ["employeecard", "batterysocket"],
        "uptie2" : "gloves",
        "goal"   : "T-1",
        "fuse1"  : {},
        "fuse2"  : {"forcefield": 3, "bolt": 2, "wristguards": 1}, # T-1      
        "buy"    : ["gloves", "forcefield", "bolt", "wristguards", "imitativegenerator", "vitae"],
        "all"    : ["employeecard", "batterysocket", "T-1", "gloves", "forcefield", "bolt", "wristguards", "imitativegenerator", "vitae"],
    },
}