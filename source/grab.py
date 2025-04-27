from source.utils.utils import *
import source.utils.params as p


def far_from_owned(coord, owned_x):
    return all(abs(coord[0] - ox) >= 200 for ox in owned_x)


def find_ego_affinity(owned_x):
    affinity = list(filter(
        lambda coord: far_from_owned(coord, owned_x),
        [gui.center(box) for box in LocateRGB.locate_all(PTH["Burn"], region=REG["EGO"])]
    ))
    return next((
        (lvl, aff)
        for lvl in range(4, 0, -1)
        for aff in affinity
        if LocateRGB.check(
            PTH[f"tier{lvl}"],
            region=(int(aff[0] - 106), int(aff[1] - 101), 66, 59),
            wait=False
    )), None)


def get_gift(coord):
    chain_actions(click, [
        lambda: gui.click(coord),
        ClickAction((1687, 870), ver="Confirm")
    ])


def grab_EGO():
    if not now.button("EGObin"): return False

    owned_x = [p[0] + p[2] for p in LocateRGB.locate_all(PTH["Owned"], region=REG["Owned"])]

    for gift in p.GIFTS["buy"]:
        if (coord := LocateRGB.locate(PTH[str(gift)], region=REG["EGO"], conf=0.85, comp=0.94)) \
           and far_from_owned(gui.center(coord), owned_x):
            get_gift(gui.center(coord))
            return True

    ego_aff = find_ego_affinity(owned_x) # (lvl, coord)

    for lvl in range(4, 0, -1):
        if ego_aff and lvl == ego_aff[0]:
            get_gift(ego_aff[1])
            return True
        elif coord := LocateRGB.locate(PTH[f"tier{lvl}"], region=REG["EGO"]):
            get_gift(gui.center(coord))
            return True
    return False


def get_card(card):
    chain_actions(click, [
        Action(card, "Card", ver="rewardCount!"),
        Action("Confirm.1", ver="connecting")
    ])

def grab_card():
    if not now.button("encounterreward"): return False

    gui.moveTo(1000, 900)
    now_click.button("Cancel") # if was misclicked
    time.sleep(1)

    for i in range(1, 5):
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
    if not now_click.button("Confirm"): return False
    gui.moveTo(965, 878)
    now_click.button("Confirm")
    return True