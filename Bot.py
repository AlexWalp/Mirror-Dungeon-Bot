from source.utils.utils import *
from source.battle import fight
from source.event import event
from source.pack import pack
from source.move import move
from source.grab import grab_card, grab_EGO, confirm
from source.shop import shop
from source.teams import TEAMS
import source.utils.params as p


# Action          -> next action is verifier
# Action with ver -> don't need next action
# default ver     -> verification by button image in corresponding region
# if ver has !    -> verification by screenshot region change (image correlation)

# INIT RUN

def dungeon_start():
    ACTIONS = [
        Action("Drive"),
        Action("MD"),
        Action("Start"),
        Action("enterInvert"),
        Action("ConfirmTeam", ver="enterBonus"),
        lambda: time.sleep(0.2),

        ClickAction((401, 381), ver="money!"),
        ClickAction((686, 381), ver="money!"),
        ClickAction((966, 381), ver="money!"),
        ClickAction((1241, 381), ver="money!"),

        Action("enterBonus"),
        Action("Confirm.0", ver="refuse"),

        Action(p.GIFTS["checks"][2], "StartEGO", ver="gifts!"),
        ClickAction((1239, 395), ver="selected!"),
        ClickAction((1239, 549), ver="selected!"),
        ClickAction((1624, 882)),

        Action("Confirm"),
        Action("Confirm", ver="loading"),
        loading_halt
    ]
    
    failed = 0
    while True:
        now_click.button("resume")
        locations = {
            "Drive": 0, 
            "MD": 1, 
            "Start": 2, 
            "enterInvert": 3, 
            "ConfirmTeam": 4, 
            "enterBonus": 6, 
            "Confirm.0": 11, 
            "refuse": 12, 
            "Confirm": 17
        }
        for key in locations.keys():
            if now.button(key):
                i = locations[key]
                break
        else: break
        try:
            chain_actions(try_click, ACTIONS[i:])
        except RuntimeError:
            failed += 1
        if failed > 5:
            print("Initialization error")
            logging.error("Initialization error")
            break
    print("Entering MD!")


# END RUN
def collect_rewards():
    wait_for_condition(
        condition=lambda: not now.button("loading"),
        action=lambda: now_click.button("Confirm.0"),
        interval=0.1
    )

def click_bonus():
    if now_rgb.button("bonus", click=True):
        time.sleep(0.2)
        if not now_rgb.button("bonus"):
            return True
    return False

def handle_bonus():
    if p.BONUS or now_rgb.button("bonus_off"): return
    time.sleep(0.2)
    if not wait_for_condition(lambda: not click_bonus()):
        raise RuntimeError

TERMIN = [
    Action("victory", click=(1693, 841)),
    lambda: win_moveTo(1710, 982),
    Action("Claim", ver="ClaimInvert"),
    handle_bonus,
    Action("ClaimInvert"),
    Action("ConfirmInvert", ver="Confirm.0"),
    collect_rewards,
    loading_halt,
    lambda: try_loc.button("Drive")
]

def dungeon_end():
    try:
        chain_actions(try_click, TERMIN)
    except RuntimeError:
        print("Termination error")
        logging.error("Termination error")
    print("MD Finished!")

# FAIL RUN
FAIL = [
    Action("defeat", click=(1693, 841)),
    lambda: win_moveTo(1710, 982),
    Action("Claim"),
    Action("GiveUp"),
    Action("ConfirmInvert", ver="loading"),
    loading_halt,
    lambda: try_loc.button("Drive")
]

def dungeon_fail():
    if not p.RESTART:
        raise RuntimeError("Mirror dungeon failed... If you want to auto-retry, enable 'Restart after run fail'")
    try:
        chain_actions(try_click, FAIL)
    except RuntimeError:
        print("Termination error")
        logging.error("Termination error")
    print("MD Failed!")


# MAIN LOOP
def main_loop():
    dungeon_start()
    error = 0
    last_error = 0
    level = 1
    while True:
        if now.button("ServerError"):
            win_click(1100, 700)
            time.sleep(10)
            if now_click.button("ServerError"):
                logging.error('Server error happened')

        if now.button("EventEffect"):
            win_click(773, 521)
            time.sleep(0.2)
            win_click(967, 774)

        if gui.getActiveWindowTitle() != 'LimbusCompany':
            pause()
        
        if now.button("victory"):
            logging.info('Run Completed')
            dungeon_end()
            return True

        if now.button("defeat"):
            logging.info('Run Failed')
            dungeon_fail()
            return False

        try:
            ck, level = pack(level)
            ck += move()
            ck += fight()
            ck += event()
            ck += grab_EGO()
            ck += confirm()
            ck += grab_card()
            ck += shop(level)
        except RuntimeError:
            handle_fuckup()
            error += 1

        if ck == False:
            if last_error != 0:
                if time.time() - last_error > 30:
                    handle_fuckup()
                    error += 1
            else:
                last_error = time.time()
        else:
            last_error = 0

        if error > 20:
            logging.error('We are stuck')
            if p.ALTF4:
                close_limbus()

        time.sleep(0.2)

# when cmd is run:
def replay_loop():
    setup()
    number = input("How many mirrors will you grind? ")
    number = int(''.join(filter(str.isdigit, number)) or '0')

    if number < 1:
        print("I respect that")
        return
    
    print(f"Grinding {number} mirrors...")
    print("Switch to Limbus Window")
    countdown(10)
    
    p.GIFTS = TEAMS[p.TEAM]
    setup_logging(enable_logging=p.LOG)
    
    logging.info('Script started')
    set_window()

    for i in range(number):
        logging.info(f'Iteration {i}')
        completed = False
        while not completed:
            completed = main_loop()


if __name__ == "__main__":
    try:
        replay_loop()
        if p.ALTF4:
            close_limbus()
    except StopExecution:
        sys.exit()


# when App is run:
def execute_me(count, affinity, sinners, log, bonus, restart, altf4, app, warning):
    p.TEAM = list(TEAMS.keys())[affinity]
    p.GIFTS = TEAMS[p.TEAM]
    p.SELECTED = [list(SINNERS.keys())[i] for i in sinners]
    p.LOG = log
    p.BONUS = bonus
    p.RESTART = restart
    p.ALTF4 = altf4
    p.APP = app
    p.WARNING = warning
    
    print(f"Grinding {count} mirrors...")
    print("Switch to Limbus Window")
    countdown(10)
    
    setup_logging(enable_logging=p.LOG)
    
    logging.info('Script started')

    try:
        set_window()
        for i in range(count):
            logging.info(f'Iteration {i}')
            completed = False
            while not completed:
                completed = main_loop()

        if p.ALTF4:
            close_limbus()
    except StopExecution:
        return
    except ZeroDivisionError: # gotta launch the game
        raise RuntimeError("Launch Limbus Company!")

    QMetaObject.invokeMethod(p.APP, "stop_execution", Qt.ConnectionType.QueuedConnection)
    return

