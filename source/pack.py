from source.utils.utils import *


def within_region(x, regions):
    for i, region in enumerate(regions):
        x1, _, w, _ = region
        if x1 < x < x1 + w:
            return i
    else:
        return None


def pack_eval(level, regions, skip):
    
    # best packs
    priority = p.PICK[f"floor{level}"]
    print(priority)
    logging.info(f"Pick: {priority}")

    # worst packs (suboptimal time)
    banned = p.IGNORE[f"floor{level}"]
    print(banned)
    logging.info(f"Ignore: {banned}")

    if p.HARD:
        pack_list = HARD_FLOORS[level]
    else:
        pack_list = FLOORS[level]

    packs = dict()

    attempts = 2
    while len(packs.keys()) < len(regions) and attempts > 0:
        sift = SIFTMatcher(region=(161, 630, 1632, 100), nfeatures=2000, contrastThreshold=0)
        for pack in pack_list:
            if len(packs.keys()) >= len(regions): break
            box = sift.locate(PTH[pack])
            if box:
                x, _ = gui.center(box)
                if all(abs(x - existing) > 100 for existing in list(packs.values())):
                    packs[pack] = x
        attempts -= 1
    
    packs = {
        pack: region_id 
        for pack, x in packs.items() 
        if (region_id := within_region(x, regions)) is not None
    }
    logging.info(packs)
    print(packs)
        
    if priority: # picking best pack
        for pr in priority:
            if pr in packs.keys():
                print(f"Entering {pr}")
                logging.info(f"Pack: {pr}")
                return packs[pr]
    if level < 3 and skip != 3 and priority:
        return None
    
    # removing S.H.I.T. packs
    filtered = {pack: i for pack, i in packs.items() if pack not in banned}

    if not filtered and skip != 3: # if all packs are S.H.I.T.
        return None
    elif not filtered:
        print("May Ayin save us all!") # we have to pick S.H.I.T. 
        return 0

    # locating relevant ego gifts in floor rewards
    ego_coords = [gui.center(box) for box in LocateRGB.locate_all(PTH[p.GIFTS["checks"][1]])]
    owned_x = [x + w for x, _, w, _ in LocateRGB.locate_all(PTH["OwnedSmall"])]

    # excluding owned ego gifts from evaluation
    ego_coords = [
        coord for coord in ego_coords
        if all(abs(coord[0] - x) >= 25 for x in owned_x)
    ]

    ids = [i for i in filtered.values()]
    new_regions = [regions[i] for i in ids]
    weight = {i: 0 for i in ids} # evaluating each floor based on ego gifts
    for coord in ego_coords:
        index = within_region(coord[0], new_regions)
        if index is not None:
            weight[ids[index]] += 1

    id = max(weight, key=weight.get)
    name = next((pack for pack, i in filtered.items() if i == id), None)
    print(f"Entering {name}")
    logging.info(f"Pack: {name}")
    return id


def pack(level):
    if not now.button("PackChoice"):
        return (False, level)
    
    if not p.HARD:
        now.button("hardDifficulty", click=(1349, 64))
    else:
        if not now.button("hardDifficulty"):
            win_click(1349, 64)

    for i in range(1, 6):
        if now.button(f"lvl{i}", "lvl"):
            level = i
            break

    print(f"Entering Floor {level}")
    logging.info(f"Floor {level}")

    win_moveTo(1721, 999)
    time.sleep(0.4)

    skips = 3
    card_count = len(LocateRGB.locate_all(PTH["PackCard"], conf=0.85))
    offset = (5 - card_count)*161
    regions = [(182 + offset + 322 * i, 280, 291, 624) for i in range(card_count)]

    print(f"{card_count} Packs")

    # import random
    # id = random.choice([i for i in range(card_count)])


    for skip in range(skips + 1):
        time.sleep(0.2)
        id = pack_eval(level, regions, skip)
        # cv2.imwrite(f"choices/pack{int(time.time())}.png", screenshot()) # debugging
        if not id is None:
            region = regions[id]
            x, y = (region[0] + (region[2] // 2), region[1] + (region[3] // 2))
            win_moveTo(x, y)
            win_dragTo(x, y + 300, duration=0.5, button="left")
            break
        if skip != 3:
            win_click(1617, 62)
            win_moveTo(1721, 999)
            time.sleep(2)
    
    if try_loc.button("Move") and level != 1:
        wait_for_condition(
            condition=lambda: now.button("Move"),
            interval=0.1
        )
        try_loc.button("Move")
    time.sleep(0.5)
    return (True, level)