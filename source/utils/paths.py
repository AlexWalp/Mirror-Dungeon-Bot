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
            if file.lower().endswith(".png"):
                name = os.path.splitext(file)[0]
                if name in path_dict:
                    raise ValueError(f"Duplicate image name detected: {name}")
                full_path = os.path.join(root, file).replace("\\", "/")
                path_dict[name] = full_path
    return path_dict

PTH = collect_png_paths(ASSETS_DIR)

# presaved regions for some buttons (always the same)
REG = {
    "TOBATTLE"       : (1586,  820,  254,  118),
    "battleEGO"      : (1525,  104,  395,   81),
    "eventskip"      : ( 850,  437,  103,   52),
    "encounterreward": ( 412,  165,  771,   72),
    "victory"        : (1426,  116,  366,  184), # also defeat
    "pause"          : (1724,   16,   83,   84),
    "check"          : (1265,  434,  430,   87),
    "EGOconfirm"     : ( 791,  745,  336,  104), # some instances use different regions
    "Cancel"         : ( 660,  650,  278,   92), 
    "Move"           : (1805,  107,   84,   86),
    "connecting"     : (1548,   66,  293,   74),
    "textEGO"        : (1031,  254,  713,  516), # also textWIN

    "Drive"          : (1229,  896,  156,  139),
    "loading"        : (1577,  408,  302,   91),
    "MD"             : ( 528,  354,  279,  196),
    "Start"          : (1473,  657,  315,  161),
    "enterInvert"    : ( 943,  669,  382,  106),
    "ConfirmTeam"    : (1593,  830,  234,   90),
    "enterBonus"     : (1566,  974,  266,   89),
    "StartEGO"       : ( 198,  207,  937,  682),
    "Claim"          : (1540,  831,  299,  132),
    "ConfirmInvert"  : ( 987,  704,  318,   71),
}