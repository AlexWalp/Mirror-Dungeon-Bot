from source.utils.utils import *
from itertools import cycle

from source.battle import fight, select_team
from source.event import event
from source.pack import pack
from source.move import move
from source.grab import grab_card, grab_EGO, confirm
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
    "Confirm.0": 17, 
    "refuse": 19, 
    "Confirm": 25
}

def dungeon_start():
    ACTIONS = [
        Action("Drive"),
        Action("MD", ver="Start"),
        lambda: win_click(1588, 567) if p.INFINITE and now_rgb.button("infinite_off") else None,
        Action("Start"),
        Action("enterInvert", ver="ConfirmTeam"),
        select_team,
        lambda: try_click.button("ConfirmTeam"),
        lambda: time.sleep(0.5),
        lambda: now_click.button("ConfirmInvert"),
        lambda: wait_for_condition(lambda: not now.button("enterBonus")),
        lambda: time.sleep(0.2),

        lambda: ClickAction(( 401, 381), ver="money!").execute(try_click) if p.BUFF[0] else None,
        lambda: ClickAction(( 686, 381), ver="money!").execute(try_click) if p.BUFF[1] else None,
        lambda: ClickAction(( 966, 381), ver="money!").execute(try_click) if p.BUFF[2] else None,
        lambda: ClickAction((1241, 381), ver="money!").execute(try_click) if p.BUFF[3] else None,

        Action("enterBonus", ver="Confirm.0"),
        lambda: now_click.button("starlight"),
        Action("Confirm.0", ver="refuse"),

        lambda: time.sleep(0.2),
        lambda: now_click.button("giftSearch"),
        ClickAction(p.GIFTS[0]["checks"][2], ver="gifts!"),
        lambda: ClickAction((1239, 395), ver="selected!").execute(try_click) if (p.BUFF[3] or p.GIFTS[0]['checks'][5] == 0) else None,
        lambda: ClickAction((1239, 549), ver="selected!").execute(try_click) if (p.BUFF[3] or p.GIFTS[0]['checks'][5] == 1) else None,
        ClickAction((1624, 882)),

        lambda: Action("Confirm", ver="Confirm").execute(try_click) if p.BUFF[3] else None,
        Action("Confirm", ver="loading"),
        loading_halt
    ]
    
    failed = 0
    while True:
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
    if p.HARD:
        if now_rgb.button("bonus", "hardbonus", click=True):
            time.sleep(0.2)
            if not now_rgb.button("bonus", "hardbonus"):
                return True
    else:
        if now_rgb.button("bonus", click=True):
            time.sleep(0.2)
            if not now_rgb.button("bonus"):
                return True
    return False

def handle_bonus():
    time.sleep(0.2)
    if p.BONUS or now_rgb.button("bonus_off"): return
    if p.HARD and now_rgb.button("bonus_off", "hardbonus"): return
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
    if not p.RESTART:
        raise RuntimeError("Mirror dungeon failed... If you want to auto-retry, enable 'Restart after run fail'")
    failed = 0
    while True:
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
    level = 1
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

        if gui.getActiveWindowTitle() != 'LimbusCompany':
            pause()

        if p.HARD and now.button("suicide"):
            if not p.INFINITE:
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
            # check if start
            for key in start_locations.keys():
                if now.button(key):
                    dungeon_start()
                    error = 0
                    last_error = 0
                    level = 1
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
            if p.ALTF4:
                close_limbus()
            if p.APP: QMetaObject.invokeMethod(p.APP, "stop_execution", Qt.ConnectionType.QueuedConnection)
            raise StopExecution # change maybe

        time.sleep(0.2)

# when cmd is run:
# def replay_loop():
#     setup()
#     number = input("How many mirrors will you grind? ")
#     number = int(''.join(filter(str.isdigit, number)) or '0')

#     if number < 1:
#         print("I respect that")
#         return
    
#     # count_exp = 1
#     # count_thd = 1
#     # grind_lux(count_exp, count_thd)


#     print(f"Grinding {number} mirrors...")
#     print("Switch to Limbus Window")
#     countdown(10)
    
#     p.GIFTS = TEAMS[p.TEAM]
#     setup_logging(enable_logging=p.LOG)
    
#     logging.info('Script started')
#     set_window()

#     for i in range(number):
#         if p.NETZACH: check_enkephalin()

#         logging.info(f'Iteration {i}')
#         completed = False
#         while not completed:
#             completed = main_loop()


# if __name__ == "__main__":
#     try:
#         replay_loop()
#         if p.ALTF4:
#             close_limbus()
#     except StopExecution:
#         sys.exit()


# when App is run:
def set_team(team, teams):
    if p.HARD: team_list = HARD
    else: team_list = TEAMS

    p.TEAM = [list(team_list.keys())[aff] for aff in list(teams[team]["affinity"])]
    p.NAME_ORDER = teams[team]["affinity_idx"]
    p.DUPLICATES = teams[team]["duplicates"]
    p.GIFTS = [team_list[keyword] for keyword in p.TEAM]

    if not p.BUFF[3]: p.GIFTS[0]['uptie1'] = {k: p.GIFTS[0]['uptie1'][k] for k in list(p.GIFTS[0]['uptie1'])[:1]}

    p.SELECTED = [list(SINNERS.keys())[i] for i in list(teams[team]["sinners"])]
    p.PICK = generate_packs(teams[team]["priority"])
    p.IGNORE = generate_packs(teams[team]["avoid"])

    logging.info(f'Team: {p.TEAM[0]}')
    
    difficulty = "HARD" if p.HARD else "NORMAL"
    if p.INFINITE: difficulty = "INFINITY"
    logging.info(f'Difficulty: {difficulty}')


def execute_me(is_lux, count, count_exp, count_thd, teams, settings, hard, app, warning):
    p.HARD = hard
    p.LOG = settings['log']
    p.BONUS = settings['bonus']
    p.RESTART = settings['restart']
    p.ALTF4 = settings['altf4']
    p.NETZACH = settings['enkephalin']
    p.SKIP = settings['skip']
    p.BUFF = settings['buff']
    p.CARD = settings['card']
    p.WISHMAKING = settings['wishmaking']
    p.WINRATE = settings['winrate']
    p.INFINITE = settings['infinity']
    p.KEYWORDLESS = settings['keywordless']
    p.APP = app
    p.WARNING = warning

    try:
        setup_logging(enable_logging=p.LOG)
    except PermissionError:
        print("No logging I guess")
        setup_logging(enable_logging=False)


    if not is_lux:
        rotator = cycle(list(teams.keys()))
        
        print(f"Grinding {count} mirrors...")
        print("Switch to Limbus Window")
        countdown(10)
        logging.info('Script started')

    try:
        set_window()
        if is_lux:
            grind_lux(count_exp, count_thd, teams)
        else:
            for i in range(count):
                team = next(rotator)
                set_team(team, teams)

                logging.info(f'Iteration {i}')
                completed = False
                while not completed:
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

