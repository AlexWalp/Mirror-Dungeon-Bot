from source.utils.utils import *
from source.battle import fight
from source.event import event
from source.pack import pack
from source.move import move
from source.grab import grab_card, grab_EGO, confirm
from source.shop import shop

default = LocatePreset()
click = LocatePreset(click=True, error=True)
nowait = LocatePreset(wait=False)

def dungeon_start():
    try:
        click.button("Drive", "Drive")
        click.button("MD", "MD")
        click.button("Start", "Start")
        time.sleep(0.5)

        click.button("enterInvert", "enterInvert")
        gui.moveTo(1726, 978)
        gui.click()
        if click.button("ConfirmTeam", "ConfirmTeam"):
            time.sleep(0.2)
            gui.click(1717, 878, duration=0.1)

        # Bonus Choice:
        if click.button("enterBonus", "enterBonus"):
            time.sleep(0.1)
            gui.moveTo(401, 381, duration=0.2)
            gui.doubleClick()
            gui.moveTo(686, 381, duration=0.1)
            gui.doubleClick()
            gui.moveTo(966, 381, duration=0.1)
            gui.doubleClick()
            gui.moveTo(1241, 381, duration=0.1)
            gui.doubleClick(duration=0.1)
            time.sleep(0.1)

        click.button("enterBonus", "enterBonus")
        click.button("EGOconfirm", (957, 764, 330, 90))

        # Starting EGO
        time.sleep(0.1)
        click.button("BurnStart", "StartEGO")
        time.sleep(0.1)
        gui.moveTo(1239, 395, duration=0.1)
        gui.doubleClick()
        time.sleep(0.1)
        gui.moveTo(1239, 549, duration=0.1)
        gui.doubleClick()
        gui.moveTo(1624, 882, duration=0.1)
        gui.doubleClick()
        time.sleep(0.1)

        click.button("EGOconfirm", "EGOconfirm")
        time.sleep(0.2)
        click.button("EGOconfirm", "EGOconfirm")

    except RuntimeError:
        print("Initialization error")
        logging.error("Initialization error")
        # gui.screenshot(f"errors/init{int(time.time())}")  # debugging
        # close_limbus()

    print("Entering MD!")


def dungeon_end():
    try:
        if click.button("victory", "victory"):
            gui.click(1693, 841)

        gui.moveTo(1700, 1026)

        click.button("Claim", "Claim")
        time.sleep(0.2)
        click.button("ClaimInvert", (1156, 776, 360, 94))
        click.button("ConfirmInvert", "ConfirmInvert")

        start_time = time.time()
        while not nowait.button("loading", "loading"):
            if time.time() - start_time > 20:
                raise RuntimeError("Infinite loop exited")
            nowait.button("EGOconfirm", (816, 657, 275, 96), click=True)

        default.button("Drive","Drive", error=True, wait=10)
        time.sleep(0.5)

    except RuntimeError:
        print("Termination error")
        logging.error("Termination error")
        # gui.screenshot(f"errors/end{int(time.time())}")  # debugging
        # close_limbus()

    print("MD Finished!")


def dungeon_fail():
    try:
        if LocateRGB.check(PTH["defeat"], region=REG["victory"], error=True):
            gui.click(1693, 841)

        gui.moveTo(1700, 1026)

        click.button("Claim", "Claim")
        time.sleep(0.2)
        click.button("GiveUp", (400, 776, 360, 94))
        click.button("ConfirmInvert", "ConfirmInvert")

        start_time = time.time()
        while default.button("loading", "loading"):
            if time.time() - start_time > 20:
                raise RuntimeError("Infinite loop exited")
            print("loading screen...")
            time.sleep(0.5)

        default.button("Drive", "Drive", error=True, wait=10)
        time.sleep(0.5)

    except RuntimeError:
        print("Termination error")
        logging.error("Termination error")
        # gui.screenshot(f"errors/end{int(time.time())}")  # debugging
        # close_limbus()

    print("MD Failed!")


def main_loop():

    dungeon_start()

    start_time = time.time()
    while default.button("loading", "loading", wait=1):
        if time.time() - start_time > 20: raise RuntimeError("Infinite loop exited")
        print("loading screen...")
        time.sleep(0.5)

    error = 0
    level = 1
    buy = ["glimpse", "dust", "stew", "paraffin", "ash"]

    while True:
        if nowait.button("ServerError", (651, 640, 309, 124), click=True):
            logging.error('Server error happened')

        if nowait.button("EventEffect", (710, 215, 507, 81)):
            gui.click(773, 521)
            time.sleep(0.2)
            gui.click(967, 774)

        if gui.getActiveWindowTitle() != 'LimbusCompany':
            pause()
        
        if nowait.button("victory", "victory"):
            logging.info('Run Completed')
            dungeon_end()
            return True

        if nowait.button("defeat", "victory"):
            logging.info('Run Failed')
            dungeon_fail()
            return False
        
        ck, level = pack(level)
        ck += move()
        ck += fight()
        ck += event()
        ck += grab_EGO(buy)
        ck += confirm()
        ck += grab_card()
        ck += shop(level, buy)

        if not ck:
            error += 1 

        if error > 1000:
            logging.error('We are stuck')
            close_limbus()


def replay_loop():

    number = input("How many mirrors will you grind? ")
    number = int(''.join(filter(str.isdigit, number)))

    if number < 1:
        print("I respect that")
        return
    
    print(f"Grinding {number} mirrors...")
    print("Switch to Limbus Window")
    countdown(10)

    logging.info('Script started')

    for i in range(number):
        logging.info(f'Iteration {i}')
        completed = False
        while not completed:
            completed = main_loop()


if __name__ == "__main__":
    replay_loop()
    # close_limbus()
