import os, sys

try:
    BASE_PATH = sys._MEIPASS
except:
    BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


ASSETS_DIR = os.path.join(BASE_PATH,"ImageAssets/UI")

def collect_png_paths(base_dir):
    path_dict = {}
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith(".png") or file.lower().endswith(".ttf"):
                name = os.path.splitext(file)[0]
                if name in path_dict:
                    raise ValueError(f"Duplicate image name detected: {name}")
                full_path = os.path.join(root, file).replace("\\", "/")
                path_dict[name] = full_path
    return path_dict

PTH = collect_png_paths(ASSETS_DIR)

# App.py assets
APP_DIR = os.path.join(BASE_PATH,"ImageAssets/AppUI")
APP_PTH = collect_png_paths(APP_DIR)
ICON = os.path.join(BASE_PATH,"app_icon.ico")

# regions for some buttons
REG = {
    # Bot.py
    "Drive"          : (1229,  896,  156,  139),
    "MD"             : ( 528,  354,  279,  196),
    "Start"          : (1473,  657,  315,  161),
    "resume"         : ( 794,  567,  336,   63),
    "enterInvert"    : ( 943,  669,  382,  106),
    "ConfirmTeam"    : (1593,  830,  234,   90),
    "enterBonus"     : (1702,  957,  166,   85),
    "starlight"      : (1069,  525,   42,   42),
    "refuse"         : (1181,  818,  295,  124),
    "giftSearch"     : (1640,  207,   70,   60),
    "StartEGO"       : ( 198,  207,  937,  682),
    "Claim"          : (1540,  831,  299,  132),
    "ConfirmInvert"  : ( 987,  704,  318,   71),
    "ClaimInvert"    : (1125,  796,  300,   70),
    "victory"        : (1426,  116,  366,  184),
    "defeat"         : (1426,  116,  366,  184),
    "GiveUp"         : ( 490,  800,  300,   60),
    "Confirm.0"      : ( 816,  657,  471,  197),
    "ServerError"    : ( 651,  640,  309,  124),
    "EventEffect"    : ( 710,  215,  507,   81),
    "bonus"          : ( 890,  357,  163,   63),
    "bonus_off"      : ( 890,  357,  163,   63),
    "hardbonus"      : (1054,  357,  163,   63),
    "ConfirmInvert.1": ( 987,  704,  318,  130),
    # regions not binded to an image
    "money!"         : (1718,   47,   57,   40),
    "gifts!"         : (1173,  324,  129,  125),
    "selected!"      : (1682,  855,   30,   42),

    # battle.py
    "TOBATTLE"       : (1586,  820,  254,  118),
    "winrate"        : ( 350,  730, 1570,  232),
    "pause"          : (1724,   16,   83,   84),
    "Confirm_alt"    : ( 960,  689,  350,  100),
    "teams"          : (  96,  441,  180,  350),
    "current_team"   : ( 330,  165,  200,   50),
    "arrow"          : ( 189,  443,   16,   15),
    "skip_yap"       : ( 740,  450,  470,  200),

    # event.py
    "textEGO"        : (1031,  254,  713,  516),
    "eventskip"      : ( 850,  437,  103,   52),
    "check"          : (1265,  434,  430,   87),
    "choices"        : (1036,  152,  199,   77),
    "Proceed"        : (1539,  906,  316,  126),
    "Commence"       : (1539,  906,  316,  126),
    "Continue"       : (1539,  906,  316,  126),
    "CommenceBattle" : (1539,  906,  316,  126),
    "probs"          : (  42,  876, 1427,   74),

    # grab.py
    "encounterreward": ( 412,  165,  771,   72),
    "Confirm"        : ( 791,  745,  336,  104),
    "Cancel"         : ( 660,  650,  278,   92),
    "EGObin"         : (  69,   31,  123,  120),
    "EGO"            : (   0,  309, 1920,  110),
    "Owned"          : (   0,  216, 1725,   50),
    "Card"           : ( 219,  283, 1531,  242),
    "Confirm.1"      : (1118,  754,  189,   70),
    "trials"         : (   0,  615, 1920,   55),
    # regions not binded to an image
    "rewardCount!"   : (1494,  181,   23,   42),

    # move.py
    "Move"           : (1805,  107,   84,   86),
    "enter"          : (1537,  739,  310,  141),
    "alldead"        : ( 261, 1019, 1391,   41),
    "suicide"        : ( 626,  157,  650,  142),
    "forfeit"        : ( 662,  547,  151,  208),
    "directions"     : ( 523,  303,  155,  473),

    # pack.py
    "lvl"            : ( 957,  151,   25,   52),
    "PackChoice"     : (1757,  126,  115,  116),
    "PackCard"       : (  76,  799,  497,  885),
    "hardDifficulty" : ( 893,  207,  115,   44),

    # shop.py
    "shop"           : ( 332,  158,  121,   55),
    "supershop"      : ( 275,  158,  220,   55),
    "sell"           : ( 776,  118,  127,   70),
    "fuse_shelf"     : ( 920,  295,  790,  482),
    "fuse_shelf_low" : ( 920,  591,  790,  150),
    "buy_shelf"      : ( 809,  300,  942,  402),
    "purchase"       : ( 972,  679,  288,   91),
    "power"          : ( 990,  832,  393,   91),
    "Confirm.2"      : ( 990,  832,  393,   91),
    "keywordSel"     : ( 832,  119,  469,   58),
    "keywordRef"     : ( 678,  162,  340,   53),
    "fuse"           : ( 754,  117,  161,   81),
    "fuseButton"     : (1107,  849,  161,   54),
    "scroll"         : (1653,  321,   64,   81),
    "scroll.0"       : (1653,  662,   64,   81),
    # regions not binded to an image
    "affinity!"      : ( 368,  327, 1160,  442),
    "revenue!"       : (1405,  126,  241,   56),
    "forecast!"      : ( 280,  257,  540,  334),

    # utils.py
    "connecting"     : (1548,   66,  293,   74),
    "loading"        : (1577,  408,  302,   91),

    # lux.py
    "Lux"            : ( 523,  145,  301,  212),
    "Exp"            : (  68,  319,  289,  135),
    # regions not binded to an image
    "pick!"          : ( 417,  667, 1428,   95),
    "thd!"           : (1152,  324,  163,  462),
}

