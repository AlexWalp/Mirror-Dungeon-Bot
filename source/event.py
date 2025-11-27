from source.utils.utils import *

PROBS = ["VeryHigh", "High", "Normal", "Low", "VeryLow"]

favorites = ["chicken", "factory"]

def event():
    if not now.button("eventskip"): return False

    start_time = time.time()
    while True:
        if time.time() - start_time > 100: return False
        if (win := gui.getActiveWindowTitle()) != p.LIMBUS_NAME: pause(win)

        for _ in range(3): win_click(906, 465, delay=0.01)
        
        if now.button("choices"):
            time.sleep(0.1)
            if now_click.button("textNew", "textEGO"): 
                if wait_for_condition(lambda: now.button("choices"), interval=0.1, timer=1): continue
            if now_click.button("textLvl", "textEGO"): 
                if wait_for_condition(lambda: now.button("choices"), interval=0.1, timer=1): continue
            if any(now_click.button(f"choice_{favorite}", "textEGO") for favorite in favorites): continue

            egos = LocateGray.locate_all(PTH["textEGO"], region=REG["textEGO"], conf=0.85)

            if not egos:
                for choice in [316, 520, 730]:
                    win_click(1348, choice, delay=0)
                    if wait_for_condition(lambda: now.button("choices"), interval=0.5, timer=2): continue
                else:
                    continue
            
            affinity = []
            for aff in p.TEAM:
                affinity += LocateGray.locate_all(PTH[f"{aff.lower()}_choice"], region=REG["textEGO"], conf=0.85)
            win = LocateGray.locate(PTH["textWIN"], region=REG["textEGO"], conf=0.85)

            filtered = []
            priority = []
            for box in egos:
                if not win or abs(box[1] - win[1]) > 80:
                    filtered.append(box)

                    for aff in affinity:
                        if abs(box[1] - aff[1]) < 80:
                            priority.append(box)
            
            if priority:
                sorted(priority, key=lambda x: x[1])            
                win_click(gui.center(priority[0]), delay=0)
                continue
            
            if filtered:
                sorted(priority, key=lambda x: x[1])            
                win_click(gui.center(filtered[0]), delay=0)
            else:
                win_click(1356, 498, delay=0)

        now_click.button("Proceed")
        now_click.button("CommenceBattle")

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