from source.utils.utils import *
import random


priority = ["Abnormality", "Risk", "Human", "Focused"]
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
    gui.moveTo(object)
    gui.mouseDown()
    gui.moveTo(429, 480, 0.4, tween=gui.easeInOutQuad)
    gui.mouseUp()
    gui.moveTo(429, 610)
    gui.click()


def hook():
    Bus = find_bus()
    if Bus is None : return False
    position(Bus)
    return True


def ck_boss(region, comp):
    image = cv2.cvtColor(np.array(gui.screenshot(region=region)), cv2.COLOR_RGB2BGR)
    red_mask = cv2.inRange(image, np.array([0, 0, 180]), np.array([50, 50, 255]))
    return LocateGray.check(PTH["boss"], red_mask, region=region, wait=False, click=True, comp=comp, conf=0.6)


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
            if LocateGray.check(PTH[suffix], region=(523, 303, 155, 473), wait=False, conf=0.85, comp=comp_val):
                regions[i] = (624, 101 + i * 275, 282, 275)
                break
    return regions


def enter():
    if LocateGray.check(PTH["enter"], region=(1537, 739, 310, 141), click=True, wait=1):
        gui.moveTo(1721, 999)
        time.sleep(0.5)
        return True
    return False


def move(): 
    if not LocateGray.check(PTH["Move"], region=(1805, 107, 84, 86), wait=False) or \
           LocateGray.check(PTH["EGOconfirm"], region=(791, 745, 336, 104), wait=False): return False
    
    # run fail detection
    dead = [gui.center(box) for box in LocateRGB.locate_all(PTH["0"], region=(261, 1019, 1391, 41), conf=0.95, threshold=50)]
    if len(dead) >= 6:
        gui.press("Esc")
        time.sleep(0.5)
        LocateGray.check(PTH["forfeit"], region=(662, 547, 151, 208), click=True)
        time.sleep(0.5)
        LocateGray.check(PTH["ConfirmInvert"], region=(987, 704, 318, 71), click=True)
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
    
    if LocateGray.check(PTH["victory"], region=(1478, 143, 296, 116), wait=False): return False

    regions = directions()
    status = [None, None, None]

    for i, region in regions.items():
        # boss
        if i == 1 and ck_boss(region, comp):
            enter()
            logging.info("Entering Bossfight")
            return True
        # other fight
        elif LocateRGB.check(PTH["coin"], region=region, wait=False, comp=comp):
            if LocateRGB.check(PTH["gift"], region=region, wait=False, comp=comp):
                if LocateGray.check(PTH[f"risk0"], region=region, wait=False, comp=comp, v_comp=v_list[i], conf=0.8) or \
                   any([LocateGray.check(PTH[f"risk1"], region=region, wait=False, comp=comp*(1-0.14*j), v_comp=v_list[i], conf=0.8) for j in range(2)]) or \
                   any([LocateGray.check(PTH[f"risk2"], region=region, wait=False, comp=comp*(1-0.14*j), conf=0.8) for j in range(2)]):
                    status[i] = "Risk"
                    continue
                elif any([LocateGray.check(PTH[f"focus{j}"], region=region, wait=False, comp=comp, v_comp=v_list[i], conf=0.85) for j in range(2)]) or \
                     any([LocateGray.check(PTH[f"focus{j+2}"], region=region, wait=False, comp=comp, conf=0.85) for j in range(2)]):
                    status[i] = "Focused"
                else:
                    status[i] = "Abnormality"
            else:
                status[i] = "Human"
                continue
        # event
        elif LocateGray.check(PTH[f"event0"], region=region, wait=False, click=True, comp=comp, v_comp=v_list[i]) or \
             LocateGray.check(PTH[f"event1"], region=region, wait=False, click=True, comp=comp, v_comp=v_list[i]) or \
             LocateGray.check(PTH[f"event2"], region=region, wait=False, click=True, comp=comp):
            enter()
            logging.info("Entering Event")
            return True
        # shop
        elif LocateGray.check(PTH[f"shop0"], region=region, wait=False, click=True, comp=comp, v_comp=v_list[i], conf=0.8) or \
             LocateGray.check(PTH[f"shop1"], region=region, wait=False, click=True, comp=comp, conf=0.8):
            enter()
            logging.info("Entering Shop")
            return True
    if any(status):
        for node in priority:
            try:
                id = random.choice([i for i, x in enumerate(status) if x == node])
                gui.click(gui.center(regions[id]))
                enter()
                logging.info(f"Entering {node} fight")
                return True
            except IndexError:
                continue
    
    # if we fail:
    for region in regions:
        gui.moveTo(gui.center(region))
        gui.click()
        if enter():
            logging.info(f"Entering unknown node")
            return True
        
    # if we double fail
    logging.info(f"Entering previous node")
    return enter()