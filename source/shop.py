from source.utils.utils import *
from itertools import combinations_with_replacement, cycle
import source.utils.params as p

loc_shop = loc_rgb(conf=0.83, wait=False, method=cv2.TM_SQDIFF_NORMED)
shop_click = loc_shop(click=True, wait=5)

item_points = {1: 3, 2: 6, 3: 10, 4: 15}
COMBOS = list(combinations_with_replacement(range(1, 5), 3))
get_tier3 = [((1, 1, 4), 21), ((1, 2, 3), 19), ((1, 2, 4), 24), ((1, 3, 3), 23), ((2, 2, 2), 18), ((2, 2, 3), 22)]

EXTRA = []
for i in range(3, 6):
    EXTRA += list(combinations_with_replacement(range(1, 5), i))



fusion_ranges = {
    1: (9, 10),
    2: (11, 16),
    3: (17, 24),
    4: (25, 45)
}

super_ranges = {
    1: (9, 9),
    2: (10, 14),
    3: (15, 21),
    4: (22, 75)
}


def combo_counter(combo):
    counter = {}
    for tier in combo:
        if tier in counter:
            counter[tier] += 1
        else:
            counter[tier] = 1
    return counter


def decide_fusion(target_tier, inventory, depth=0):
    if target_tier not in fusion_ranges: raise ValueError("Invalid target fusion tier")

    if p.SUPER == "shop":
        combos = COMBOS
        ranges = fusion_ranges
    else:
        combos = EXTRA
        ranges = super_ranges

    low, high = ranges[target_tier]
    valid_combos = [
        (combo, sum(item_points[t] for t in combo))
        for combo in combos
        if low <= sum(item_points[t] for t in combo) <= high
    ]
    
    best_choice = None
    best_missing = None
    best_missing_cost = None
    best_total_cost = None

    for combo, total in valid_combos:
        needed = combo_counter(combo)
        missing = {}
        missing_cost = 0
        for tier, count_needed in needed.items():
            have = len(inventory[tier])
            if have < count_needed:
                deficit = count_needed - have
                missing[tier] = deficit
                missing_cost += deficit * item_points[tier]
        
        if missing.get(4, 0) > 0: # we are not buying tier 4 for fusion, no way
            continue
        
        if p.SUPER == "shop" and not depth and missing.get(3, 0) == 1 and \
           sum([missing.get(i, 0) for i in range(1, 2)]) == 0:
            new_have = {tier: len(items) for tier, items in inventory.items()}
            skip_missing = True
            for i in range(1, 5): # update inventory
                if i in needed.keys():
                    for _ in range(needed[i]):
                        if i == 3 and skip_missing:
                            skip_missing = False
                            continue
                        if new_have[i] > 0:
                            new_have[i] -= 1
            new_combo = None
            best_price = None
            for tier3_combo, price in get_tier3: # I don't want to do a recursion
                need = combo_counter(tier3_combo)
                for tier, count_needed in need.items():
                    if new_have[tier] < count_needed:
                        break
                else:
                    if best_price is None or price < best_price:
                        new_combo = tier3_combo
                        best_price = price
            # new_combo, new_missing = decide_fusion(3, new_inventory, 1)
            if new_combo:
                combo = new_combo
                missing = {}
                missing_cost = 0
                total = total - item_points[3] + best_price

        if best_missing_cost is None        or \
           missing_cost < best_missing_cost or \
          (missing_cost == best_missing_cost and 
           total < best_total_cost):

            best_choice = combo
            best_missing = missing
            best_missing_cost = missing_cost
            best_total_cost = total

    return best_choice, best_missing