SINNERS = {
    "YISANG"    : ( 351, 207, 196, 285),
    "FAUST"     : ( 547, 207, 196, 285),
    "DONQUIXOTE": ( 743, 207, 196, 285),
    "RYOSHU"    : ( 939, 207, 196, 285),
    "MEURSAULT" : (1135, 207, 196, 285),
    "HONGLU"    : (1331, 207, 196, 285),
    "HEATHCLIFF": ( 351, 492, 196, 285),
    "ISHMAEL"   : ( 547, 492, 196, 285),
    "RODION"    : ( 743, 492, 196, 285),
    "SINCLAIR"  : ( 939, 492, 196, 285),
    "OUTIS"     : (1135, 492, 196, 285),
    "GREGOR"    : (1331, 492, 196, 285)
}


# Easy dungeon floors
FLOORS = {
    1: [
        'TheForgotten', 'TheOutcast', 'NagelundHammer', 'FlatbrokeGamblers',
        'AutomatedFactory', 'TheUnloving', 'FaithErosion', 'NestWorkshopandTechnology'
    ],
    2: [
        'FlatbrokeGamblers', 'AutomatedFactory', 'TheUnloving', 'FaithErosion',
        'NestWorkshopandTechnology', 'LakeWorld', 'HellsChicken', 'SEA',
        'TobeCleaved', 'TobePierced', 'TobeCrushed'
    ],
    3: [
        'TobeCleaved', 'TobePierced', 'TobeCrushed', 'TheUnconfronting', 'FallingFlowers',
        'DregsoftheManor', 'EmotionalRepression', 'EmotionalSeduction', 'EmotionalIndolence',
        'EmotionalCraving', 'EmotionalFlood', 'EmotionalSubservience', 'EmotionalJudgment'
    ],
    4: [
        'MiracleinDistrict20', 'TheNoonofViolet', 'FullStoppedbyaBullet', 'TearfulThings',
        'CrawlingAbyss', 'ACertainWorld', 'toClaimTheirBones', 'TimekillingTime',
        'MurderontheWARPExpress', 'RepressedWrath', 'AddictingLust', 'TreadwheelSloth',
        'DevouredGluttony', 'DegradedGloom', 'VainPride', 'InsignificantEnvy', 'HatredandDespair'
    ],
    5: [
        'TearfulThings', 'CrawlingAbyss', 'ACertainWorld', 'toClaimTheirBones',
        'TimekillingTime', 'MurderontheWARPExpress', 'RepressedWrath', 'AddictingLust',
        'TreadwheelSloth', 'DevouredGluttony', 'DegradedGloom', 'VainPride', 'InsignificantEnvy',
        'LCBRegularCheckup', 'NocturnalSweeping', 'SlicersDicers', 'PiercersPenetrators',
        'CrushersBreakers'
    ]
}

BANNED = [
    "AutomatedFactory", "TheUnloving", "FaithErosion", "TobeCrushed", "TheNoonofViolet", 
    "MurderontheWARPExpress", "FullStoppedbyaBullet", "VainPride", "CrawlingAbyss", "TimekillingTime", 
    "NocturnalSweeping", "toClaimTheirBones"
]


