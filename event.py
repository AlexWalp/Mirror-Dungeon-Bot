from utils import *

PROBS = ["VeryHigh.png", "High.png", "Normal.png", "Low.png", "VeryLow.png"]
PATH = pth(UI_PATH, "event")


def event():
    if not check("eventskip.png", region=(850, 437, 103, 52), skip_wait=True, path=PATH): return False

    start_time = time.time()
    while True:
        if time.time() - start_time > 100: raise RuntimeError("Infinite loop exited")

        for _ in range(3): gui.click(906, 465)

        if check("choices.png", region=(1036, 152, 199, 77), skip_wait=True, path=PATH):
            egos = locate_all("textEGO.png", region=(1031, 254, 713, 516), path=PATH)
            print(egos)
            if not egos:
                gui.click(1348, 316)
                continue
            try:
                win = locateOnScreenRGBA("textWIN.png", region=(1031, 254, 713, 516), path=PATH)
                for box in egos:
                    if abs(box[1] - win[1]) > 80:
                        gui.click(gui.center(box))
                        break
                else:
                    gui.click(1356, 498)
            except gui.ImageNotFoundException:
                gui.click(gui.center(egos[0]))

        check("Proceed.png", region=(1539, 906, 316, 126), click=True, skip_wait=True, path=PATH)

        if check("check.png", region=(1265, 434, 430, 87), skip_wait=True, path=PATH):
            time.sleep(0.3)
            for prob in PROBS:
                if check(pth("sinprob", prob), region=(42, 876, 1427, 74), click=True, skip_wait=True, path=PATH):
                    break
            check("Commence.png", region=(1539, 906, 316, 126), click=True, path=PATH)

        if check("Continue.png", region=(1539, 906, 316, 126), skip_wait=True, click=True, path=PATH):
            connection()
            return True