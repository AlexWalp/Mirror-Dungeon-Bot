from source.utils.utils import *

PROBS = ["VeryHigh", "High", "Normal", "Low", "VeryLow"]


def event():
    if not now.button("eventskip"): return False

    start_time = time.time()
    while True:
        if time.time() - start_time > 100: return False
        if gui.getActiveWindowTitle() != 'LimbusCompany':
            pause()

        for _ in range(3): gui.click(906, 465)

        if now.button("choices"):
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

        now_click.button("Proceed")

        if now.button("check"):
            matches = {
                prob: now.button(prob, "probs")
                for prob in PROBS
            }
            if any(matches.values()):
                for prob in PROBS:
                    if now_click.button(prob, "probs"):
                        click.button("Commence")
                        break

        if now_click.button("Continue"):
            connection()
            return True