# Hard dungeon floors
HARD_FLOORS = {
    1: [
        'TheForgotten', 'TheOutcast', 'NagelundHammer', 'FlatbrokeGamblers',
        'AutomatedFactory', 'TheUnloving', 'FaithErosion', 'NestWorkshopandTechnology', 
        'LakeWorld', 'TobeCleaved', 'TobePierced', 'TobeCrushed', 'DregsoftheManor'
    ],
    2: [
        'AutomatedFactory', 'TheUnloving', 'HellsChicken', 'SEA', 'TobeCleaved', 'TobePierced', 
        'TobeCrushed', 'FallingFlowers', 'EmotionalRepression', 'EmotionalSeduction', 'EmotionalIndolence',
        'EmotionalCraving', 'EmotionalFlood', 'EmotionalSubservience', 'EmotionalJudgment'
    ],
    3: [
        'TheUnconfronting', 'MiracleinDistrict20', 'TheNoonofViolet', 'FullStoppedbyaBullet', 
        'TearfulThings', 'CrawlingAbyss', 'ACertainWorld', 'toClaimTheirBones', 'RepressedWrath', 
        'AddictingLust', 'TreadwheelSloth', 'DevouredGluttony', 'DegradedGloom', 'VainPride', 
        'InsignificantEnvy', 'SlicersDicers', 'PiercersPenetrators', 'CrushersBreakers',
        'RisingPowerSupply', 'DeepSigh', 'SinkingPang', 'CrushingExternalForce', 'DizzyingWaves',
        'TrickledSanguineBlood', 'BurningHaze', 'HatredandDespair'
    ],
    4: [
        'TearfulThings', 'CrawlingAbyss', 'ACertainWorld', 'toClaimTheirBones', 'TimekillingTime', 
        'MurderontheWARPExpress', 'RepressedWrath', 'AddictingLust', 'TreadwheelSloth', 
        'DevouredGluttony', 'DegradedGloom', 'VainPride', 'InsignificantEnvy', 'ThunderandLightning', 
        'PoisedBreathing', 'SinkingDeluge', 'UnrelentingMight', 'AbnormalSeismicZone', 
        'MountainofCorpsesSeaofBlood', 'SeasonoftheFlame', 'toClaimTheirBonesBokGak',
        'MiracleinDistrict20BokGak', 'Line2', 'Line1', 'TheEvilDefining', 'TheUnchanging',
        'TimekillingTimeBokGak'
    ],
    5: [
        'TimekillingTime', 'MurderontheWARPExpress', 'LCBRegularCheckup', 'NocturnalSweeping', 
        'ThunderandLightning', 'PoisedBreathing', 'SinkingDeluge', 'UnrelentingMight',
        'AbnormalSeismicZone', 'MountainofCorpsesSeaofBlood', 'SeasonoftheFlame', 'PitifulEnvy', 
        'TyrannicalPride', 'SunkGloom', 'ExcessiveGluttony', 'InertSloth', 'TanglingLust', 
        'UnboundWrath', 'toClaimTheirBonesBokGak', 'MiracleinDistrict20BokGak', 'Line4', 'Line3',
        'TheInfiniteProcession', 'TheHeartbreaking', 'LaManchalandReopening', 'TheEvilDefining',
        'TheUnchanging', 'FourHousesandGreed', 'Line5', 'TheSurrenderedWitnessing', 'TheDreamEnding',
        'TimekillingTimeBokGak'
    ]
}

HARD_BANNED = [
    "TheNoonofViolet", "MurderontheWARPExpress", "FullStoppedbyaBullet", "TimekillingTime", 
    "NocturnalSweeping", 'Line4', 'Line3', 'toClaimTheirBonesBokGak', 'TheEvilDefining', 
    'SinkingDeluge', 'PoisedBreathing', 'InertSloth', 'EmotionalFlood', 'CrawlingAbyss', 
    'TreadwheelSloth', 'VainPride', 'PitifulEnvy', 'TyrannicalPride', 'UnrelentingMight', 
    'Line5', 'TheSurrenderedWitnessing', 'TheDreamEnding', 'HatredandDespair', 'TimekillingTimeBokGak'
]


def get_unique(pack_list):
    unique = []
    seen = set()
    for floor in sorted(pack_list):
        for item in pack_list[floor]:
            if item not in seen:
                seen.add(item)
                unique.append(item)
    return unique


FLOORS_UNIQUE = get_unique(FLOORS)
HARD_UNIQUE = get_unique(HARD_FLOORS)