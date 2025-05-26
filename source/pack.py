from source.utils.utils import *


def within_region(x, regions):
    comp = 1920 / p.WINDOW[2]
    x = int(x*comp)
    for i, region in enumerate(regions):
        x1, _, w, _ = region
        if x1 < x < x1 + w:
            return i
    else:
        return None

        
def SIFT_matching(template, kp2, des2, search_region, min_matches=40):
    comp = p.WINDOW[2] / 1920
    if comp != 1:
        template = cv2.resize(template, None, fx=comp, fy=comp, interpolation=cv2.INTER_LINEAR)

    sift = cv2.SIFT_create(nfeatures=1700, contrastThreshold=0)
    kp1, des1 = sift.detectAndCompute(template, None)

    if des1 is None or des2 is None: return None

    bf = cv2.BFMatcher(cv2.NORM_L2)
    good = bf.match(des1, des2)

    if len(good) >= min_matches:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, maxIters=200)
        if M is not None and mask is not None:
            matches_mask = mask.ravel().tolist()
            if sum(matches_mask) >= 0.25 * len(good):
                h, w = template.shape
                pts = np.float32([[0,0], [0,h], [w,h], [w,0]]).reshape(-1, 1, 2)
                dst = cv2.perspectiveTransform(pts, M)

                x_coords = dst[:,0,0]
                y_coords = dst[:,0,1]
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)

                if (x_max - x_min < 2 * w) and (y_max - y_min < 2 * h):
                    x, y = int(x_min), int(y_min)
                    return (search_region[0] + x, search_region[1] + y, int(x_max - x), int(y_max - y))
    return None


def pack_eval(level, regions, skip):
    
    # best packs
    priority = p.GIFTS[f"floor{level}"]

    # worst packs (suboptimal time)
    banned = []
    if level == 1 or level == 2:
        banned = ["AutomatedFactory", "TheUnloving", "FaithErosion"]
    if level == 2 or level == 3:
        banned += ["TobeCrushed"]
    if level == 4 or level == 5:
        banned = ["TheNoonofViolet", "MurderontheWARPExpress", "FullStoppedbyaBullet", "VainPride", "CrawlingAbyss", "TimekillingTime", "NocturnalSweeping", "YieldMyFleshtoClaimTheirBones"]

    packs = dict()

    image = cv2.cvtColor(np.array(screenshot(region=(161, 630, 1632, 100))), cv2.COLOR_RGB2GRAY) 
    sift = cv2.SIFT_create(nfeatures=1700, contrastThreshold=0)
    kp2, des2 = sift.detectAndCompute(image, None)   
    for pack in FLOORS[level]:
        if len(packs.keys()) >= 5: break
        template = cv2.imread(PTH[pack], cv2.IMREAD_GRAYSCALE)
        coords = SIFT_matching(template, kp2, des2, (161, 630, 1632, 100))
        if coords:
            x, _ = gui.center(coords)
            if all(abs(x - existing) > 100 for existing in list(packs.values())):
                packs[pack] = x
    
    packs = {
        pack: region_id 
        for pack, x in packs.items() 
        if (region_id := within_region(x, regions)) is not None
    }

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
    
    now.button("hardDifficulty", click=(1349, 64))

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
        id = pack_eval(level, regions, skip)
        #gui.screenshot(f"choice/pack{int(time.time())}") # debugging
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