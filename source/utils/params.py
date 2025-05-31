import threading

SELECTED = ["YISANG", "DONQUIXOTE" , "ISHMAEL", "RODION", "SINCLAIR", "GREGOR"]
GIFTS = dict()
LOG = True
BONUS = False
TEAM = "BURN"
RESTART = True
ALTF4 = False
NETZACH = False
SKIP = True
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
    'floor4': ['TheNoonofViolet', 'MurderontheWARPExpress', 'FullStoppedbyaBullet', 'VainPride', 'CrawlingAbyss', 'TimekillingTime', 'YieldMyFleshtoClaimTheirBones'], 
    'floor5': ['MurderontheWARPExpress', 'VainPride', 'CrawlingAbyss', 'TimekillingTime', 'NocturnalSweeping', 'YieldMyFleshtoClaimTheirBones']
}

WARNING = None
WINDOW = (0, 0, 1920, 1080)

pause_event = threading.Event()
stop_event = threading.Event()