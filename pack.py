from utils import *


PATH = pth(UI_PATH, "pack")



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

    pr_coords = [] # locating all best packs coordinates
    for card in priority:
        for result in results:
            if best_match(card, result[1]):
                pr_coords.append(gui.center(
                    Box(min(x:= [p[0] for p in result[0]]) + 161, 
                        min(y:= [p[1] for p in result[0]]) + 657, 
                        max(x) - min(x), 
                        max(y) - min(y))))
                break
        
    if pr_coords: # picking best pack
        return within_region(pr_coords[0][0], pr_coords[0][1], regions)
    elif level < 3 and skip != 3:
        return None
    
    bn_coords = [] # locating all worst packs coordinates
    for card in banned:
        for result in results:
            if best_match(card, result[1]):
                bn_coords.append(gui.center(
                    Box(min(x:= [p[0] for p in result[0]]) + 161, 
                        min(y:= [p[1] for p in result[0]]) + 657, 
                        max(x) - min(x), 
                        max(y) - min(y))))
    
    remove = set() # removing S.H.I.T. packs
    if bn_coords:
        for coord in bn_coords:
            i = within_region(coord[0], coord[1], regions)
            remove.add(i)
    filtered = [val for i, val in enumerate(regions) if i not in remove]

    if not filtered and skip != 3: # if all packs are S.H.I.T.
        return None
    elif not filtered:
        print("May Ayin save us all!") # we have to pick S.H.I.T. 
        return 0 # 16 and 5 

    # locating relevant ego gifts in floor rewards
    ego_coords = [gui.center(box) for box in locate_all(pth("teams", "Burn", "littleBurn.png"))]
    owned_x = [box[0] + box[2] for box in locate_all("OwnedSmall.png", path=PATH)]

    remove = set() # excluding owned ego gifts from evaluation
    for x in owned_x:
        for i in range(len(ego_coords)):
            if abs(x - ego_coords[i][0]) < 25:
                remove.add(i)
    ego_coords = [val for i, val in enumerate(ego_coords) if i not in remove]


    weight = [0]*len(filtered) # evaluating each floor based on ego gifts
    if ego_coords:
        for coord in ego_coords:
            i = within_region(coord[0], coord[1], filtered)
            if i == None : continue
            weight[i] += 1
    index_max = max(range(len(weight)), key=weight.__getitem__)
    return regions.index(filtered[index_max])


def pack(level):
    if not check("PackChoice.png", region=(1757, 126, 115, 116), wait=0.2, path=PATH):
        return (False, level)
    
    if check("hardDifficulty.png", region=(893, 207, 115, 44), skip_wait=True, path=PATH):
        gui.moveTo(1349, 64)
        gui.click()

    level = detect_char(region=(725, 151, 449, 52), digit=True)

    print(f"Entering Floor {level}")
    logging.info(f"Floor {level}")

    gui.moveTo(1721, 999)
    time.sleep(0.4)

    skips = 3
    card_count = len(locate_all("PackCard.png", conf=0.85, path=PATH))
    offset = (5 - card_count)*161
    regions = [(182 + offset + 322 * i, 280, 291, 624) for i in range(card_count)]

    print(f"{card_count} Packs")

    for skip in range(skips + 1):
        id = pack_eval(level, regions, skip)
        #gui.screenshot(f"choice/pack{int(time.time())}.png") # debugging
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
            check("refresh.png", region=(1493, 26, 257, 83), wait=1, click=True, path=PATH)
            gui.moveTo(1721, 999)
            time.sleep(2)
    
    if check(pth("path", "Move.png"), region=(1805, 107, 84, 86), error=True) and level != 1:
        start_time = time.time()
        while check(pth("path", "Move.png"), skip_wait=True, region=(1805, 107, 84, 86)):
            if time.time() - start_time > 20: raise RuntimeError("Infinite loop exited")
            time.sleep(0.1)
        check(pth("path", "Move.png"), region=(1805, 107, 84, 86), error=True)
    time.sleep(0.5)
    return (True, level)