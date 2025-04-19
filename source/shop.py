from source.utils.utils import *


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
    to_get = ["glimpse", "dust", "stew", "paraffin", "ash", "book", "hellterfly", "fiery", "wing", "soothe"]
    items = {1: 0, 2: 0, 3: 0, 4: 0}
    coords = {1: [], 2: [], 3: [], 4: []}

    image = cv2.cvtColor(np.array(gui.screenshot(region=(920, 295, 790, 482))), cv2.COLOR_RGB2BGR) # bgr

    for gift in to_get:
        try:
            res = gui.center(LocateRGB.try_locate(PTH[str(gift)], region=(920, 295, 790, 482), conf=0.85))
            print(f"got {gift}")
            cv2.rectangle(image, (int(res[0] - 74 - 920), int(res[1] - 72 - 295)), (int(res[0] - 920), int(res[1] - 295)), (0, 0, 0), -1)
        except gui.ImageNotFoundException:
            continue

    for i in range(4, 0, -1):
        found = [gui.center(box) for box in LocateRGB.locate_all(PTH[str(i)], region=(920, 295, 790, 482), image=image, threshold=50)]
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
            enhance("glimpse") # enhance glimpse
            LocateGray.check(PTH["power"], region=(990, 832, 393, 91))
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
                    LocateGray.check(PTH["ConfirmInvert"], region=(985, 701, 322, 75), click=True)
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
        res = LocateRGB.try_locate(PTH["stone"], region=(920, 295, 790, 482), conf=0.85)
        items[4] = 1
        coords[4].append(gui.center(res))
    except:
        print("no usless ego gift")

    glimpse_ck = False
    # get glimpse
    if not LocateRGB.check(PTH["glimpse"], region=(920, 295, 790, 482), wait=False, conf=0.85):
        combo, missing = decide_fusion(4, items)
        if missing is None:
            for tier in combo:
                to_click.append(coords[tier][0])
                coords[tier].pop(0)
            glimpse_ck = True
        else:
            return missing

    # get soothe
    elif not LocateRGB.check(PTH["soothe"], region=(920, 295, 790, 482), wait=False, conf=0.85):
        if not LocateRGB.check(PTH["book"], region=(920, 295, 790, 482), wait=False, conf=0.85):
            if not LocateRGB.check(PTH["stew"], region=(920, 295, 790, 482), wait=False, conf=0.85):
                combo, missing = decide_fusion(2, items)
                if missing is None:
                    for tier in combo:
                        to_click.append(coords[tier][0])
                        coords[tier].pop(0)
                else:
                    return missing
            elif not LocateRGB.check(PTH["paraffin"], region=(920, 295, 790, 482), wait=False, conf=0.85):
                combo, missing = decide_fusion(1, items)
                if missing is None:
                    for tier in combo:
                        to_click.append(coords[tier][0])
                        coords[tier].pop(0)
                else:
                    return missing
            else:
                try: # fusing book
                    to_click.append(gui.center(LocateRGB.locate(PTH["stew"], region=(920, 295, 790, 482), conf=0.85)))
                    to_click.append(gui.center(LocateRGB.locate(PTH["paraffin"], region=(920, 295, 790, 482), conf=0.85)))
                except gui.ImageNotFoundException:
                    raise RuntimeError("Fusing unexpected error")
                
        elif not LocateRGB.check(PTH["dust"], region=(920, 295, 790, 482), wait=False, conf=0.85):
            combo, missing = decide_fusion(3, items)
            if missing is None:
                for tier in combo:
                    to_click.append(coords[tier][0])
                    coords[tier].pop(0)
            else:
                return missing
        elif not LocateRGB.check(PTH["ash"], region=(920, 295, 790, 482), wait=False, conf=0.85):
            combo, missing = decide_fusion(1, items)
            if missing is None:
                for tier in combo:
                    to_click.append(coords[tier][0])
                    coords[tier].pop(0)
            else:
                return missing
        else:
            try: # fusing soothe
                to_click.append(gui.center(LocateRGB.locate(PTH["book"], region=(920, 295, 790, 482), conf=0.85)))
                to_click.append(gui.center(LocateRGB.locate(PTH["dust"], region=(920, 295, 790, 482), conf=0.85)))
                to_click.append(gui.center(LocateRGB.locate(PTH["ash"], region=(920, 295, 790, 482), conf=0.85)))
            except gui.ImageNotFoundException:
                raise RuntimeError("Fusing unexpected error")
    else: raise NotImplementedError

    if to_click:
        for i in to_click:
            gui.click(i, duration=0.1)
        gui.click(1197, 876, duration=0.1)
        LocateGray.check(PTH["EGOconfirm"], region=(990, 832, 393, 91), click=True)
        LocateGray.check(PTH["EGOconfirm"], region=(791, 745, 336, 104), click=True)

        if glimpse_ck and LocateRGB.check(PTH["glimpse"], region=(920, 295, 790, 482), wait=False, conf=0.85):
            enhance_glimpse()
    return None


