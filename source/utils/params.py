import threading

SELECTED = ["YISANG", "DONQUIXOTE" , "ISHMAEL", "RODION", "SINCLAIR", "GREGOR"]
GIFTS = dict()
LOG = True
BONUS = False
TEAM = "BURN"
RESTART = True
ALTF4 = False
APP = None

WINDOW = (0, 0, 1920, 1080)

pause_event = threading.Event()
stop_event = threading.Event()