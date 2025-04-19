from source.utils.utils import *


def within_region(x, y, regions):
    for i, region in enumerate(regions):
        x1, y1, w, h = region
        if x1 < x < x1 + w and y1 < y < y1 + h:
            return i
        

def best_match(target, text, threshold=0.6):
    target_len = len(target)
    best_ratio = 0

    empty_len = int((1 - threshold)*len(text))
    text = empty_len*" " + text + empty_len*" "

    for i in range(len(text) - target_len + 1):
        substring = text[i:i + target_len]
        matches = sum(1 for a, b in zip(target, substring) if a == b)
        ratio = matches / target_len

        best_ratio = max(best_ratio, ratio)

    return best_ratio >= threshold


def get_coords(keywords, results):
    coords = []
    for pack in keywords:
        for result in results:
            if best_match(pack, result[1]):
                x = [p[0] for p in result[0]]
                y = [p[1] for p in result[0]]
                coords.append(gui.center((
                    min(x) + 161, 
                    min(y) + 657, 
                    max(x) - min(x), 
                    max(y) - min(y)
                )))
                break
    return coords


def pack_eval(level, regions, skip):
    
    # best packs
    if level == 1: priority = ["Outcast", "Gamblers"]
    elif level == 2: priority = ["Chicken"]
    else: priority = []

    # worst packs (suboptimal time)
    banned = []
    if level == 1 or level == 2:
        banned = ["Factory", "Unloving", "Faith"]
    if level == 2 or level == 3:
        banned += ["Crushed"]
    if level == 4 or level == 5:
        banned = ["Violet", "WARP", "Express", "Full", "Bullet", "Stopped", "Pride", "Abyss", "Time", "Nlocturnal", "Sweeping"]
        # currently Full-Stop floor breaks pathing function, so we avoid it

    # getting text from pack names
    data = np.array(gui.screenshot(region=(161, 657, 1582, 73)))
    results = ocr.readtext(data, decoder='greedy')

    print(results) # testing

    pr_coords = get_coords(priority, results) # locating all best packs coordinates
        
    if pr_coords: # picking best pack
        return within_region(pr_coords[0][0], pr_coords[0][1], regions)
    elif level < 3 and skip != 3:
        return None
    
    bn_coords = get_coords(banned, results) # locating all worst packs coordinates
    
    # removing S.H.I.T. packs
    banned_indices = {within_region(x, y, regions) for x, y in bn_coords}
    filtered = [region for i, region in enumerate(regions) if i not in banned_indices]

    if not filtered and skip != 3: # if all packs are S.H.I.T.
        return None
    elif not filtered:
        print("May Ayin save us all!") # we have to pick S.H.I.T. 
        return 0 # 16 and 5 

    # locating relevant ego gifts in floor rewards
    ego_coords = [gui.center(box) for box in LocateRGB.locate_all(PTH["littleBurn"])]
    owned_x = [x + w for x, _, w, _ in LocateRGB.locate_all(PTH["OwnedSmall"])]

    # excluding owned ego gifts from evaluation
    ego_coords = [
        coord for i, coord in enumerate(ego_coords)
        if all(abs(coord[0] - x) >= 25 for x in owned_x)
    ]

    weight = [0] * len(filtered) # evaluating each floor based on ego gifts
    for coord in ego_coords:
        i = within_region(coord[0], coord[1], filtered)
        if i is not None:
            weight[i] += 1

    index_max = max(range(len(weight)), key=weight.__getitem__)
    return regions.index(filtered[index_max])


def pack(level):
    if not LocateGray.check(PTH["PackChoice"], region=(1757, 126, 115, 116), wait=0.2):
        return (False, level)
    
    if LocateGray.check(PTH["hardDifficulty"], region=(893, 207, 115, 44), wait=False):
        gui.moveTo(1349, 64)
        gui.click()

    level = detect_char(region=(725, 151, 449, 52), digit=True)

    print(f"Entering Floor {level}")
    logging.info(f"Floor {level}")

    gui.moveTo(1721, 999)
    time.sleep(0.4)

    skips = 3
    card_count = len(LocateRGB.locate_all(PTH["PackCard"], conf=0.85))
    offset = (5 - card_count)*161
    regions = [(182 + offset + 322 * i, 280, 291, 624) for i in range(card_count)]

    print(f"{card_count} Packs")

    # import random
    # id = random.choice([i for i in range(card_count)])


    for skip in range(skips + 1):
        id = pack_eval(level, regions, skip)
        #gui.screenshot(f"choice/pack{int(time.time())}") # debugging
        if not id is None:
            region = regions[id]
            name = detect_char(region=(region[0], 657, region[2], 73))
            print(f"Entering {name}")
            logging.info(f"Pack: {name}")
            x, y = (region[0] + (region[2] // 2), region[1] + (region[3] // 2))
            gui.moveTo(x, y)
            gui.dragTo(x, y + 300, 0.5, button="left")
            break
        if skip != 3:
            LocateGray.check(PTH["refresh"], region=(1493, 26, 257, 83), wait=1, click=True)
            gui.moveTo(1721, 999)
            time.sleep(2)
    
    if LocateGray.check(PTH["Move"], region=(1805, 107, 84, 86), error=True) and level != 1:
        start_time = time.time()
        while LocateGray.check(PTH["Move"], region=(1805, 107, 84, 86), wait=False):
            if time.time() - start_time > 20: raise RuntimeError("Infinite loop exited")
            time.sleep(0.1)
        LocateGray.check(PTH["Move"], region=(1805, 107, 84, 86), error=True)
    time.sleep(0.5)
    return (True, level)