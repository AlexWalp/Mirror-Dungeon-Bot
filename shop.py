from utils import *


PATH = pth(UI_PATH, "shop")

item_points = {1: 3, 2: 6, 3: 10, 4: 15}

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
    if target_tier not in fusion_ranges: raise ValueError("Invalid target fusion tier.")

    low, high = fusion_ranges[target_tier]
    
    combos = []
    for i in range(1, 5):
        for j in range(i, 5):
            for k in range(j, 5):
                combos.append((i, j, k))
    
    valid_combos = []
    for combo in combos:
        total = sum(item_points[t] for t in combo)
        if low <= total <= high:
            valid_combos.append((combo, total))
    
    best_choice = None
    best_missing = None
    best_missing_cost = None
    best_total_cost = None

    for combo, total in valid_combos:
        needed = combo_counter(combo)
        missing = {}
        missing_cost = 0
        for tier, count_needed in needed.items():
            have = inventory.get(tier, 0)
            if have < count_needed:
                deficit = count_needed - have
                missing[tier] = deficit
                missing_cost += deficit * item_points[tier]
        
        if missing.get(4, 0) > 0: # we are not buying tier 4 for fusion, no way
            continue

        if missing_cost == 0:
            return combo, None

        if best_missing_cost is None        or \
           missing_cost < best_missing_cost or \
          (missing_cost == best_missing_cost and 
           total < best_total_cost):

            best_choice = combo
            best_missing = missing
            best_missing_cost = missing_cost
            best_total_cost = total

    if best_choice is None: raise ValueError
    return best_choice, best_missing


def inventory_check():
    to_get = ["glimpse.png", "dust.png", "stew.png", "paraffin.png", "ash.png", "book.png", "hellterfly.png", "fiery.png", "wing.png", "soothe.png"]
    items = {1: 0, 2: 0, 3: 0, 4: 0}
    coords = {1: [], 2: [], 3: [], 4: []}

    image = np.array(gui.screenshot(region=(920, 295, 790, 482))) # bgr

    for gift in to_get:
        try:
            res = gui.center(locateOnScreenRGBA(pth("teams", "Burn", "gifts", gift), region=(920, 295, 790, 482), grayscale=False, conf=0.85, A=True))
            print(f"got {gift}")
            cv2.rectangle(image, (int(res[0] - 74 - 920), int(res[1] - 72 - 295)), (int(res[0] - 920), int(res[1] - 295)), (0, 0, 0), -1)
        except gui.ImageNotFoundException:
            continue

    for i in range(4, 0, -1):
        found = [gui.center(box) for box in locate_all(pth("teams", "Burn", "gifts", f"{i}.png"), region=(920, 295, 790, 482), screenshot=image, threshold=50)]
        for res in found:
            cv2.rectangle(image, (int(res[0] - 37 - 920), int(res[1] - 37 - 295)), (int(res[0] + 37 - 920), int(res[1] + 37 - 295)), (0, 0, 0), -1)
        for coord in found:
            items[i] += 1
            coords[i].append(coord)
    
    return items, coords


def enhance_glimpse():
    time.sleep(0.1)
    gui.click(750, 873, duration=0.1) # close fusing
    while True:
        if balance(300):
            time.sleep(0.1)
            gui.click(250, 581, duration=0.1) # enhancing
            enhance(pth("teams", "Burn", "gifts", "glimpse.png")) # enhance glimpse
            check("power.png", region=(990, 832, 393, 91), path=PATH)
            connection()
            time.sleep(0.3)
            gui.click(750, 873, duration=0.1) # enhancing done
            time.sleep(0.1)
            break
        else:
            gui.click(600, 585) # sell
            _, coords = inventory_check()
            for i in range(1, 5):
                if coords[i] != []:
                    gui.click(coords[i][0])
                    gui.click(1182, 879)
                    check(pth("end", "ConfirmInvert.png"), region=(985, 701, 322, 75), click=True)
                    connection()
                    time.sleep(0.5)
                    gui.click(750, 879, duration=0.1) # exit
                    time.sleep(0.2)
                    break
            else:
                time.sleep(0.1)
                gui.click(750, 879, duration=0.1) # exit
                break # nothing to sell
    init_fuse() # back to fusing