def inventory_check(reg, h):
    coords = {1: [], 2: [], 3: [], 4: []}
    have = {}

    fuse_shelf = screenshot(region=reg)
    image = amplify(fuse_shelf)

    for gift in [all for aff in p.GIFTS for all in aff["all"]]:
        try:
            template = amplify(cv2.imread(PTH[gift]))
            x, y = gui.center(LocateRGB.try_locate(template, image=image, region=reg, conf=0.88))
            print(f"got {gift}")
            have[gift] = (x, y, h)
            fuse_shelf = rectangle(fuse_shelf, (int(x - 62 - reg[0]), int(y - 72 - reg[1])), (int(x + 60 - reg[0]), int(y + 60 - reg[1])), (0, 0, 0), -1)
        except gui.ImageNotFoundException:
            continue
    
    for aff in p.GIFTS:
        if not p.AGGRESSIVE_FUSING or not aff["sin"]: # ignore same affinity gifts if not aggressive or slash/pierce/blunt team
            found = [gui.center(box) for box in LocateRGB.locate_all(PTH[aff["checks"][4]], region=reg, image=fuse_shelf, threshold=50, method=cv2.TM_SQDIFF_NORMED)]
            for res in found:
                fuse_shelf = rectangle(fuse_shelf, (int(res[0] - 103 - reg[0]), int(res[1] - 105 - reg[1])), (int(res[0] + 19 - reg[0]), int(res[1] + 17 - reg[1])), (0, 0, 0), -1)
        
    for i in range(4, 0, -1):
        found = [gui.center(box) for box in LocateRGB.locate_all(PTH[str(i)], region=reg, image=fuse_shelf, threshold=50, method=cv2.TM_SQDIFF_NORMED)]
        for res in found:
            fuse_shelf = rectangle(fuse_shelf, (int(res[0] - 20 - reg[0]), int(res[1] - 22 - reg[1])), (int(res[0] + 102 - reg[0]), int(res[1] + 100 - reg[1])), (0, 0, 0), -1)
            x, y = res
            coords[i].append((x, y, h))
    return coords, have

def browse(loops):
    for _ in range(loops):
        win_moveTo(1227, 380)
        gui.mouseDown()
        win_moveTo(1227, 254, duration=0.3)
        gui.mouseUp()

        win_click(1227, 380)

def concat(dict1, dict2):
    for key in dict2:
        if key in dict1:
            dict1[key].extend(dict2[key])
        else:
            dict1[key] = dict2[key]
    return dict1

def get_inventory():
    coords, have = inventory_check(REG["fuse_shelf"], 0)
    if now_rgb.button("scroll"):
        h = 1
        while not now_rgb.button("scroll.0"):
            browse(1)
            new_coords, new_have = inventory_check(REG["fuse_shelf_low"], h)
            coords = concat(coords, new_coords)
            have.update(new_have)
            h += 1
    
        for _ in range(10): gui.scroll(1)
        win_moveTo(1227, 234)
        time.sleep(0.4)
    return coords, have


def buy_known(aff):
    shop_shelf = update_shelf()
    output = False
    for gift in aff["buy"]:
        try:
            res = loc_shop.try_find(gift, "buy_shelf", image=shop_shelf, comp=0.75, conf=0.7)
            print(f"got {gift}")
            win_click(res)
            conf_gift()
            time.sleep(0.1)
            shop_shelf = update_shelf()
            output = True
        except gui.ImageNotFoundException:
            continue
    return shop_shelf, output

def buy_affinity(aff):
    box = True
    while box:
        shop_shelf = update_shelf()
        box = LocateRGB.locate(PTH[aff["checks"][0]], region=REG["buy_shelf"], image=shop_shelf, method=cv2.TM_SQDIFF_NORMED, comp=0.88, conf=0.8)
        if box: 
            res = gui.center(box)
            win_click(res)
            conf_gift()
            time.sleep(0.1)
    return shop_shelf, False

def buy_some(rerolls=1, priority=False):
    time.sleep(0.2)
    iterations = rerolls + 1
    for i in range(iterations):
        for aff in p.GIFTS:
            if not priority or not aff["sin"]: # just by same affinity
                print('bruh')
                buy_affinity(aff)
            else: # buy only necessary stuff
                buy_known(aff)

        if rerolls and balance(200):
            rerolls -= 1
            Action(p.SUPER, click=(1715, 176), ver="keywordRef").execute(shop_click)
            wait_for_condition(
                condition=lambda: now.button("keywordRef") and not now.button("connecting"), 
                action=confirm_affinity
            )
            connection() 


