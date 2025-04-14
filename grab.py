from utils import *


PATH = pth(UI_PATH, "grab")
CARD_PATH = pth(PATH, "card")
EGO_PATH = pth(PATH, "levels")



def grab_EGO():
    if not check("EGObin.png", region=(69, 31, 123, 120), skip_wait=True, path=PATH): return False

    owned = locate_all("Owned.png", region=(0, 216, 1725, 50), path=PATH)
    owned_x = [box[0] + box[2] for box in owned]

    ego = locate_all(pth("teams", "Burn", "Burn.png"), region=(0, 309, 1920, 110))
    ego = [gui.center(coord) for coord in ego]

    remove = set()
    for x in owned_x:
        for i in range(len(ego)):
            if abs(x - ego[i][0]) < 200:
                remove.add(i)
    ego = [val for i, val in enumerate(ego) if i not in remove]

    if len(ego) == 1:
        time.sleep(0.2)
        gui.moveTo(ego[0], duration=0.1)
        gui.click(duration=0.1)
    elif len(ego) > 1:
        weights = [0]*len(ego)
        for i in range(len(ego)):
            for lvl in range(4, 0, -1):
                try:
                    locateOnScreenRGBA(f"{lvl}.png", region=(int(ego[i][0] - 106), int(ego[i][1] - 101), 66, 59), conf=0.85, grayscale=False, path=EGO_PATH)
                    weights[i] = lvl
                    break
                except gui.ImageNotFoundException:
                    continue
        index_max = max(range(len(weights)), key=weights.__getitem__)
        time.sleep(0.2)
        gui.moveTo(ego[index_max], duration=0.1)
        gui.click(duration=0.1)
    else:
        for lvl in range(4, 0, -1):
            try:
                res = locateOnScreenRGBA(f"{lvl}.png", region=(0, 309, 1920, 110), grayscale=False, path=EGO_PATH)
                time.sleep(0.2)
                gui.moveTo(gui.center(res), duration=0.1)
                gui.click(duration=0.1)
                break
            except gui.ImageNotFoundException:
                continue
    time.sleep(0.1)
    gui.click(1687, 870)
    check("EGOconfirm.png", region=(791, 745, 336, 104), click=True)
    return True


def grab_card():
    if not check("encounterreward.png", region=(412, 165, 771, 72), skip_wait=True, path=PATH): return False

    gui.moveTo(1000, 900)
    check("Cancel.png", region=(660, 650, 278, 92), skip_wait=True, click=True, path=PATH)

    time.sleep(1)

    for i in range(1, 5):
        if check(f"{i}.png", region=(219, 283, 1531, 242), skip_wait=True, click=True, path=CARD_PATH):

            check("EGOconfirm.png", region=(1118, 754, 189, 70), click=True, error=True) # confirm card

            start_time = time.time()
            while check("encounterreward.png", region=(412, 165, 771, 72), skip_wait=True, path=PATH):
                check("EGOconfirm.png", region=(791, 745, 336, 104), skip_wait=True, click=True)     # confirm ego
                if time.time() - start_time > 20: raise RuntimeError("Infinite loop exited")
                time.sleep(0.1)
            
            return True
    else:
        return False
    

def confirm():
    if not check("EGOconfirm.png", region=(791, 745, 336, 104), skip_wait=True, click=True): return False

    gui.moveTo(965, 878)

    check("EGOconfirm.png", region=(791, 745, 336, 104), skip_wait=True, click=True)
    return True