def fuse():
    items, coords = inventory_check()
    to_click = []

    try: # getting rid of useless stone ego gift I hate
        res = locateOnScreenRGBA(pth("teams", "Burn", "gifts", "stone.png"), region=(920, 295, 790, 482), grayscale=False)
        items[4] = 1
        coords[4].append(gui.center(res))
    except:
        print("no usless ego gift")

    glimpse_ck = False
    # get glimpse
    if not check(pth("teams", "Burn", "gifts", "glimpse.png"), region=(920, 295, 790, 482), grayscale=False, skip_wait=True, conf=0.85, A=True):
        combo, missing = decide_fusion(4, items)
        if missing is None:
            for tier in combo:
                to_click.append(coords[tier][0])
                coords[tier].pop(0)
            glimpse_ck = True
        else:
            return missing

    # get soothe
    elif not check(pth("teams", "Burn", "gifts", "soothe.png"), region=(920, 295, 790, 482), grayscale=False, skip_wait=True):
        if not check(pth("teams", "Burn", "gifts", "book.png"), region=(920, 295, 790, 482), grayscale=False, skip_wait=True):
            if not check(pth("teams", "Burn", "gifts", "stew.png"), region=(920, 295, 790, 482), grayscale=False, skip_wait=True):
                combo, missing = decide_fusion(2, items)
                if missing is None:
                    for tier in combo:
                        to_click.append(coords[tier][0])
                        coords[tier].pop(0)
                else:
                    return missing
            elif not check(pth("teams", "Burn", "gifts", "paraffin.png"), region=(920, 295, 790, 482), grayscale=False, skip_wait=True):
                combo, missing = decide_fusion(1, items)
                if missing is None:
                    for tier in combo:
                        to_click.append(coords[tier][0])
                        coords[tier].pop(0)
                else:
                    return missing
            else:
                try: # fusing book
                    to_click.append(gui.center(locateOnScreenRGBA(pth("teams", "Burn", "gifts", "stew.png"), region=(920, 295, 790, 482), grayscale=False)))
                    to_click.append(gui.center(locateOnScreenRGBA(pth("teams", "Burn", "gifts", "paraffin.png"), region=(920, 295, 790, 482), grayscale=False)))
                except gui.ImageNotFoundException:
                    raise RuntimeError("Fusing unexpected error")
                
        elif not check(pth("teams", "Burn", "gifts", "dust.png"), region=(920, 295, 790, 482), grayscale=False, skip_wait=True):
            combo, missing = decide_fusion(3, items)
            if missing is None:
                for tier in combo:
                    to_click.append(coords[tier][0])
                    coords[tier].pop(0)
            else:
                return missing
        elif not check(pth("teams", "Burn", "gifts", "ash.png"), region=(920, 295, 790, 482), grayscale=False, skip_wait=True):
            combo, missing = decide_fusion(1, items)
            if missing is None:
                for tier in combo:
                    to_click.append(coords[tier][0])
                    coords[tier].pop(0)
            else:
                return missing
        else:
            try: # fusing soothe
                to_click.append(gui.center(locateOnScreenRGBA(pth("teams", "Burn", "gifts", "book.png"), region=(920, 295, 790, 482), grayscale=False)))
                to_click.append(gui.center(locateOnScreenRGBA(pth("teams", "Burn", "gifts", "dust.png"), region=(920, 295, 790, 482), grayscale=False)))
                to_click.append(gui.center(locateOnScreenRGBA(pth("teams", "Burn", "gifts", "ash.png"), region=(920, 295, 790, 482), grayscale=False)))
            except gui.ImageNotFoundException:
                raise RuntimeError("Fusing unexpected error")
    else: raise NotImplementedError

    if to_click:
        for i in to_click:
            gui.click(i, duration=0.1)
        gui.click(1197, 876, duration=0.1)
        check("EGOconfirm.png", region=(990, 832, 393, 91), click=True)
        check("EGOconfirm.png", region=(791, 745, 336, 104), click=True)

        if glimpse_ck and check(pth("teams", "Burn", "gifts", "glimpse.png"), region=(920, 295, 790, 482), grayscale=False, skip_wait=True, conf=0.85, A=True):
            enhance_glimpse()
    return None


def init_fuse():
    time.sleep(0.2)
    gui.click(419, 587)
    check("fuse.png", region=(754, 117, 161, 81), path=PATH)
    time.sleep(0.2)
    gui.click(1281, 517)
    check(pth("teams", "Burn", "reBurn.png"), region=(368, 327, 1160, 442), click=True)
    time.sleep(0.1)
    gui.click(1194, 841)