def sell():
    Action(p.SUPER, click=(600, 585), ver="sell").execute(click)
    coords, _ = inventory_check(REG["fuse_shelf"], 0)
    for i in range(1, 5):
        if coords[i] != []:
            chain_actions(click, [
                ClickAction(coords[i][0][:2], ver="revenue!"),
                ClickAction((1182, 879)),
                Action("ConfirmInvert", ver="connecting"),
                connection,
                Action("sell", click=(750, 879), ver=p.SUPER),
            ])
            return True
    else:
        Action("sell", click=(750, 879), ver=p.SUPER).execute(click)
        return False # nothing to sell

def enhance_special():
    Action("fuse", click=(750, 873), ver=p.SUPER).execute(click) # close fusing
    while True:
        if balance(300):
            Action(p.SUPER, click=(250, 581), ver="power").execute(click)
            enhance(p.GIFTS[p.IDX]["uptie2"]) # enhance special
            Action("power", click=(750, 873), ver=p.SUPER).execute(click)
            break
        elif not sell(): break
    init_fuse() # back to fusing


def actual_fuse(tier, coords):
    to_click = []
    combo, missing = decide_fusion(tier, coords)
    if not missing:
        for tier in combo:
            to_click.append(coords[tier][0])
            coords[tier].pop(0)
        perform_clicks(to_click)
        return None
    else: return missing

def perform_clicks(to_click):
    to_click = sorted(to_click, key=lambda x: x[2])
    h = 0
    for pos in to_click:
        if pos[2] - h > 0:
            browse(pos[2] - h)
            h = pos[2]
            time.sleep(0.2)
        ClickAction(pos[:2], ver="forecast!").execute(click_rgb)
    if h:
        win_moveTo(1227, 380)
        for _ in range(10): gui.scroll(1)
    chain_actions(click, [
        Action("fuse", click=(1197, 876)),
        Action("Confirm.2"),
        Action("Confirm", ver="fuseButton")
    ])
    to_click.clear()


def set_affinity(i):
    if p.IDX == i: return
    p.IDX = i
    ClickAction((469, 602), ver="keywordSel").execute(shop_click)
    confirm_affinity()
    time.sleep(0.2)

def search_have(have, fuse_type, idx):
    missing = 0
    iterations = 0
    names = []
    if name := next((key for key, value in p.GIFTS[idx][f"fuse{fuse_type + 1}"].items() if value is None), None):
        if name in have:
            iterations += 2
        else:
            names += list(p.GIFTS[idx][f"fuse{fuse_type}"].keys())

    names += [key for key, value in p.GIFTS[idx][f"fuse{fuse_type + 1}"].items() if value is not None]
    for name in names:
        if name not in have.keys():
                missing += 1
        iterations += 1
    return missing/iterations

def fuse_search(have):
    advanced_fusing = []
    for i in range(len(p.GIFTS)):
        if p.GIFTS[i]["sin"] and not p.GIFTS[i]["goal"][0] in have.keys():
            advanced_fusing.append((i, search_have(have, 1, i), 1))
        if p.HARD and p.GIFTS[i]["sin"] and not p.GIFTS[i]["goal"][1] in have.keys():
            advanced_fusing.append((i, search_have(have, 3, i), 3))
    advanced_fusing.sort(key=lambda item: (item[1], item[0]))
    return advanced_fusing

