from source.utils.utils import *
from itertools import combinations_with_replacement
import source.utils.params as p

loc_shop = loc_rgb(conf=0.83, wait=False, method=cv2.TM_SQDIFF_NORMED)
shop_click = loc_shop(click=True, wait=5)

item_points = {1: 3, 2: 6, 3: 10, 4: 15}
COMBOS = list(combinations_with_replacement(range(1, 5), 3))

fusion_ranges = {
    1: (9, 10),
    2: (11, 16),
    3: (17, 24),
    4: (25, 45)
}


def combo_counter(combo):
    counter = {}
    for tier in combo:
        if tier in counter:
            counter[tier] += 1
        else:
            counter[tier] = 1
    return counter


def decide_fusion(target_tier, inventory):
    if target_tier not in fusion_ranges: raise ValueError("Invalid target fusion tier")

    low, high = fusion_ranges[target_tier]
    valid_combos = [
        (combo, sum(item_points[t] for t in combo))
        for combo in COMBOS
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

        if best_missing_cost is None        or \
           missing_cost < best_missing_cost or \
          (missing_cost == best_missing_cost and 
           total < best_total_cost):

            best_choice = combo
            best_missing = missing
            best_missing_cost = missing_cost
            best_total_cost = total

    return best_choice, best_missing


def inventory_check():
    coords = {1: [], 2: [], 3: [], 4: []}
    have = {}

    fuse_shelf = screenshot(region=REG["fuse_shelf"]) # bgr
    image = amplify(fuse_shelf)

    for gift in p.GIFTS["all"]:
        try:
            template = amplify(cv2.imread(PTH[gift]))
            res = gui.center(LocateRGB.try_locate(template, image=image, region=REG["fuse_shelf"], conf=0.83))
            print(f"got {gift}")
            have[gift] = res
            fuse_shelf = rectangle(fuse_shelf, (int(res[0] - 982), int(res[1] - 367)), (int(res[0] - 860), int(res[1] - 235)), (0, 0, 0), -1)
        except gui.ImageNotFoundException:
            continue
    for i in range(4, 0, -1):
        found = [gui.center(box) for box in LocateRGB.locate_all(PTH[str(i)], region=REG["fuse_shelf"], image=fuse_shelf, threshold=50, method=cv2.TM_SQDIFF_NORMED)]
        for res in found:
            fuse_shelf = rectangle(fuse_shelf, (int(res[0] - 940), int(res[1] - 317)), (int(res[0] - 818), int(res[1] - 195)), (0, 0, 0), -1)
        for coord in found:
            coords[i].append(coord)
    
    return coords, have


def sell():
    Action("shop", click=(600, 585), ver="sell").execute(click)
    coords, _ = inventory_check()
    for i in range(1, 5):
        if coords[i] != []:
            chain_actions(click, [
                ClickAction(coords[i][0], ver="revenue!"),
                ClickAction((1182, 879)),
                Action("ConfirmInvert", ver="connecting"),
                connection,
                Action("sell", click=(750, 879), ver="shop"),
            ])
            return True
    else:
        Action("sell", click=(750, 879), ver="shop").execute(click)
        return False # nothing to sell

def enhance_special():
    Action("fuse", click=(750, 873), ver="shop").execute(click) # close fusing
    while True:
        if balance(300):
            Action("shop", click=(250, 581), ver="power").execute(click)
            enhance(p.GIFTS["uptie2"]) # enhance special
            Action("power", click=(750, 873), ver="shop").execute(click)
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
    for pos in to_click:
        ClickAction(pos, ver="forecast!").execute(click_rgb)
    chain_actions(click, [
        Action("fuse", click=(1197, 876)),
        Action("Confirm.2"),
        Action("Confirm", ver="fuseButton")
    ])
    to_click.clear()


def fuse():
    time.sleep(0.2)
    coords, have = inventory_check()
    to_click = []
    is_special = False

    # try: # getting rid of useless stone ego gift I hate
    #     res = loc_shop.try_find(p.GIFTS["useless"], "fuse_shelf")
    #     coords[4].append(res)
    # except:
    #     print("no usless ego gift")

    # get powerful ego gift
    if not p.GIFTS["uptie2"] in have.keys():
        missing = actual_fuse(4, coords)
        if missing: return missing
        if loc_shop.button(p.GIFTS["uptie2"], "fuse_shelf", wait=0.2):
            is_special = True

    # get fused ego gift
    elif not p.GIFTS["goal"] in have.keys():
        for name, tier in p.GIFTS["fuse2"].items():
            if not name in have.keys():
                if tier != None:
                    missing = actual_fuse(tier, coords)
                    return missing
                else: # need to fuse
                    for name, tier in p.GIFTS["fuse1"].items():
                        if not name in have.keys():
                            missing = actual_fuse(tier, coords)
                            return missing
                        to_click.append(have[name])
                    perform_clicks(to_click)
                    return None
            to_click.append(have[name])
        perform_clicks(to_click)
    else: raise NotImplementedError

    if is_special: enhance_special()
    return None


def confirm_affinity():
    click_rgb.button(p.GIFTS["checks"][3], "affinity!")
    win_click(1194, 841)

def init_fuse():
    chain_actions(shop_click, [
        Action("shop", click=(469, 602), ver="fuse"),
        lambda: time.sleep(0.1),
        ClickAction((469, 602), ver="keywordSel")
    ])
    click_rgb.button(p.GIFTS["checks"][3], "affinity!")
    win_click(1194, 841)

def fuse_loop():
    skip = 0
    init_fuse()
    try:
        while True:
            missing = fuse()
            if missing:
                Action("fuse", click=(750, 873), ver="shop").execute(click)
                time.sleep(0.1)
                result, skip = buy_loop(missing, skip)
                if not result: return
                else:
                    init_fuse() # open fusing
    except NotImplementedError:
        Action("fuse", click=(750, 873), ver="shop").execute(click)
        print("We got everything!")


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
    shop_shelf = update_shelf()
    output = False
    for gift in p.GIFTS["buy"]:
        try:
            res = loc_shop.try_find(gift, "buy_shelf", image=shop_shelf, comp=0.75, conf=0.7)
            print(f"got {gift}")
            win_click(res)
            conf_gift()
            output = True
            shop_shelf = update_shelf()
        except gui.ImageNotFoundException:
            continue
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

def buy_loop(missing, skip, uptie=True):
    print("need", missing)
    result, missing = buy(missing)
    if not result or not uptie:
        try: 
            if skip < 1 and balance(200):
                Action("shop", click=(1715, 176), ver="keywordRef").execute(shop_click)
                wait_for_condition(
                    condition=lambda: now.button("keywordRef") and not now.button("connecting"), 
                    action=confirm_affinity
                )
                connection()
                skip += 1

                result, missing = buy(missing)
        except RuntimeError:
            print("no cash, sorry")

        if skip < 2 and balance(200):
            win_click(1489, 177) # free reroll
            connection()

            skip += 1
            new_result, _ = buy(missing)
            result = result or new_result
    return result, skip


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
    if not now.button("shop"): return False
    time.sleep(0.2)

    if level == 1:
        ClickAction((250, 581), ver="power").execute(click)
        if not loc_shop.button("+", "fuse_shelf", conf=0.95):
            # we really are on the first floor
            try:
                for gift in p.GIFTS["uptie1"]:
                    enhance(gift)
                Action("power", click=(750, 873), ver="shop").execute(click)
                buy_loop({3: 2}, skip=0, uptie=False)
            except RuntimeError:
                handle_fuckup()
        else:
            # the bot was started midway, so this is not the first floor
            level = 2
            Action("power", click=(750, 873), ver="shop").execute(click)
    if 5 > level > 1 or (not p.SKIP and level == 5):
        fuse_loop()
    
    time.sleep(0.1)
    leave()
    return True