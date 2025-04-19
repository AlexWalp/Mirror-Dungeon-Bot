from source.utils.utils import *

PROBS = ["VeryHigh", "High", "Normal", "Low", "VeryLow"]


def event():
    if not LocateGray.check(PTH["eventskip"], region=PTH["eventskip"], wait=False): return False

    start_time = time.time()
    while True:
        if time.time() - start_time > 100: raise RuntimeError("Infinite loop exited")

        for _ in range(3): gui.click(906, 465)

        if LocateGray.check(PTH["choices"], region=(1036, 152, 199, 77), wait=False):
            egos = LocateGray.locate_all(PTH["textEGO"], region=REG["textEGO"])
            print(egos)
            if not egos:
                gui.click(1348, 316)
                continue
            try:
                win = LocateGray.try_locate(PTH["textWIN"], region=REG["textEGO"])
                for box in egos:
                    if abs(box[1] - win[1]) > 80:
                        gui.click(gui.center(box))
                        break
                else:
                    gui.click(1356, 498)
            except gui.ImageNotFoundException:
                gui.click(gui.center(egos[0]))

        LocateGray.check(PTH["Proceed"], region=(1539, 906, 316, 126), click=True, wait=False)

        if LocateGray.check(PTH["check"], region=REG["check"], wait=False):
            time.sleep(0.3)
            for prob in PROBS:
                if LocateGray.check(PTH[str(prob)], region=(42, 876, 1427, 74), click=True, wait=False):
                    break
            LocateGray.check(PTH["Commence"], region=(1539, 906, 316, 126), click=True)

        if LocateGray.check(PTH["Continue"], region=(1539, 906, 316, 126), click=True, wait=False):
            connection()
            return True