def fuse():
    time.sleep(0.2)
    coords, have = get_inventory()
    to_click = []
    fuse_type = 0
    advanced = False

    # get powerful ego gift
    for i in range(len(p.GIFTS)):
        if not p.GIFTS[i]["uptie2"] in have.keys():
            p.AGGRESSIVE_FUSING = True
            _, missing = decide_fusion(4, coords)
            if missing: 
                if i == 0 or p.DONE_FUSING:
                    return missing
                else:
                    advanced = True
                    break
            else:
                set_affinity(i)
                actual_fuse(4, coords)
                if loc_shop.button(p.GIFTS[p.IDX]["uptie2"], "fuse_shelf", wait=0.2):
                    if p.IDX == 0:
                        enhance_special()
                return None
    else:
        p.AGGRESSIVE_FUSING = False

    # get recipe ego gifts
    if advanced or not p.AGGRESSIVE_FUSING: 
        advanced_fusing = fuse_search(have)
        if advanced_fusing:
            i, _, fuse_type = advanced_fusing[0]
            set_affinity(i)
        else:
            p.DONE_FUSING = True
            if not p.AGGRESSIVE_FUSING:
                raise NotImplementedError
            else:
                return None

    if fuse_type:
        for name, tier in p.GIFTS[p.IDX][f"fuse{fuse_type+1}"].items():
            if not name in have.keys():
                if tier != None:
                    missing = actual_fuse(tier, coords)
                    return missing
                else: # need to fuse
                    for name, tier in p.GIFTS[p.IDX][f"fuse{fuse_type}"].items():
                        if not name in have.keys():
                            missing = actual_fuse(tier, coords)
                            return missing
                        to_click.append(have[name])
                    perform_clicks(to_click)
                    return None
            to_click.append(have[name])
        perform_clicks(to_click)

    return None


def confirm_affinity():
    click_rgb.button(p.GIFTS[p.IDX]["checks"][3], "affinity!")
    win_click(1194, 841)

def init_fuse():
    chain_actions(shop_click, [
        Action(p.SUPER, click=(469, 602), ver="fuse"),
        lambda: time.sleep(0.1),
        ClickAction((469, 602), ver="keywordSel")
    ])
    confirm_affinity()

def fuse_loop():
    skip = 0
    init_fuse()
    try:
        while True:
            missing = fuse()
            if missing:
                Action("fuse", click=(750, 873), ver=p.SUPER).execute(click)
                time.sleep(0.1)
                result = buy_loop(missing)
                if not result: return
                else:
                    init_fuse() # open fusing
    except NotImplementedError:
        Action("fuse", click=(750, 873), ver=p.SUPER).execute(click)
        print("We got everything!")
        buy_some(2)


def balance(money):
    answer_me = True
    bal = -1
    start_time = time.time()
    # gui.screenshot(f"cost{time.time()}.png", region=(857, 175, 99, 57)) # debugging
    while bal == -1:
        if time.time() - start_time > 20: raise RuntimeError("Infinite loop exited")
        digits = []
        for i in range(9, -1, -1):
            pos = [gui.center(box) for box in LocateRGB.locate_all(PTH[f"cost{i}"], region=(857, 175, 99, 57), threshold=7, conf=0.9, method=cv2.TM_SQDIFF_NORMED)]
            for coord in pos:
                if all(abs(coord[0] - existing_coord) > 7 for _, existing_coord in digits):
                    digits.append((i, coord[0]))
        digits = sorted(digits, key=lambda x: x[1])

        bal = ""
        for i in digits: bal += str(i[0])
        bal = int(bal or -1)
        if bal != -1 and bal < money and answer_me: 
            time.sleep(0.2)
            answer_me = False # you game me an answer, but not your own
            bal = -1 # I will ask again
    print("money", bal)
    return bal >= money


def conf_gift():
    connection()
    Action("purchase", ver="Confirm").execute(click)
    wait_for_condition(
        condition=lambda: now.button("Confirm"),
        action=lambda: now_click.button("Confirm"),
        interval=0.1
    )

def update_shelf():
    shop_shelf = screenshot(region=REG["buy_shelf"])
    shop_shelf = rectangle(shop_shelf, (52, 33), (224, 195), (0, 0, 0), -1)
    for ignore in ["purchased", "cost"]:
        found = [gui.center(box) for box in LocateRGB.locate_all(PTH[str(ignore)], region=REG["buy_shelf"], image=shop_shelf, threshold=20)]
        for res in found:
            shop_shelf = rectangle(shop_shelf, (int(res[0] - 70 - 809), int(res[1] - 25 - 300)), (int(res[0] + 70 - 809), int(res[1] + 150 - 300)), (0, 0, 0), -1)
    return shop_shelf

def filter_x_distance(points, x_tol=2, y_tol=25):
    points = sorted(points, key=lambda p: p[0])
    result = []
    for p in points:
        if all(abs(p[0] - q[0]) >= x_tol or abs(p[1] - q[1]) > y_tol for q in result):
            result.append(p)
    return result

