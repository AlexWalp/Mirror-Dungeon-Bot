# Burn
TEAMS = {
    "BURN": {
        "checks" : ["Burn", "smallBurn", (315, 370), "reBurn", "bigBurn"],
        "floors" : ["TheOutcast", "HellsChicken", "LCBRegularCheckup"],
        "uptie1" : ["hellterfly", "fiery"],
        "uptie2" : "glimpse",
        "goal"   : ["soothe"],
        "fuse1"  : {"stew": 2, "paraffin": 1}, # book
        "fuse2"  : {"book": None, "dust": 3, "ash": 1}, # soothe
        "buy"    : ["glimpse", "wing", "dust", "stew", "paraffin", "ash"], # order is important
        "all"    : ["glimpse", "dust", "stew", "paraffin", "ash", "book", "hellterfly", "fiery", "wing", "soothe"],
        "sin"    : True
    },

    # Bleed
    "BLEED": {
        "checks" : ["Bleed", "smallBleed", (535, 370), "reBleed", "bigBleed"],
        "floors" : ["FaithErosion", "TheOutcast", "HellsChicken"],
        "uptie1" : ["clerid"], # wolf
        "uptie2" : "redstained",
        "goal"   : ["redmist"],
        "fuse1"  : {"millarca": 2, "hymn": 1}, # devotion
        "fuse2"  : {"devotion": None, "smokeswires": 3, "muzzle": 1}, # redmist  
        "buy"    : ["redstained", "gossypium", "smokeswires", "millarca", "muzzle", "hymn", "contaminatedneedle", "fracturedblade", "scripture", "rustedknife"],
        "all"    : ["clerid", "wolf", "devotion", "redmist", "redstained", "gossypium", "smokeswires", "millarca", "muzzle", "hymn", "contaminatedneedle", "fracturedblade", "scripture", "rustedknife"],
        "sin"    : True
    },

    # Tremor
    "TREMOR": {
        "checks" : ["Tremor", "smallTremor", (755, 370), "reTremor", "bigTremor"],
        "floors" : ["SEA", "ACertainWorld"],
        "uptie1" : ["bracelet", "reverberation"],
        "uptie2" : "downpour",
        "goal"   : ["oscillation"],
        "fuse1"  : {},
        "fuse2"  : {"truthbell": 3, "cogs": 2, "nixie": 1}, # oscillation    
        "buy"    : ["downpour", "truthbell", "cogs", "nixie", "synaesthesia", "spanner", "clockwork", "biovial", "eyeball"],
        "all"    : ["oscillation", "bracelet", "reverberation", "downpour", "truthbell", "cogs", "nixie", "synaesthesia", "spanner", "clockwork", "biovial", "eyeball"],
        "sin"    : True
    },

    # Rupture
    "RUPTURE": {
        "checks" : ["Rupture", "smallRupture", (975, 370), "reRupture", "bigRupture"],
        "floors" : ["TheOutcast", "HellsChicken", "LCBRegularCheckup"],
        "uptie1" : ["lamp"], # "thunderbranch" "lasso"
        "uptie2" : "thrill",
        "goal"   : ["trance"],
        "fuse1"  : {},
        "fuse2"  : {"battery": 3, "rope": 2, "bundle": 1}, # trance
        "buy"    : ["thrill", "breast", "thunderbranch", "battery", "rope", "bundle", "umbrella"],
        "all"    : ["thrill", "lasso", "lamp", "breast", "battery", "rope", "thunderbranch", "brooch", "bundle", "trance", "umbrella"],
        "sin"    : True
    },

    # Sinking
    "SINKING": {
        "checks" : ["Sinking", "smallSinking", (315, 665), "reSinking", "bigSinking"],
        "floors" : ["DregsoftheManor", "ACertainWorld"],
        "uptie1" : ["redorder"],
        "uptie2" : "artisticsense",
        "goal"   : ["musicsheet"],
        "fuse1"  : {},
        "fuse2"  : {"midwinter": 3, "tangledbones": 2, "headlessportrait": 1}, # musicsheet    
        "buy"    : ["musicsheet", "midwinter", "tangledbones", "headlessportrait", "compass", "crumbs"],
        "all"    : ["redorder", "meltedspring", "artisticsense", "musicsheet", "midwinter", "tangledbones", "headlessportrait", "compass", "crumbs"],
        "sin"    : True
    },

    # Poise
    "POISE": {
        "checks" : ["Poise", "smallPoise", (535, 665), "rePoise", "bigPoise"],
        "floors" : [],
        "uptie1" : ["stonetomb"], # holder
        "uptie2" : "clearmirror",
        "goal"   : ["luckypouch"],
        "fuse1"  : {"recollection": 2, "pendant": 1},
        "fuse2"  : {"reminiscence": None, "clover": 3, "horseshoe": 1}, # luckypouch  
        "buy"    : ["clearmirror", "nebulizer", "clover", "recollection", "pendant", "horseshoe", "bamboohat", "brokenblade", "finifugality"],
        "all"    : ["luckypouch", "stonetomb", "holder", "reminiscence", "clearmirror", "nebulizer", "clover", "recollection", "pendant", "horseshoe", "bamboohat", "brokenblade", "finifugality"],
        "sin"    : True
    },

    # Charge
    "CHARGE": {
        "checks" : ["Charge", "smallCharge", (755, 665), "reCharge", "bigCharge"],
        "floors" : ["HellsChicken"],
        "uptie1" : ["employeecard", "batterysocket"],
        "uptie2" : "gloves",
        "goal"   : ["T-1"],
        "fuse1"  : {},
        "fuse2"  : {"forcefield": 3, "bolt": 2, "wristguards": 1}, # T-1      
        "buy"    : ["gloves", "forcefield", "bolt", "wristguards", "imitativegenerator", "vitae"],
        "all"    : ["employeecard", "batterysocket", "T-1", "gloves", "forcefield", "bolt", "wristguards", "imitativegenerator", "vitae"],
        "sin"    : True
    },

    "SLASH": {
        "checks" : ["Slash", "smallSlash", (975, 665), "reSlash", "bigSlash"],
        "floors" : [],
        "uptie1" : ["shortcane"],
        "uptie2" : "slashmemory",
        "goal"   : [],
        "fuse1"  : {},
        "fuse2"  : {},
        "buy"    : ["slashmemory"],
        "all"    : ["shortcane", "slashmemory"],
        "sin"    : False
    },

    "PIERCE": {
        "checks" : ["Pierce", "smallPierce", (315, 840), "rePierce", "bigPierce"],
        "floors" : [],
        "uptie1" : ["plumeproof"],
        "uptie2" : "piercememory",
        "goal"   : [],
        "fuse1"  : {},
        "fuse2"  : {},
        "buy"    : ["piercememory"],
        "all"    : ["plumeproof", "piercememory"],
        "sin"    : False
    },

    "BLUNT": {
        "checks" : ["Blunt", "smallBlunt", (535, 840), "reBlunt", "bigBlunt"],
        "floors" : [],
        "uptie1" : [],
        "uptie2" : "bluntmemory",
        "goal"   : [],
        "fuse1"  : {},
        "fuse2"  : {},
        "buy"    : ["bluntmemory"],
        "all"    : ["bluntmemory"],
        "sin"    : False
    },
}

