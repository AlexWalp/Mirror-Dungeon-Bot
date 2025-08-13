from source.utils.utils import *
import source.utils.params as p


def far_from_owned(coord, owned_x):
    '''
    Checks whether the ego gift is owned

    Args:
        coord: ego gift coordinates (x, y)
        owned_x: x coordinates of located "owned" icons
    '''
    return all(abs(coord[0] - ox) >= 200 for ox in owned_x)


def find_ego_affinity(owned_x, image):
    '''
    Finds the first affinity EGO gift with the highest tier

    Args:
        owned_x: x coordinates of located "owned" icons
        affinity EGO gifts with those icons are excluded
        image: image with ego gifts that can be adjusted
    Returns:
        tuple (lvl, aff), where lvl is ego gift level and 
        aff is its coordinates (x, y) 
    '''
    affinity = []
    for aff in p.GIFTS:
        affinity += list(filter(
            lambda coord: far_from_owned(coord, owned_x),
            [gui.center(box) for box in LocateRGB.locate_all(PTH[aff["checks"][0]], image=image, region=REG["EGO"])]
        ))
    comp = p.WINDOW[2] / 1920
    return next((
        (lvl, aff)
        for lvl in range(4, 0, -1)
        for aff in affinity
        if LocateRGB.check(
            PTH[f"tier{lvl}"],
            image=image[0:int(42*comp), int((aff[0] - 106)*comp):int((aff[0] - 106 + 66)*comp)],
            wait=False
    )), None)


def get_gift(image, owned_x):
    '''
    Locates EGO gift tiers, affinity, level and their coordinates, then selects the best

    Args:
        image: image with EGO gifts that can be modified
        owned_x: x coordinates of "owned" icons

    Returns:
        image: image with the selected EGO gift replaced with a black rectangle
        (removed from further analysis in case we are selecting multiple gifts)
    '''
    if p.GIFTS[0]["sin"] or not LocateRGB.check(PTH[p.GIFTS[0]["checks"][0]], image=image, region=REG["EGO"], wait=False):
        for gift in [buy for aff in p.GIFTS if aff["sin"] for buy in aff["buy"]]:
            if (coord := LocateRGB.locate(PTH[str(gift)], image=image, region=REG["EGO"], conf=0.84, comp=0.94)) \
            and far_from_owned(gui.center(coord), owned_x):
                point = gui.center(coord)
                win_click(point)
                return rectangle(image, (int(point[0]-100), 0), (int(point[0]+100), 110), (0, 0, 0), -1)

    ego_aff = find_ego_affinity(owned_x, image) # (lvl, coord)

    for lvl in range(4, 0, -1):
        if ego_aff and lvl == ego_aff[0]:
            point = ego_aff[1]
            win_click(point)
            return rectangle(image, (int(point[0]-100), 0), (int(point[0]+100), 110), (0, 0, 0), -1)
        elif boxes := LocateRGB.locate_all(PTH[f"tier{lvl}"], image=image, region=REG["EGO"], method=cv2.TM_SQDIFF_NORMED, threshold=30):
            for box in boxes:
                point = gui.center(box)
                if far_from_owned(point, owned_x):
                    break
            win_click(point)
            return rectangle(image, (int(point[0]-100), 0), (int(point[0]+100), 110), (0, 0, 0), -1)


def grab_EGO():
    '''
    Selects EGO gift(s) on the Ego Gift Selection screen
    retuns whether or not the EGO gift(s) is/are selected
    '''
    if not now.button("EGObin"): return False
    time.sleep(0.8)

    owned_x = [p[0] + p[2] for p in LocateRGB.locate_all(PTH["Owned"], region=REG["Owned"])]
    image = screenshot(region=REG["EGO"])

    cycle = 1
    if p.HARD and now.button("trials"): cycle = 2

    for _ in range(cycle):
        image = get_gift(image, owned_x)
        time.sleep(0.1)

    try:
        ClickAction((1687, 870), ver="Confirm").execute(click)
    except RuntimeError:
        gui.press("enter", 2, 1)
        time.sleep(1)
    return True


def get_card(card):
    '''
    Clicks the selected card

    Args:
        card: (x, y) coordinates
    '''
    chain_actions(click, [
        Action(card, "Card", ver="rewardCount!"),
        Action("Confirm.1", ver="connecting")
    ])

def grab_card():
    '''
    Selects the Reward Card according to specified priority
    Returns whether the card was selected or not
    '''
    if not now.button("encounterreward"): return False

    win_moveTo(1000, 900)
    now_click.button("Cancel") # if was misclicked
    time.sleep(1)
    for i in p.CARD:
        if now.button(f"card{i}", "Card"):
            get_card(f"card{i}")
            wait_for_condition(
                condition=lambda: now.button("encounterreward"), 
                action=lambda: now_click.button("Confirm"), 
                interval=0.1
            )
            return True
    else:
        return False
    

def confirm():
    '''Function to confirm EGO gift pop-ups'''
    if not now_click.button("Confirm"): return False
    win_moveTo(965, 878)
    time.sleep(0.3)
    now_click.button("Confirm")
    return True