def get_shop(shop_shelf):
    tier1 = [gui.center(box) for box in LocateRGB.locate_all(PTH["buy1"], region=REG["buy_shelf"], image=shop_shelf, threshold=3.5, conf=0.92, method=cv2.TM_SQDIFF_NORMED)]
    tier4 = [gui.center(box) for box in LocateRGB.locate_all(PTH["buy4"], region=REG["buy_shelf"], image=shop_shelf, threshold=10, conf=0.92, method=cv2.TM_SQDIFF_NORMED)]
    tier1 = filter_x_distance(tier1)
    have = {1: [], 2: [], 3: []}
    visited = set()
    for i, pt_i in enumerate(tier1):
        if i in visited: continue
        count = 1
        for j in range(i + 1, len(tier1)):
            pt_j = tier1[j]
            if all(abs(pt_i[k] - pt_j[k]) <= 25 for k in range(2)):
                visited.add(j)
                count += 1
        have[min(count, 3)].append(pt_i)
    have[1] = [
        (fx, fy) for (fx, fy) in have[1]
        if not any(abs(fx - x) <= 25 and abs(fy - y) <= 25 for (x, y) in tier4)
    ]
    return have

def buy(missing):
    output = False
    for aff in p.GIFTS:
        if aff["sin"]:
            shop_shelf, out = buy_known(aff)
        else:
            shop_shelf, out = buy_affinity(aff)
        if out: output = True

    if output: return True, missing # got build

    gained = {1: 0, 2: 0, 3: 0}
    for tier in sorted(missing.keys(), reverse=True):
        for _ in range(missing[tier]):
            have = get_shop(shop_shelf)
            print(f"got {have}")
            if have[tier]:
                win_click(have[tier][0])
                conf_gift()
                shop_shelf = update_shelf()
                gained[tier] += 1
            else:
                return output, {key: missing[key] - gained[key] for key in missing} # got something
    return True, {} # got everything

def buy_loop(missing, floor1=False):
    print("need", missing)
    result, missing = buy(missing)
    if not result or floor1:
        try: 
            if balance(200):
                Action(p.SUPER, click=(1715, 176), ver="keywordRef").execute(shop_click)
                wait_for_condition(
                    condition=lambda: now.button("keywordRef") and not now.button("connecting"), 
                    action=confirm_affinity
                )
                connection()

                result, missing = buy(missing)

            if (not result or floor1) and balance(200):
                win_click(1489, 177)
                connection()

                new_result, _ = buy(missing)
                result = result or new_result
        except RuntimeError:
            print("no cash, sorry")
    return result


def enhance(template):
    shop_click.button(str(template), "fuse_shelf")
    for i in range(2):
        chain_actions(click, [
            Action("power"),
            Action("Confirm.2", ver="power")
        ])
        win_moveTo(1215, 939)

def leave():
    chain_actions(click, [
        ClickAction((1705, 967)),
        Action("ConfirmInvert", ver="Move")
    ])


def shop(level):
    if now.button("shop"): p.SUPER = "shop"
    elif not p.HARD or not now.button("supershop"): return False
    else: p.SUPER = "supershop"

    time.sleep(0.2)

    if level == 1:
        ClickAction((250, 581), ver="power").execute(click)
        if not loc_shop.button("+", "fuse_shelf", conf=0.95):
            # we really are on the first floor
            try:
                for gift in p.GIFTS[0]["uptie1"]:
                    enhance(gift)
                Action("power", click=(750, 873), ver=p.SUPER).execute(click)
                time.sleep(0.3)
                buy_loop({3: 2}, floor1=True)
            except RuntimeError:
                handle_fuckup()
        else:
            # the bot was started midway, so this is not the first floor
            level = 2
            Action("power", click=(750, 873), ver=p.SUPER).execute(click)
    if 5 > level > 1 or (not p.SKIP and level == 5):
        buy_some(rerolls=0, priority=True)
        fuse_loop()
    
    time.sleep(0.1)
    leave()
    return True