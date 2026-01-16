from source.utils.utils import *
from itertools import cycle

from source.battle import fight, select_team
from source.event import event
from source.pack import pack
from source.move import move
from source.grab import grab_card, grab_EGO, confirm, get_adversity
from source.shop import shop
from source.lux import grind_lux, check_enkephalin
from source.teams import TEAMS, HARD
import source.utils.params as p


# Action          -> next action is verifier
# Action with ver -> don't need next action
# default ver     -> verification by button image in corresponding region
# if ver has !    -> verification by screenshot region change (image correlation)

# INIT RUN

start_locations = {
    "Drive": 0, 
    "MD": 1, 
    "Start": 2, 
    "enterInvert": 4, 
    "ConfirmTeam": 6, 
    "enterBonus": 11, 
    "Confirm.0": 14, 
    "refuse": 16, 
    "Confirm": 24
}

def select_grace():
    for i in range(len(p.BUFF)):
        if p.BUFF[i]:
            x = int(375 + 297*(i % 5))
            y = int(375 + 333*(i // 5))
            ClickAction((x, y), ver="money!").execute(try_click)
            if p.BUFF[i] > 1:
                ClickAction((x + 61*(1 - 2*(p.BUFF[i] < 3)), y + 140), ver="money!").execute(try_click)

def dungeon_start():
    ACTIONS = [
        Action("Drive"),
        Action("MD", ver="Start"),
        lambda: win_click(1588, 567) if p.EXTREME and now_rgb.button("infinite_off") else None,
        Action("Start"),
        Action("enterInvert", ver="ConfirmTeam"),
        select_team,
        lambda: try_click.button("ConfirmTeam"),
        lambda: time.sleep(0.5),
        lambda: now_click.button("ConfirmInvert"),
        lambda: wait_while_condition(lambda: not now.button("enterBonus")),
        lambda: time.sleep(0.2),

        select_grace,

        Action("enterBonus", ver="Confirm.0"),
        lambda: now_click.button("starlight"),
        Action("Confirm.0", ver="refuse"),

        lambda: time.sleep(0.2),
        lambda: now_click.button("giftSearch"),
        ClickAction(p.GIFTS[0]["checks"][2], ver="gifts!"),
        lambda: ClickAction((1239, 395), ver="selected!").execute(try_click) if (p.BUFF[3] or p.GIFTS[0]['checks'][5] == 0) else None,
        lambda: ClickAction((1239, 549), ver="selected!").execute(try_click) if (p.BUFF[3] or p.GIFTS[0]['checks'][5] == 1) else None,
        lambda: ClickAction((1239, 703), ver="selected!").execute(try_click) if p.BUFF[9] else None,
        ClickAction((1624, 882)),

        lambda: Action("Confirm", ver="Confirm").execute(try_click) if p.BUFF[9] else None,
        lambda: Action("Confirm", ver="Confirm").execute(try_click) if p.BUFF[3] else None,
        Action("Confirm", ver="loading"),
        loading_halt
    ]
    
    failed = 0
    while True:
        try:
            now_click.button("resume")
            for key in start_locations.keys():
                if now.button(key):
                    i = start_locations[key]
                    break
            else: break
            try:
                chain_actions(try_click, ACTIONS[i:])
            except RuntimeError:
                failed += 1
                win_moveTo(1509, 978)
        except gui.PauseException as e:
            pause(e.window)
        if failed > 5:
            print("Initialization error")
            logging.error("Initialization error")
            break
    print("Entering MD!")


# END RUN
def collect_rewards():
    wait_while_condition(
        condition=lambda: not now.button("loading"),
        action=lambda: now_click.button("Confirm.0"),
        interval=0.1
    )

def click_bonus():
    if p.HARD:
        now_rgb.button("bonus", "hardbonus", click=True)
    else:
        now_rgb.button("bonus", click=True)

def bonus_gone():
    if p.HARD:
        if not loc_rgb.button("bonus", "hardbonus", wait=1):
            return now_rgb.button("bonus_off", "hardbonus", conf=0.8)
        else: return False
    elif not loc_rgb.button("bonus", wait=1):
        return now_rgb.button("bonus_off", conf=0.8)
    else: return False

def handle_bonus():
    time.sleep(0.5)
    if p.BONUS or bonus_gone(): return

    if not wait_while_condition(lambda: not bonus_gone(), click_bonus):
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

end_locations = {
    "victory": 0,
    "Claim": 2,
    "ClaimInvert": 4,
    "ConfirmInvert": 5,
    "Confirm.0": 6,
}

def dungeon_end():
    failed = 0
    while True:
        try:
            for key in end_locations.keys():
                if now.button(key):
                    i = end_locations[key]
                    break
            else: break
            try:
                chain_actions(try_click, TERMIN[i:])
            except RuntimeError:
                failed += 1
                win_moveTo(1710, 982)
        except gui.PauseException as e:
            pause(e.window)
        if now.button("out_of_fuel"):
            logging.error("We are out of enkephalin!")
            if p.ALTF4: close_limbus()
            if p.APP: QMetaObject.invokeMethod(p.APP, "stop_execution", Qt.ConnectionType.QueuedConnection)
            raise StopExecution
        if failed > 5:
            print("Termination error")
            logging.error("Termination error")
            break
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

fail_locations = {
    "defeat": 0,
    "Claim": 2,
    "GiveUp": 3,
    "ConfirmInvert": 4,
    "loading": 5,
}

def dungeon_fail():
    failed = 0
    while True:
        try:
            for key in fail_locations.keys():
                if now.button(key):
                    i = fail_locations[key]
                    break
            else: break
            try:
                chain_actions(try_click, FAIL[i:])
            except RuntimeError:
                failed += 1
                win_moveTo(1710, 982)
        except gui.PauseException as e:
            pause(e.window)
        if failed > 5:
            print("Termination error")
            logging.error("Termination error")
            break
    print("MD Failed!")


# MAIN LOOP
def main_loop():
    dungeon_start()
    error = 0
    last_error = 0
    ck = False
    p.MOVE_ANIMATION = False
    p.LVL = 1
    while True:
        if now.button("ServerError"):
            for _ in range(3):
                time.sleep(6)
                win_click(1100, 700)
                time.sleep(1)
                if not now.button("ServerError"): break

            time.sleep(10)
            if now_click.button("ServerError"):
                logging.error('Server error happened')

        if now.button("EventEffect"):
            win_click(773, 521)
            time.sleep(0.2)
            win_click(967, 774)

        if (win := gui.getActiveWindowTitle()) != p.LIMBUS_NAME: pause(win)

        if p.HARD and now.button("suicide"):
            if not p.EXTREME:
                win_click(815, 681)
            else:
                win_click(1117, 681)
            connection()
        
        if now.button("victory"):
            logging.info('Run Completed')
            dungeon_end()
            return True

        if now.button("defeat"):
            logging.info('Run Failed')
            dungeon_fail()
            return False

        try:
            ck  = pack()
            ck += move()
            ck += fight()
            ck += event()
            ck += grab_EGO()
            ck += confirm()
            if p.EXTREME:
                ck += get_adversity()
            ck += grab_card()
            ck += shop()
        except RuntimeError:
            handle_fuckup()
            error += 1
        except gui.PauseException as e:
            pause(e.window)

        if ck == False:
            # check if start
            for key in start_locations.keys():
                if now.button(key):
                    dungeon_start()
                    error = 0
                    last_error = 0
                    p.LVL = 1
                    break
            else: 
                # check if end
                for key in end_locations.keys():
                    if now.button(key):
                        logging.info('Run Completed')
                        dungeon_end()
                        return True
                
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
            if p.ALTF4: close_limbus()
            if p.APP: QMetaObject.invokeMethod(p.APP, "stop_execution", Qt.ConnectionType.QueuedConnection)
            raise StopExecution # change maybe

        time.sleep(0.2)


# when App is run:
def set_team(team, teams, keywordless):
    if p.HARD: team_list = HARD
    else: team_list = TEAMS

    p.TEAM = [list(team_list.keys())[aff] for aff in list(teams[team]["affinity"])]
    p.NAME_ORDER = teams[team]["affinity_idx"]
    p.DUPLICATES = teams[team]["duplicates"]
    p.GIFTS = [team_list[keyword] for keyword in p.TEAM]

    if not p.BUFF[3]: p.GIFTS[0]['uptie1'] = {k: p.GIFTS[0]['uptie1'][k] for k in list(p.GIFTS[0]['uptie1'])[:1]}

    p.SELECTED = [list(SINNERS.keys())[i] for i in list(teams[team]["sinners"])]
    p.PICK = generate_packs_pr(teams[team]["priority"])
    p.IGNORE = generate_packs_av(teams[team]["avoid"])
    p.PICK_ALL = generate_packs_all(teams[team]["priority"])
    print(p.PICK, p.IGNORE, p.PICK_ALL)

    logging.info(f'Team: {p.TEAM[0]}')
    
    difficulty = "HARD" if p.HARD else "NORMAL"
    if p.EXTREME: 
        difficulty = "EXTREME"
        lunar_comp = list(set(["slashmemory", "piercememory", "bluntmemory"]) - set([f"{name.lower()}memory" for name in p.TEAM]))
        stones = [f"stone{i}" for i in range(7)] + lunar_comp
        p.KEYWORDLESS = keywordless | {"lunarmemory": 2} | {gift: 2 for gift in stones}
    else:
        p.KEYWORDLESS = keywordless
    logging.info(f'Difficulty: {difficulty}')


def execute_me(count, count_exp, count_thd, teams, settings, hard, app, warning):
    p.HARD = hard
    p.BONUS = settings['bonus']
    p.RESTART = settings['restart']
    p.ALTF4, p.ALTF4_lux = settings['altf4']
    p.NETZACH = settings['enkephalin']
    p.SKIP = settings['skip']
    p.BUFF = settings['buff']
    p.CARD = settings['card']
    p.WISHMAKING = settings['wishmaking']
    p.WINRATE = settings['winrate']
    p.EXTREME = settings['infinity']
    p.APP = app
    p.WARNING = warning

    if count == -1: count = 9999
    print("Switch to Limbus Window")
    countdown(10)
    logging.info('Script started')
    try:
        gui.set_window()
        lux_keys = [key for key in teams.keys() if key >= 7]
        team_keys = [key for key in teams.keys() if key < 7]

        if lux_keys:
            print("Entering Lux!")
            grind_lux(count_exp, count_thd, teams)
            if team_keys and p.APP: QMetaObject.invokeMethod(p.APP, "lux_hide", Qt.ConnectionType.QueuedConnection)
            elif p.ALTF4_lux:
                close_limbus()
            
        if team_keys:
            print("Entering MD!")
            rotator = cycle(team_keys)
            keywordless = settings['keywordless']

            for i in range(count):
                team = next(rotator)

                logging.info(f'Iteration {i}')
                completed = False
                while not completed:
                    set_team(team, teams, keywordless)
                    completed = main_loop()
                    if p.NETZACH: check_enkephalin()

            if p.ALTF4:
                close_limbus()
    except StopExecution:
        return
    except ZeroDivisionError: # gotta launch the game
        raise RuntimeError("Launch Limbus Company!")

    QMetaObject.invokeMethod(p.APP, "stop_execution", Qt.ConnectionType.QueuedConnection)
    return

