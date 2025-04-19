from source.utils.utils import *
from source.battle import fight
from source.event import event
from source.pack import pack
from source.move import move
from source.grab import grab_card, grab_EGO, confirm
from source.shop import shop



def dungeon_start():
    try:
        LocateGray.check(PTH["Drive"], region=(1229, 896, 156, 139), click=True, error=True)
        LocateGray.check(PTH["MD"], region=(528, 354, 279, 196), click=True, error=True)
        LocateGray.check(PTH["Start"], region=(1473, 657, 315, 161), click=True, error=True)
        time.sleep(0.5)

        LocateGray.check(PTH["enterInvert"], region=(943, 669, 382, 106), click=True, error=True)
        gui.moveTo(1726, 978)
        gui.click()
        if LocateGray.check(PTH["ConfirmTeam"], region=(1593, 830, 234, 90), error=True):
            time.sleep(0.2)
            gui.click(1717, 878, duration=0.1)

        # Bonus Choice:

        if LocateGray.check(PTH["enterBonus"], region=(1566, 974, 266, 89), error=True):
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
    
        LocateGray.check(PTH["enterBonus"], region=(1566, 974, 266, 89), click=True, error=True)
        LocateGray.check(PTH["EGOconfirm"], region=(957, 764, 330, 90), click=True, error=True)

        # Starting EGO

        time.sleep(0.1)
        LocateGray.check(PTH["BurnStart"], region=(198, 207, 937, 682), click=True, error=True)
        time.sleep(0.1)
        gui.moveTo(1239, 395, duration=0.1)
        gui.doubleClick()
        time.sleep(0.1)
        gui.moveTo(1239, 549, duration=0.1)
        gui.doubleClick()
        gui.moveTo(1624, 882, duration=0.1)
        gui.doubleClick()
        time.sleep(0.1)

        LocateGray.check(PTH["EGOconfirm"], region=(794, 745, 321, 102), click=True, error=True)
        time.sleep(0.2)
        LocateGray.check(PTH["EGOconfirm"], region=(794, 745, 321, 102), click=True, error=True)

    except RuntimeError:
        print("Initialization error")
        logging.error("Initialization error")
        # gui.screenshot(f"errors/init{int(time.time())}") # debugging
        # close_limbus()

    print("Entering MD!")


def dungeon_end():
    try:
        if LocateGray.check(PTH["victory"], region=(1426, 116, 366, 154), error=True):
            gui.click(1693, 841)

        gui.moveTo(1700, 1026)

        LocateGray.check(PTH["Claim"], region=(1540, 831, 299, 132), click=True, error=True)
        time.sleep(0.2)
        LocateGray.check(PTH["ClaimInvert"], region=(1156, 776, 360, 94), click=True, error=True)
        LocateGray.check(PTH["ConfirmInvert"], region=(987, 704, 318, 71), click=True, error=True)

        start_time = time.time()
        while not LocateGray.check(PTH["loading"], region=(1577, 408, 302, 91), wait=False):
            if time.time() - start_time > 20: raise RuntimeError("Infinite loop exited")
            LocateGray.check(PTH["EGOconfirm"], region=(816, 657, 275, 96), wait=False, click=True)

        LocateGray.check(PTH["Drive"], region=(1229, 896, 156, 139), error=True, wait=10)
        time.sleep(0.5)

    except RuntimeError:
        print("Termination error")
        logging.error("Termination error")
        # gui.screenshot(f"errors/end{int(time.time())}") # debugging
        # close_limbus()

    print("MD Finished!")


def dungeon_fail():
    try:
        if LocateRGB.check(PTH["defeat"], region=(1426, 116, 366, 184), error=True):
            gui.click(1693, 841)

        gui.moveTo(1700, 1026)

        LocateGray.check(PTH["Claim"], region=(1540, 831, 299, 132), click=True, error=True)
        time.sleep(0.2)
        LocateGray.check(PTH["GiveUp"], region=(400, 776, 360, 94), click=True, error=True)
        LocateGray.check(PTH["ConfirmInvert"], region=(987, 704, 318, 71), click=True, error=True)

        start_time = time.time()
        while LocateGray.check(PTH["loading"], region=(1577, 408, 302, 91)):
            if time.time() - start_time > 20: raise RuntimeError("Infinite loop exited")
            print("loading screen...")
            time.sleep(0.5)

        LocateGray.check(PTH["Drive"], region=(1229, 896, 156, 139), error=True, wait=10)
        time.sleep(0.5)

    except RuntimeError:
        print("Termination error")
        logging.error("Termination error")
        # gui.screenshot(f"errors/end{int(time.time())}") # debugging
        # close_limbus()

    print("MD Failed!")


def main_loop():

    dungeon_start()

    start_time = time.time()
    while LocateGray.check(PTH["loading"], region=(1577, 408, 302, 91), wait=1):
        if time.time() - start_time > 20: raise RuntimeError("Infinite loop exited")
        print("loading screen...")
        time.sleep(0.5)

    error = 0
    level = 1
    buy = ["glimpse", "dust", "stew", "paraffin", "ash"]

    while True:
        if LocateGray.check(PTH["ServerError"], region=(651, 640, 309, 124), click=True, wait=False):
            logging.error('Server error happened')

        if LocateGray.check(PTH["EventEffect"], region=(710, 215, 507, 81), wait=False):
            gui.click(773, 521)
            time.sleep(0.2)
            gui.click(967, 774)

        if gui.getActiveWindowTitle() != 'LimbusCompany':
            pause()
        
        if LocateGray.check(PTH["victory"], region=(1478, 143, 296, 116), wait=False):
            logging.info('Run Completed')
            dungeon_end()
            return True

        if LocateRGB.check(PTH["defeat"], region=(1426, 116, 366, 184), wait=False):
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
