from source.utils.utils import *
from source.event import event
import source.utils.params as p


exit_if = ["loading", "Move", "EGObin", "encounterreward", "victory"]

sins = { # bgr values
    "wrath"   : (  0,   0, 254),
    "gloom"   : (239, 197,  26),
    "sloth"   : ( 49, 205, 251),
    "lust"    : (  0, 108, 254),
    "pride"   : (213,  75,   1),
    "gluttony": (  1, 228, 146),
    "envy"    : (222,   1, 150),
}


def find_skill3(background, known_rgb, threshold=40, min_pixels=10, max_pixels=100, sin="envy"):
    median_rgb = np.median(background, axis=(0, 1)).astype(int)
    blended_rgb = (median_rgb * 0.45 + np.array(known_rgb) * 0.55).astype(int)
    
    lower_bound = np.clip(blended_rgb - threshold, 0, 255)
    upper_bound = np.clip(blended_rgb + threshold, 0, 255)
    mask = cv2.inRange(background, lower_bound, upper_bound)

    # collecting clusters (colors that are directly connected)
    num_labels, _, stats, centroids = cv2.connectedComponentsWithStats(mask)
    
    cluster_centers = []

    # some pixel value checks (colors in cluster may be disconnected)
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        center = centroids[i]
        
        if min_pixels <= area <= max_pixels:
            x = int(center[0])
            x1, x2 = max(0, x-25), min(background.shape[1], x+25)
            y1, y2 = 0, 10
            
            region_mask = mask[y1:y2, x1:x2]
            similar_pixels = np.count_nonzero(region_mask)

            if 150 >= similar_pixels >= 20:
                cluster_centers.append(center)
    # print(sin)
    # print(centroids)
    # print(cluster_centers)

    # merging neightbouring clusters
    merged = []
    while cluster_centers:
        current = cluster_centers.pop()
        group = [c for c in cluster_centers if np.linalg.norm(current - c) <= 50]
        cluster_centers = [c for c in cluster_centers if np.linalg.norm(current - c) > 50]
        merged.append(np.mean([current] + group, axis=0))
    
    # filter by color patterns
    filtered = []
    while merged:
        center = merged.pop()
        x = int(center[0])
        x1, x2 = max(0, x-30), min(background.shape[1], x+30)
        y1, y2 = 0, 10
        region_mask = mask[y1:y2, x1:x2]

        pattern = np.zeros((y2-y1, x2-x1), dtype=np.uint8)
        pattern = np.maximum(pattern, region_mask)
        try:
            if pattern.shape[1] < 33 : raise gui.ImageNotFoundException
            LocateGray.try_locate(PTH[str(sin)], pattern, region=(0, 0, pattern.shape[1], 10), conf=0.74, method=cv2.TM_CCORR_NORMED)
            filtered.append(center[0])
        except gui.ImageNotFoundException:
            # print(sin)
            # cv2.imwrite(f"{time.time()}{sin}.png", pattern)
            continue

    return filtered


def select(sinners):
    selected = [gui.center(box) for box in LocateGray.locate_all(PTH["selected"])]
    num = len(selected)
    if num < 6:
        for name in sinners:
            if not now.button("selected", SINNERS[name]):
                gui.click(gui.center(SINNERS[name]))
                time.sleep(0.1)
                num += 1 
                if num == 6:
                    break

    gui.click(1728, 884) # to battle
    loading_halt()


def chain(gear_start, gear_end, background):
    # Finding skill3 positions
    x, y = gear_start
    length = gear_end[0] - gear_start[0]
    skill_num = int(round((length - 140)/115))
    skill3 = []
    for sin in sins.keys():
        skill3 += find_skill3(background, sins[sin], sin=sin)
    moves = [False]*skill_num
    for coord in skill3:
        bin_index = int(min(max((coord - 14 + 80*(2*((coord + gear_start[0] + 100)/1920) - 1)) // 115, 0), skill_num - 1)) # for full hd
        moves[bin_index] = True
    # print(gear_start)
    # print(gear_end)
    # print(length)
    # print(moves)

    # Chaining
    gui.moveTo(gear_start)
    gui.mouseDown()
    x += 75
    y -= 46
    for i in range(skill_num):
        if moves[i]:
            gui.moveTo(x + 68, y + 200)
        else:
            gui.moveTo(x + 68, y + 70)
        x += 115
    
    gui.press("enter", 1, 0.1)
    gui.mouseUp()


def fight():
    is_tobattle = now.button("TOBATTLE")
    is_battle   = now.button("battleEGO")
    if not is_tobattle and not is_battle: return False
    if is_tobattle: select(p.SELECTED)

    print("Entered Battle")
    last_error = 0
    while True:
        ck = False
        if loc.button("battleEGO", wait=1):
            gui.click(500, 83, duration=0.1)
            ck = True
            try:
                gear_start = gui.center(LocateEdges.try_locate(PTH["gear"], region=(0, 761, 900, 179), conf=0.7))
                gear_end = gui.center(LocateEdges.try_locate(PTH["gear2"], region=(350, 730, 1570, 232), conf=0.7))
                background = cv2.cvtColor(np.array(gui.screenshot(region=(int(gear_start.x + 100), 775, int(gear_end.x - gear_start.x - 200), 10))), cv2.COLOR_RGB2BGR)
                # background = cv2.cvtColor(np.array(gui.screenshot(f"skill_data/{time.time()}.png", region=(int(gear_start.x + 100), 775, int(gear_end.x - gear_start.x - 200), 10))), cv2.COLOR_RGB2BGR)
                chain(gear_start, gear_end, background)
            except gui.ImageNotFoundException:
                gui.press("p", 1, 0.1)
                gui.press("enter", 1, 0.1)

        if now.button("eventskip"):
            ck = True
            event()

        for i in exit_if:
            if now.button(i):
                if i == "loading": loading_halt()
                print("Battle is over")
                logging.info("Battle is over")
                return True
        
        if gui.getActiveWindowTitle() != 'LimbusCompany':
            ck = True
            pause()
        
        if now.button("pause"):
            ck = True
            time.sleep(1)
        else:
            time.sleep(0.2)
        
        # stuck check
        if ck == False:
            if last_error != 0:
                if time.time() - last_error > 30:
                    raise RuntimeError
            else:
                last_error = time.time()
        else:
            last_error = 0