from utils import *
from battle import fight
from event import event
from pack import pack
from pathing import move
from grab import grab_card, grab_EGO, confirm
from shop import shop



def dungeon_start():
    try:
        check(pth("start", "Drive.png"), region=(1229, 896, 156, 139), click=True, error=True)
        check(pth("start", "MD.png"), region=(528, 354, 279, 196), click=True, error=True)
        check(pth("start", "Start.png"), region=(1473, 657, 315, 161), click=True, error=True)
        time.sleep(0.2)

        check(pth("start", "enterInvert.png"), region=(943, 669, 382, 106), click=True, error=True)
        gui.moveTo(1726, 978)
        gui.click()
        if check(pth("start", "ConfirmTeam.png"), region=(1593, 830, 234, 90), error=True):
            time.sleep(0.2)
            gui.click(1717, 878, duration=0.1)

        # Bonus Choice:

        if check(pth("start", "enterBonus.png"), region=(1566, 974, 266, 89), error=True):
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
    
        check(pth("start", "enterBonus.png"), region=(1566, 974, 266, 89), click=True, error=True)
        check("EGOconfirm.png", region=(957, 764, 330, 90), click=True, error=True)

        # Starting EGO

        time.sleep(0.1)
        check(pth("teams", "Burn", "BurnStart.png"), region=(198, 207, 937, 682), click=True, error=True)
        time.sleep(0.1)
        gui.moveTo(1239, 395, duration=0.1)
        gui.doubleClick()
        time.sleep(0.1)
        gui.moveTo(1239, 549, duration=0.1)
        gui.doubleClick()
        gui.moveTo(1624, 882, duration=0.1)
        gui.doubleClick()
        time.sleep(0.1)

        check("EGOconfirm.png", region=(794, 745, 321, 102), click=True, error=True)
        time.sleep(0.2)
        check("EGOconfirm.png", region=(794, 745, 321, 102), click=True, error=True)

    except RuntimeError:
        print("Initialization error")
        logging.error("Initialization error")
        # gui.screenshot(f"errors/init{int(time.time())}.png") # debugging
        # close_limbus()

    print("Entering MD!")


def dungeon_end():
    try:
        if check(pth("end", "victory.png"), region=(1426, 116, 366, 154), error=True):
            gui.click(1693, 841)

        gui.moveTo(1700, 1026)

        check(pth("end", "Claim.png"), click=True, region=(1540, 831, 299, 132), error=True)
        time.sleep(0.2)
        check(pth("end", "ClaimInvert.png"), click=True, region=(1156, 776, 360, 94), error=True)
        check(pth("end", "ConfirmInvert.png"), click=True, region=(987, 704, 318, 71), error=True)

        start_time = time.time()
        while not check("loading.png", region=(1577, 408, 302, 91), skip_wait=True):
            if time.time() - start_time > 20: raise RuntimeError("Infinite loop exited")
            check("EGOconfirm.png", region=(816, 657, 275, 96), skip_wait=True, click=True)

        check(pth("start", "Drive.png"), region=(1229, 896, 156, 139), error=True, wait=10)
        time.sleep(0.5)

    except RuntimeError:
        print("Termination error")
        logging.error("Termination error")
        # gui.screenshot(f"errors/end{int(time.time())}.png") # debugging
        # close_limbus()

    print("MD Finished!")


def main_loop():

    dungeon_start()

    start_time = time.time()
    while check(button="loading.png", region=(1577, 408, 302, 91), wait=1):
        if time.time() - start_time > 20: raise RuntimeError("Infinite loop exited")
        print("loading screen...")
        time.sleep(0.5)

    error = 0
    level = 1
    buy = ["glimpseShop.png", "dustShop.png", "stewShop.png", "paraffinShop.png", "ashShop.png"]

    while True:
        if check(button="ServerError.png", region=(651, 640, 309, 124), click=True, skip_wait=True):
            logging.error('Server error happened')

        if check(button="EventEffect.png", region=(710, 215, 507, 81), skip_wait=True):
            gui.click(773, 521)
            time.sleep(0.2)
            gui.click(967, 774)

        if gui.getActiveWindowTitle() != 'LimbusCompany':
            pause()
        
        if check(pth("end", "victory.png"), region=(1478, 143, 296, 116), skip_wait=True):
            logging.info('Run Completed')
            break
        
        ck, level = pack(level)
        ck += move()
        ck += fight()
        ck += event()
        ck += grab_EGO()
        ck += confirm()
        ck += grab_card()
        ck += shop(level, buy)

        if not ck:
            error += 1 

        if error > 1000:
            logging.error('We are stuck')
            gui.screenshot(pth(BASE_PATH, "errors", "stuck", f"{int(time.time())}.png")) # debugging
            close_limbus()

    dungeon_end()


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
        main_loop()


if __name__ == "__main__":
    replay_loop()
    # close_limbus()
