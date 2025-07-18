from source.utils.utils import *
from source.battle import fight

def is_full(shift):
    image = screenshot(region=(530 - shift, 1003, 5, 5))
    y, x = image.shape[0] // 2, image.shape[1] // 2
    b, g, r = image[y, x]
    return (
        0 <= r <= 10 and
        160 <= g <= 255 and
        50 <= b <= 140
    )

def check_enkephalin(shift=0): # 227
    if not is_full(shift=shift): return

    ClickAction((601 - shift, 1004), ver="ConfirmInvert.1").execute(click)
    win_click(1208, 496, duration=0.5)
    Action("ConfirmInvert.1", ver="connecting").execute(click)
    connection()
    time.sleep(0.5)
    gui.press("esc")
    time.sleep(0.5)


def start_lux():
    try:
        if now.button("Drive"):
            Action("Drive", ver="Lux").execute(click)
        if now.button("Lux"):
            Action("Lux", ver="Exp").execute(click)
    except RuntimeError:
        print("Lux init failed")


def grind_lux(count_exp, count_thd):
    countdown(10)
    setup_logging(enable_logging=p.LOG)
    logging.info('Script started')

    print("Entering Lux!")
    while count_exp:
        if not now.button("winrate") and not now.button("Exp"): start_lux()
        if gui.getActiveWindowTitle() != 'LimbusCompany': pause()
        time.sleep(0.5)

        choices = LocateRGB.locate_all(PTH["EnterDoor"], region=REG["pick!"])
        if len(choices) != 0:
            if p.NETZACH: check_enkephalin(shift=227)

            choices.sort(key=lambda box: box[0], reverse=True)
            print(choices)
            win_click(gui.center(choices[0]))
            time.sleep(0.5)

            logging.info("Exp Luxcavation")
        fight(lux=True)

        if now.button("victory"):
            time.sleep(0.5)
            gui.press("Esc")
            if loc.button("Exp"):
                count_exp-= 1
        elif now.button("defeat"):
            time.sleep(0.5)
            if not p.RESTART:
                raise RuntimeError("Luxcavation failed!")
            gui.press("Enter")

    p.SELECTED = p.SELECTED[:6]
    while count_thd:
        if not now.button("winrate") and not now.button("Exp"): start_lux()
        if gui.getActiveWindowTitle() != 'LimbusCompany': pause()

        if now.button("Exp"):
            if p.NETZACH: check_enkephalin(shift=227)

            win_click(225, 492)
            time.sleep(1)
            win_click(553, 721)

            wait_for_condition(lambda: not now.button("EnterSmall", "thd!"))
            time.sleep(0.5)

        choices = LocateRGB.locate_all(PTH["EnterSmall"], region=REG["thd!"])
        if len(choices) != 0:
            choices.sort(key=lambda box: box[1], reverse=True)
            win_click(gui.center(choices[0]))
            time.sleep(0.5)

            logging.info("Thread Luxcavation")
        fight(lux=True)

        if now.button("victory"):
            time.sleep(0.5)
            gui.press("Esc")
            if loc.button("Exp"):
                count_thd -= 1
        elif now.button("defeat"):
            time.sleep(0.5)
            if not p.RESTART:
                raise RuntimeError("Luxcavation failed!")
            gui.press("Enter")

    wait_for_condition(lambda: not now.button("Exp"))
    time.sleep(1)
    gui.press("Esc")
    logging.info("Done with Luxcavation!")