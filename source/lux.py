from source.utils.utils import *
from source.battle import fight

def is_full():
    image = screenshot(region=(672, 1003, 5, 5))
    y, x = image.shape[0] // 2, image.shape[1] // 2
    b, g, r = image[y, x]
    return (
        0 <= r <= 10 and
        160 <= g <= 255 and
        50 <= b <= 140
    )

def check_enkephalin():
    if not is_full(): return

    ClickAction((601, 1004), ver="ConfirmInvert").execute(click)
    win_click(1208, 496, duration=0.2)
    Action("ConfirmInvert", ver="connecting").execute(click)
    win_click(1593, 833, duration=0.2)
    time.sleep(0.5)


def grind_lux(count_exp, count_thd):
    countdown(10)
    setup_logging(enable_logging=p.LOG)
    logging.info('Script started')

    if not now.button("winrate") and not now.button("Exp"):
        Action("Drive", ver="Lux").execute(click)
        Action("Lux", ver="Exp").execute(click)
    print("Entering Lux!")
    while count_exp:
        if gui.getActiveWindowTitle() != 'LimbusCompany': pause()
        time.sleep(0.5)

        choices = LocateRGB.locate_all(PTH["EnterDoor"], region=REG["pick!"])
        if len(choices) != 0:
            cv2.imwrite("test.png", screenshot(region=REG["pick!"]))
            choices.sort(key=lambda box: box[0], reverse=True)
            print(choices)
            win_click(gui.center(choices[0]))
            time.sleep(0.5)

            logging.info("Exp Luxcavation")
        fight(lux=True)

        if loc.button("victory"):
            count_exp -= 1
            gui.press("Enter")
            gui.press("Enter")
        elif loc.button("defeat"):
            if not p.RESTART:
                raise RuntimeError("Luxcavation failed!")
            gui.press("Enter")
    
    while count_thd:
        if gui.getActiveWindowTitle() != 'LimbusCompany': pause()
        wait_for_condition(lambda: not now.button("Exp"))
        win_click(225, 492)
        time.sleep(1)
        win_click(553, 721)

        wait_for_condition(lambda: not now.button("EnterSmall", "thd!"))
        time.sleep(1)
        choices = LocateRGB.locate_all(PTH["EnterSmall"], region=REG["thd!"])
        if len(choices) != 0:
            choices.sort(key=lambda box: box[1], reverse=True)
            win_click(gui.center(choices[0]))
            time.sleep(0.5)

            logging.info("Thread Luxcavation")
        fight(lux=True)

        if loc.button("victory"):
            count_thd -= 1
            gui.press("Enter")
            gui.press("Enter")
        elif loc.button("defeat"):
            if not p.RESTART:
                raise RuntimeError("Luxcavation failed!")
            gui.press("Enter")

    wait_for_condition(lambda: not now.button("Exp"))
    time.sleep(1)
    gui.press("Esc")

    if p.NETZACH:
        time.sleep(1)
        check_enkephalin()
    logging.info("Done with Luxcavation!")
    
