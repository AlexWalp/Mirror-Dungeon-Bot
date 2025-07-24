import threading

V = "2.1.3"

SELECTED = ["YISANG", "DONQUIXOTE" , "ISHMAEL", "RODION", "SINCLAIR", "GREGOR"]
GIFTS = dict()
LOG = True
BONUS = False
TEAM = "BURN"
RESTART = True
ALTF4 = False
NETZACH = False
SKIP = True
HARD = False
APP = None

PICK = {
    'floor1': ['TheOutcast'], 
    'floor2': ['HellsChicken'], 
    'floor3': [], 
    'floor4': [], 
    'floor5': ['LCBRegularCheckup']
}

IGNORE = {
    'floor1': ['AutomatedFactory', 'TheUnloving', 'FaithErosion'], 
    'floor2': ['AutomatedFactory', 'TheUnloving', 'FaithErosion', 'TobeCrushed'], 
    'floor3': ['TobeCrushed'], 
    'floor4': ['TheNoonofViolet', 'MurderontheWARPExpress', 'FullStoppedbyaBullet', 'VainPride', 'CrawlingAbyss', 'TimekillingTime', 'toClaimTheirBones'], 
    'floor5': ['MurderontheWARPExpress', 'VainPride', 'CrawlingAbyss', 'TimekillingTime', 'NocturnalSweeping', 'toClaimTheirBones']
}

WARNING = None
WINDOW = (0, 0, 1920, 1080)

pause_event = threading.Event()
stop_event = threading.Event()

SUPER = "shop" # for Hard MD
AGRESSIVE_FUSING = True