from source.utils.utils import *


def grab_EGO(to_buy):
    if not LocateGray.check(PTH["EGObin"], region=(69, 31, 123, 120), wait=False): return False

    owned = LocateRGB.locate_all(PTH["Owned"], region=(0, 216, 1725, 50))
    owned_x = [x + w for x, _, w, _ in owned]

    ego = [
        center for gift in to_buy
        if (res := LocateRGB.locate(PTH[str(gift)], region=(0, 295, 1920, 100), conf=0.85, comp=0.94)) is not None
        and all(abs((center := gui.center(res))[0] - ox) >= 200 for ox in owned_x)
    ]

    if len(ego) == 1:
        time.sleep(0.2)
        gui.moveTo(ego[0], duration=0.1)
        gui.click(duration=0.1)
    elif len(ego) > 1:
        weights = [0]*len(ego)
        for i in range(len(ego)):
            for lvl in range(4, 0, -1):
                try:
                    LocateRGB.try_locate(PTH[f"tier{lvl}"], region=(int(ego[i][0] - 106), int(ego[i][1] - 101), 66, 59))
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
                res = LocateRGB.try_locate(PTH[f"tier{lvl}"], region=(0, 309, 1920, 110))
                time.sleep(0.2)
                gui.moveTo(gui.center(res), duration=0.1)
                gui.click(duration=0.1)
                break
            except gui.ImageNotFoundException:
                continue
    time.sleep(0.1)
    gui.click(1687, 870)
    LocateGray.check(PTH["EGOconfirm"], region=REG["EGOconfirm"], click=True)
    return True


def grab_card():
    if not LocateGray.check(PTH["encounterreward"], region=REG["encounterreward"], wait=False): return False

    gui.moveTo(1000, 900)
    LocateGray.check(PTH["Cancel"], region=REG["Cancel"], wait=False, click=True)

    time.sleep(1)

    for i in range(1, 5):
        if LocateGray.check(PTH[f"card{i}"], region=(219, 283, 1531, 242), wait=False, click=True):

            LocateGray.check(PTH["EGOconfirm"], region=(1118, 754, 189, 70), click=True, error=True) # confirm card

            start_time = time.time()
            while LocateGray.check(PTH["encounterreward"], region=REG["encounterreward"], wait=False):
                LocateGray.check(PTH["EGOconfirm"], region=REG["EGOconfirm"], wait=False, click=True)     # confirm ego
                if time.time() - start_time > 20: raise RuntimeError("Infinite loop exited")
                time.sleep(0.1)
            
            return True
    else:
        return False
    

def confirm():
    if not LocateGray.check(PTH["EGOconfirm"], region=REG["EGOconfirm"], wait=False, click=True): return False
    gui.moveTo(965, 878)
    LocateGray.check(PTH["EGOconfirm"], region=REG["EGOconfirm"], wait=False, click=True)
    return True