def init_fuse():
    time.sleep(0.2)
    gui.click(419, 587)
    LocateGray.check(PTH["fuse"], region=(754, 117, 161, 81))
    time.sleep(0.2)
    gui.click(1281, 517)
    LocateRGB.check(PTH["reBurn"], region=(368, 327, 1160, 442), click=True)
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
    shop_shelf = cv2.cvtColor(np.array(gui.screenshot(region=(809, 300, 942, 402))), cv2.COLOR_RGB2BGR)

    for ignore in ["purchased", "cost"]:
        found = [gui.center(box) for box in LocateRGB.locate_all(PTH[str(ignore)], region=(809, 300, 942, 402), image=shop_shelf, threshold=20)]
        for res in found:
            cv2.rectangle(shop_shelf, (int(res[0] - 70 - 809), int(res[1] - 25 - 300)), (int(res[0] + 70 - 809), int(res[1] + 150 - 300)), (0, 0, 0), -1)

    output = False
    for gift in to_buy:
        if LocateRGB.check(PTH[str(gift)], region=(809, 300, 942, 402), image=shop_shelf, click=True, wait=False, conf=0.85, comp=0.75):
            LocateGray.check(PTH["purchase"], region=(972, 679, 288, 91), click=True)
            connection()
            LocateGray.check(PTH["EGOconfirm"], region=(791, 745, 336, 104), click=True)
            output = True
    time.sleep(0.1)
    if LocateRGB.check(PTH[f"buy{tier}"], region=(809, 300, 942, 402), image=shop_shelf, wait=False, click=True):
        LocateGray.check(PTH["purchase"], region=(972, 679, 288, 91), click=True)
        connection()
        LocateGray.check(PTH["EGOconfirm"], region=(791, 745, 336, 104), click=True)
    else:
        return output
    return True


def buy_loop(to_buy, tier, skip, uptie=True):
    result = buy(to_buy, tier)
    if not result or not uptie:
        if skip < 1 and balance(200):
            gui.click(1715, 176) # reroll for this team type
            LocateRGB.check(PTH["reBurn"], region=(368, 327, 1160, 442), click=True)
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


def enhance(template):
    LocateRGB.check(PTH[str(template)], region=(925, 279, 758, 504), click=True, conf=0.85)
    for i in range(2):
        LocateGray.check(PTH["power"], region=(990, 832, 393, 91), click=True)
        LocateGray.check(PTH["EGOconfirm"], region=(990, 832, 393, 91), click=True)
        gui.moveTo(1215, 939)


def leave():
    time.sleep(0.1)
    gui.click(1705, 967, duration=0.1)
    LocateGray.check(PTH["ConfirmInvert"], region=(985, 701, 322, 75), click=True, error=True)
    

def shop(level, to_buy):
    if not LocateGray.check(PTH["shop"], region=(332, 158, 121, 55), wait=False): return False

    if level == 1:
        gui.click(250, 581) # enhancing
        if not LocateRGB.check(PTH["+"], region=(925, 279, 758, 504), wait=False):
            # we really are on the first floor
            enhance("hellterfly")
            enhance("fiery")
            LocateGray.check(PTH["power"], region=(990, 832, 393, 91))
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

    LocateGray.check(PTH["Move"], region=(1805, 107, 84, 86), error=True)
    return True