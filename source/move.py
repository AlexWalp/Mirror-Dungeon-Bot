from source.utils.utils import *


priority = ["Event", "Normal", "Miniboss", "Risky", "Focused"]
v_list = [0.8, 0.9, 1]

def find_danteh(): # looks for high resolution Dante
    for i in range(2):
        try:
            Danteh = LocateRGB.try_locate(PTH[f"Danteh{i}"])
            print("Danteh found")
            x, y = gui.center(Danteh)
            return x, y
        except:
            continue
    return None


def find_bus(): # looks for low resolution Dante
    try:
        Bus = LocateRGB.try_locate(PTH["Bus"])
        print("Danteh found")
        x, y = gui.center(Bus)
        return x, y
    except:
        return None


def zoom(direction):
    for i in range(6):
        Danteh = find_danteh()
        if Danteh:
            return Danteh
        gui.scroll(direction)
        time.sleep(0.1)
    return None


def position(object):
    win_moveTo(object)
    gui.mouseDown()
    win_moveTo(429, 480, duration=0.4, tween=gui.easeInOutQuad)
    gui.mouseUp()
    win_moveTo(429, 710)
    gui.click()


def hook():
    Bus = find_bus()
    if Bus is None : return False
    position(Bus)
    return True


def is_boss(region, comp):
    image = cv2.cvtColor(np.array(screenshot(region=region)), cv2.COLOR_RGB2BGR)
    red_mask = cv2.inRange(image, np.array([0, 0, 180]), np.array([50, 50, 255]))
    return now_click.button("boss", region, image=red_mask, comp=comp, conf=0.6)

def is_risky(_loc, comp, region):
    if _loc.button("risk0", region) or \
   any(_loc.button("risk1", region, comp=comp*(1 - 0.14*j)) for j in range(2)) or \
   any(_loc.button("risk2", region, comp=comp*(1 - 0.14*j), v_comp=None) for j in range(2)):
        return True
    return False

def is_focused(_loc, region):
    if any(_loc.button(f"focus{j}", region, conf=0.85) for j in range(2)) or \
       any(_loc.button(f"focus{j+2}", region, conf=0.85, v_comp=None) for j in range(2)):
        return True
    return False

def is_event(_loc, region):
    if any(_loc.button(f"event{j}", region, conf=0.85) for j in range(2)) or \
           _loc.button("event2", region, conf=0.9, v_comp=None):
        return True
    return False

def is_shop(_loc, region):
    if _loc.button("shop0", region) or \
       _loc.button("shop1", region, v_comp=None):
        return True
    return False

def see_future(_loc, choices):
    if len(choices) == 1: return choices[0]
    for i in choices:
        region = (906, 101 + i * 275, 859, 275)
        _loc = _loc(conf=0.9, v_comp=v_list[i])
        if any(_loc.button(f"event_future{j}", region) for j in range(2)) or \
               _loc.button("event2", region, v_comp=None):
            return i
    return random.choice(choices)


def directions():
    options = {
        0: "_up",
        1: "_forward",
        2: "_down"
    }
    regions = dict()
    for i, suffix in options.items():
        for j in range(2):
            comp_val = 1 - 0.14 * j
            if now.button(suffix, "directions", conf=0.85, comp=comp_val):
                regions[i] = (624, 101 + i * 275, 282, 275)
                break
    return regions


def enter(fight=False):
    if now.button("enter", wait=1):
        click.button("enter")
        win_moveTo(1721, 999)
        connection()
        return True
    return False


def move(): 
    if not now.button("Move") or \
           now.button("Confirm"): return False
    
    # run fail detection
    dead = [gui.center(box) for box in LocateRGB.locate_all(PTH["0"], region=REG["alldead"], conf=0.95, threshold=50)]
    if len(dead) >= 6:
        gui.press("Esc")
        time.sleep(0.5)
        chain_actions(click, [
            Action("forfeit"),
            Action("ConfirmInvert", ver="connecting"),
        ])
        connection()
        return False
    # fail detection end

    comp = 1 # image compression is off

    Dante = find_danteh()
    if Dante is None: 
        Dante = zoom(-1)
        comp = 0.86 # image compression is on
        if Dante is None and find_bus(): hook()
        if Dante is None: Dante = zoom(1)
        if Dante is None: return False
    
    position(Dante)

    if now.button("victory"): return False

    regions = directions()
    status = [None, None, None]

    for i, region in regions.items():
        _loc = LocatePreset(comp=comp, v_comp=v_list[i], conf=0.8, wait=False)
        if i == 1 and is_boss(region, comp):
            enter()
            #loc.button("TOBATTLE", wait=3)
            logging.info("Entering Boss fight")
            return True

        elif now_rgb.button("coin", region, conf=0.9, comp=comp):
            if now_rgb.button("gift", region, conf=0.9, comp=comp):
                if is_risky(_loc, comp, region):
                    status[i] = "Risky"
                    continue
                elif is_focused(_loc, region):
                    status[i] = "Focused"
                    continue
                else:
                    status[i] = "Miniboss"
                    continue
            else:
                status[i] = "Normal"
                continue

        elif is_event(_loc, region):
            status[i] = "Event"
            continue

        elif is_shop(_loc, region):
            win_click(gui.center(regions[i]))
            enter()
            logging.info("Entering Shop")
            return True
    if any(status):
        for node in priority:
            if node in status:
                id = see_future(_loc, [i for i, x in enumerate(status) if x == node])
                win_click(gui.center(regions[id]))
                enter()
                #if node != "Event": loc.button("TOBATTLE", wait=3)
                logging.info(f"Entering {node} {'fight'*(node!='Event')}")
                return True
    
    # if we fail
    win_click(429, 480)
    if enter(): return True

    # if we double fail:
    for i in range(3):
        win_moveTo(gui.center((624, 101 + i * 275, 282, 275)))
        gui.click()
        if enter():
            logging.info(f"Entering unknown node")
            return True