def fuse_loop(to_buy):
    skip = 0
    init_fuse()
    try:
        while True:
            missing = fuse()
            if missing:
                gui.click(750, 873) # close fusing
                result = True
                for tier in sorted(missing.keys(), reverse=True):
                    for i in range(missing[tier]):
                        result, skip = buy_loop(to_buy, tier, skip)
                if not result:
                    break
                else:
                    init_fuse() # open fusing
    except NotImplementedError:
        gui.click(750, 873) # close fusing
        print("We got everything!")


def balance(money):
    start_time = time.time()
    while True:
        if time.time() - start_time > 20: raise RuntimeError("Infinite loop exited")
        bal = detect_char(region=(857, 175, 99, 57), digit=True)
        if bal != None: break
    if bal >= money: return True
    return False


def buy(to_buy, tier):
    shop_shelf = np.array(gui.screenshot(region=(809, 300, 942, 402)))

    for ignore in ["purchased.png", "cost.png"]:
        found = [gui.center(box) for box in locate_all(pth("shop", ignore), region=(809, 300, 942, 402), screenshot=shop_shelf, threshold=20)]
        for res in found:
            cv2.rectangle(shop_shelf, (int(res[0] - 70 - 809), int(res[1] - 25 - 300)), (int(res[0] + 70 - 809), int(res[1] + 150 - 300)), (0, 0, 0), -1)

    output = False
    for gift in to_buy:
        if check(pth("teams", "Burn", "buy", gift), region=(809, 300, 942, 402), click=True, skip_wait=True, grayscale=False, screenshot=shop_shelf):
            check("purchase.png", region=(972, 679, 288, 91), click=True, path=PATH)
            check("EGOconfirm.png", region=(791, 745, 336, 104), click=True)
            output = True
    time.sleep(0.1)
    if check(pth(UI_PATH, "teams", "Burn", "buy", f"{tier}.png"), region=(809, 300, 942, 402), skip_wait=True, grayscale=False, click=True, screenshot=shop_shelf):
        check("purchase.png", region=(972, 679, 288, 91), click=True, path=PATH)
        check("EGOconfirm.png", region=(791, 745, 336, 104), click=True)
    else:
        return output
    return True


def buy_loop(to_buy, tier, skip, uptie=True):
    result = buy(to_buy, tier)
    if not result or not uptie:
        if skip < 1 and balance(200):
            gui.click(1715, 176) # reroll for this team type
            check(pth("teams", "Burn", "reBurn.png"), region=(368, 327, 1160, 442), click=True)
            gui.click(1194, 841)
            connection()
            skip += 1

            result = buy(to_buy, tier)
        if skip < 2 and balance(200):
            gui.click(1489, 177) # free reroll
            connection()

            skip += 1
            result = buy(to_buy, tier)
    return result, skip


def enhance(image):
    check(image, region=(925, 279, 758, 504), conf=0.85, click=True, grayscale=False)
    for i in range(2):
        check("power.png", region=(990, 832, 393, 91), click=True, path=PATH)
        check("EGOconfirm.png", region=(990, 832, 393, 91), click=True)
        gui.moveTo(1215, 939)


def leave():
    time.sleep(0.1)
    gui.click(1705, 967, duration=0.1)
    check(pth("end", "ConfirmInvert.png"), region=(985, 701, 322, 75), click=True, error=True)
    

def shop(level, to_buy):
    if not check("shop.png", region=(332, 158, 121, 55), skip_wait=True, path=PATH): return False

    if level == 1:
        gui.click(250, 581) # enhancing
        if not check("+.png", path=PATH, region=(925, 279, 758, 504), skip_wait=True, grayscale=False):
            # we really are on the first floor
            enhance(pth("teams", "Burn", "gifts", "hellterfly.png"))
            enhance(pth("teams", "Burn", "gifts", "fiery.png"))
            check("power.png", region=(990, 832, 393, 91), path=PATH)
            time.sleep(0.1)
            gui.click(750, 873) # enhancing done

            buy_loop(to_buy, tier=3, skip=0, uptie=False)

            leave()
        else:
            # the bot was started midway, so this is not the first floor
            level = 2
            time.sleep(0.1)
            gui.click(750, 873) # enhancing done
    if level == 5:
        leave()
    elif level > 1:
        fuse_loop(to_buy)
        leave()

    check(pth("path", "Move.png"), region=(1805, 107, 84, 86), error=True)
    return True