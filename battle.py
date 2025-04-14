from utils import *
from event import event

PATH = pth(UI_PATH, "battle")

sinners = ["YISANG", "DONQUIXOTE" , "ISHMAEL", "RODION", "SINCLAIR", "GREGOR"]

SINNERS = {
    "YISANG"    : ( 351, 207, 196, 285),
    "FAUST"     : ( 547, 207, 196, 285),
    "DONQUIXOTE": ( 743, 207, 196, 285),
    "RYOSHU"    : ( 939, 207, 196, 285),
    "MEURSAULT" : (1135, 207, 196, 285),
    "HONGLU"    : (1331, 207, 196, 285),
    "HEATHCLIFF": ( 351, 492, 196, 285),
    "ISHMAEL"   : ( 547, 492, 196, 285),
    "RODION"    : ( 743, 492, 196, 285),
    "SINCLAIR"  : ( 939, 492, 196, 285),
    "OUTIS"     : (1135, 492, 196, 285),
    "GREGOR"    : (1331, 492, 196, 285)
}

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
            locateOnScreenRGBA(pth("sins", f"{sin}.png"), region=(0, 0, 60, 10), conf=0.75, path=PATH, screenshot=pattern)
            filtered.append(center[0])
        except gui.ImageNotFoundException:
            # print(sin)
            # cv2.imwrite(f"{time.time()}{sin}.png", pattern)
            continue

    return filtered


def select(sinners):
    selected = [gui.center(box) for box in locate_all(pth("battle", "selected.png"))]
    num = len(selected)
    if num < 6:
        for sinner in sinners:
            if not check(pth("battle", "selected.png"), region=SINNERS[sinner], skip_wait=True):
                gui.click(gui.center(SINNERS[sinner]))
                time.sleep(0.1)
                num += 1 
                if num == 6:
                    break
    gui.click(1728, 884) # to battle
    

def chain(gear_start, gear_end, background):
    # Finding skill3 positions
    x, y = gear_start
    length = gear_end[0] - gear_start[0]
    skill_num = (length - 150)//115
    skill3 = []
    for sin in sins.keys():
        skill3 += find_skill3(background, sins[sin], sin=sin)
    moves = [False]*skill_num
    for coord in skill3:
        bin_index = int(min(max((coord - 14 + 40*(2*(coord/length) - 1)) // 115, 0), skill_num - 1))
        moves[bin_index] = True
    print(moves)

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
    is_tobattle = check("TOBATTLE.png", region=(1586, 820, 254, 118), skip_wait=True, path=PATH)
    if not is_tobattle and not check("battleEGO.png", region=(1525, 104, 395, 81), skip_wait=True, path=PATH): return False
    elif is_tobattle: select(sinners)

    print("Entered Battle")

    start_time = time.time()
    while check("loading.png", region=(1577, 408, 302, 91), wait=2):
        if time.time() - start_time > 20: raise RuntimeError("Infinite loop exited")
        print("loading screen...")
        time.sleep(0.5)


    while True:
        if check("battleEGO.png", region=(1525, 104, 395, 81), wait=1, path=PATH):
            gui.click(500, 83, duration=0.1)

            try:
                gear_start = gui.center(locateOnScreenEdges("gear.png", region=(0, 761, 548, 179), conf=0.7, path=PATH))
                gear_end = gui.center(locateOnScreenRGBA("gear2.png", region=(1000, 730, 900, 232), conf=0.8, path=PATH, A=True))
                background = cv2.cvtColor(np.array(gui.screenshot(region=(int(gear_start.x + 100), 775, int(gear_end.x - gear_start.x - 200), 10))), cv2.COLOR_RGB2BGR)
                # background = cv2.cvtColor(np.array(gui.screenshot(f"skill_data/{time.time()}.png", region=(int(gear_start.x + 100), 775, int(gear_end.x - gear_start.x - 200), 10))), cv2.COLOR_RGB2BGR)
                chain(gear_start, gear_end, background)
            except gui.ImageNotFoundException:
                gui.press("p", 1, 0.1)
                gui.press("enter", 1, 0.1)

        if check(pth("event", "eventskip.png"), region=(850, 437, 103, 52), skip_wait=True):
            event()

        if check('loading.png', region=(1577, 408, 302, 91), skip_wait=True)  or \
           check(pth("path", "Move.png"), region=(1805, 107, 84, 86), skip_wait=True) or \
           check(pth("grab", "EGObin.png"), region=(69, 31, 123, 120), skip_wait=True)       or \
           check(pth("grab", "encounterreward.png"), region=(412, 165, 771, 72), skip_wait=True) or \
           check(pth("end", "victory.png"), region=(1478, 143, 296, 116), skip_wait=True):
            
            start_time = time.time()
            while check('loading.png', region=(1577, 408, 302, 91), skip_wait=True):
                if time.time() - start_time > 20: raise RuntimeError("Infinite loop exited")
                time.sleep(0.1)
    
            print("Battle is over")
            logging.info("Battle is over")

            return True
        
        if gui.getActiveWindowTitle() != 'LimbusCompany':
            pause()
        
        if check('pause.png', region=(1724, 16, 83, 84), skip_wait=True, path=PATH):
            time.sleep(1)
        else:
            time.sleep(0.2)