# HARDMODE
HARD = {
    "BURN": {
        "checks" : ["Burn", "smallBurn", (315, 370), "reBurn", "bigBurn"],
        "floors" : ["TheOutcast", "HellsChicken", "LCBRegularCheckup"],
        "uptie1" : ["hellterfly", "fiery"],
        "uptie2" : "glimpse",
        "goal"   : ["soothe", "purloinedflame"],
        "fuse1"  : {"stew": 2, "paraffin": 1}, # book
        "fuse2"  : {"book": None, "dust": 3, "ash": 1}, # soothe

        "fuse3"  : {},
        "fuse4"  : {"disk": 3, "hearthflame": 2, "intellect": 1}, # purloinedflame

        "buy"    : ["glimpse", "wing", "dust", "stew", "paraffin", "ash", "disk", "hearthflame", "intellect"], # order is important
        "all"    : ["glimpse", "dust", "stew", "paraffin", "ash", "book", "hellterfly", "fiery", "wing", "soothe",
                    "purloinedflame", "disk", "hearthflame", "intellect"],
        "sin"    : True
    },

    # Bleed
    "BLEED": {
        "checks" : ["Bleed", "smallBleed", (535, 370), "reBleed", "bigBleed"],
        "floors" : ["FaithErosion", "TheOutcast", "HellsChicken"],
        "uptie1" : ["clerid"], # wolf
        "uptie2" : "redstained",
        "goal"   : ["redmist", "hemorrhagicshock"],
        "fuse1"  : {"millarca": 2, "hymn": 1}, # devotion
        "fuse2"  : {"devotion": None, "smokeswires": 3, "muzzle": 1}, # redmist

        "fuse3"  : {},
        "fuse4"  : {"bloodsack": 3, "rustedknife": 3, "ironstake": 1}, # hemorrhagicshock

        "buy"    : ["redstained", "gossypium", "smokeswires", "millarca", "muzzle", "hymn", "bloodsack", "rustedknife", "ironstake", "contaminatedneedle", "fracturedblade", "scripture"],
        "all"    : ["clerid", "wolf", "devotion", "redmist", "redstained", "gossypium", "smokeswires", "millarca", "muzzle", "hymn", "contaminatedneedle", 
                    "fracturedblade", "scripture", "hemorrhagicshock", "rustedknife", "bloodsack", "ironstake"],
        "sin"    : True
    },

    # Tremor
    "TREMOR": {
        "checks" : ["Tremor", "smallTremor", (755, 370), "reTremor", "bigTremor"],
        "floors" : ["SEA", "ACertainWorld"],
        "uptie1" : ["bracelet", "reverberation"],
        "uptie2" : "downpour",
        "goal"   : ["oscillation", "vibrobell"],
        "fuse1"  : {},
        "fuse2"  : {"truthbell": 3, "cogs": 2, "nixie": 1}, # oscillation

        "fuse3"  : {"wobblingkeg": 2, "gemstone": 1}, # epicenter
        "fuse4"  : {"epicenter": None, "clockwork": 3, "venomousskin": 1}, # vibrobell

        "buy"    : ["downpour", "truthbell", "cogs", "nixie", "clockwork", "wobblingkeg", "gemstone", "venomousskin", "synaesthesia", "spanner", "biovial", "eyeball"],
        "all"    : ["oscillation", "bracelet", "reverberation", "downpour", "truthbell", "cogs", "nixie", "synaesthesia", "spanner", 
                    "clockwork", "biovial", "eyeball", "vibrobell", "epicenter", "venomousskin", "wobblingkeg", "gemstone"],
        "sin"    : True
    },

    # Rupture
    "RUPTURE": {
        "checks" : ["Rupture", "smallRupture", (975, 370), "reRupture", "bigRupture"],
        "floors" : ["TheOutcast", "HellsChicken", "LCBRegularCheckup"],
        "uptie1" : ["lamp"], # "thunderbranch" "lasso"
        "uptie2" : "thrill",
        "goal"   : ["trance", "ruin"],
        "fuse1"  : {},
        "fuse2"  : {"battery": 3, "rope": 2, "bundle": 1}, # trance
        
        "fuse3"  : {"apocalypse": 2, "bonestake": 1}, # effigy
        "fuse4"  : {"effigy": None, "thunderbranch": 3, "gun": 1}, # ruin

        "buy"    : ["thrill", "breast", "thunderbranch", "battery", "rope", "apocalypse", "bundle", "bonestake", "gun", "umbrella"],
        "all"    : ["thrill", "lasso", "lamp", "breast", "battery", "rope", "thunderbranch", "brooch", "bundle", "trance", "umbrella",
                    "ruin", "effigy", "gun", "apocalypse", "bonestake"],
        "sin"    : True
    },

    # Sinking
    "SINKING": {
        "checks" : ["Sinking", "smallSinking", (315, 665), "reSinking", "bigSinking"],
        "floors" : ["DregsoftheManor", "ACertainWorld"],
        "uptie1" : ["redorder"],
        "uptie2" : "artisticsense",
        "goal"   : ["musicsheet", "wave"],
        "fuse1"  : {},
        "fuse2"  : {"midwinter": 3, "tangledbones": 2, "headlessportrait": 1}, # musicsheet

        "fuse3"  : {"overcoat": 2, "cantabile": 1},
        "fuse4"  : {"globe": None, "distantstar": 3, "thornypath": 1}, # wave

        "buy"    : ["musicsheet", "midwinter", "tangledbones", "headlessportrait", "distantstar", "overcoat", "cantabile", "thornypath", "compass", "crumbs"],
        "all"    : ["redorder", "meltedspring", "artisticsense", "musicsheet", "midwinter", "tangledbones", "headlessportrait", "compass", "crumbs",
                    "wave", "globe", "distantstar", "thornypath", "overcoat", "cantabile"],
        "sin"    : True
    },

    # Poise
    "POISE": {
        "checks" : ["Poise", "smallPoise", (535, 665), "rePoise", "bigPoise"],
        "floors" : [],
        "uptie1" : ["stonetomb"], # holder
        "uptie2" : "clearmirror",
        "goal"   : ["luckypouch", "spirits"],
        "fuse1"  : {"recollection": 2, "pendant": 1},
        "fuse2"  : {"reminiscence": None, "clover": 3, "horseshoe": 1}, # luckypouch

        "fuse3"  : {},
        "fuse4"  : {"endorphinkit": 3, "angel": 2, "devil": 1}, # spirits

        "buy"    : ["clearmirror", "nebulizer", "clover", "recollection", "pendant", "horseshoe", "endorphinkit", "angel", "devil", "bamboohat", "brokenblade", "finifugality"],
        "all"    : ["luckypouch", "stonetomb", "holder", "reminiscence", "clearmirror", "nebulizer", "clover", "recollection", "pendant", 
                    "horseshoe", "bamboohat", "brokenblade", "finifugality", "spirits", "endorphinkit", "angel", "devil"],
        "sin"    : True
    },

    # Charge
    "CHARGE": {
        "checks" : ["Charge", "smallCharge", (755, 665), "reCharge", "bigCharge"],
        "floors" : ["HellsChicken"],
        "uptie1" : ["employeecard", "batterysocket"],
        "uptie2" : "gloves",
        "goal"   : ["T-1", "T-5"],
        "fuse1"  : {},
        "fuse2"  : {"forcefield": 3, "bolt": 2, "wristguards": 1}, # T-1

        "fuse3"  : {"minitelepole": 2, "UPS": 1}, # insulator
        "fuse4"  : {"insulator": None, "rod": 3, "vitae": 1}, # T-5

        "buy"    : ["gloves", "forcefield", "bolt", "wristguards", "minitelepole", "rod", "vitae", "UPS", "imitativegenerator"],
        "all"    : ["employeecard", "batterysocket", "T-1", "gloves", "forcefield", "bolt", "wristguards", "imitativegenerator",
                    "T-5", "insulator", "rod", "vitae", "minitelepole", "UPS"],
        "sin"    : True
    },

    "SLASH": {
        "checks" : ["Slash", "smallSlash", (975, 665), "reSlash", "bigSlash"],
        "floors" : [],
        "uptie1" : ["shortcane"],
        "uptie2" : "slashmemory",
        "goal"   : [],
        "fuse1"  : {},
        "fuse2"  : {},
        "fuse3"  : {},
        "fuse4"  : {},
        "buy"    : ["slashmemory"],
        "all"    : ["shortcane", "slashmemory"],
        "sin"    : False
    },

    "PIERCE": {
        "checks" : ["Pierce", "smallPierce", (315, 840), "rePierce", "bigPierce"],
        "floors" : [],
        "uptie1" : ["plumeproof"],
        "uptie2" : "piercememory",
        "goal"   : [],
        "fuse1"  : {},
        "fuse2"  : {},
        "fuse3"  : {},
        "fuse4"  : {},
        "buy"    : ["piercememory"],
        "all"    : ["plumeproof", "piercememory"],
        "sin"    : False
    },

    "BLUNT": {
        "checks" : ["Blunt", "smallBlunt", (535, 840), "reBlunt", "bigBlunt"],
        "floors" : [],
        "uptie1" : [],
        "uptie2" : "bluntmemory",
        "goal"   : [],
        "fuse1"  : {},
        "fuse2"  : {},
        "fuse3"  : {},
        "fuse4"  : {},
        "buy"    : ["bluntmemory"],
        "all"    : ["bluntmemory"],
        "sin"    : False
    },
}

# from utils.paths import PTH
# for team in HARD.keys():
#     for gift in HARD[team]["all"]:
#         print(PTH[gift])