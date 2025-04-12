from utils import *

PATH = pth(UI_PATH, "path")

NODE_LIST = ["event.png", "eventSmall.png", 
             "eventNew.png", "eventNewSmall.png", # Order MATTERS!!!
             "risk.png",  "riskSmall.png", 
             "human.png", "humanSmall.png", 
             "focus.png", "focusSmall.png"]


def find_danteh(): # looks for high resolution Dante
    for i in range(2):
        try:
            Danteh = locateOnScreenRGBA(f"Danteh{i}.png", confidence=0.8, path=PATH)
            print("Danteh found")
            x, y = gui.center(Danteh)
            return x, y
        except:
            continue
    return None


def find_bus(): # looks for low resolution Dante
    try:
        Bus = locateOnScreenRGBA("Bus.png", confidence=0.55, grayscale=False, path=PATH)
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


def directions():
    img = gui.screenshot(region=(545, 405, 30, 240))
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    cv2.rectangle(img, (10, 0), (30, 230), 0, -1)
    cv2.rectangle(img, (0, 150), (10, 230), 0, -1)


    max_val = np.max(img)
    _, binary = cv2.threshold(img, max_val - 5, 255, cv2.THRESH_BINARY)

    num_labels, _, _, centroids = cv2.connectedComponentsWithStats(binary)

    values = np.array([False]*3) # up, middle and bottom

    for i in range(1, num_labels):
        if 0 < centroids[i][1] < 75:
            values[0] = True
        elif 75 < centroids[i][1] < 150:
            values[1] = True
        elif 150 < centroids[i][1] < 240:
            values[2] = True

    return values


def enter():
    check("enter.png", region=(1537, 739, 310, 141), click=True, error=True, path=PATH)
    gui.moveTo(1721, 999)
    time.sleep(1)


def move(): 
    if not check("Move.png", region=(1805, 107, 84, 86), skip_wait=True, path=PATH) or \
           check("EGOconfirm.png", region=(791, 745, 336, 104), skip_wait=True): return False
    
    # run fail detection
    dead = [gui.center(box) for box in locate_all(pth("end", "0.png"), conf=0.9, region=(261, 1019, 1391, 41), threshold=50)]
    if len(dead) >= 6:
        gui.press("Esc")
        time.sleep(0.5)
        check(pth("end", "forfeit.png"), region=(662, 547, 151, 208), click=True)
        time.sleep(0.5)
        check(pth("end", "ConfirmInvert.png"), click=True, region=(987, 704, 318, 71))
        connection()
        return False
    # fail detection end

    Dante = find_danteh()
    if Dante is None: 
        Dante = zoom(-1)
        if Dante is None and find_bus(): hook()
        if Dante is None: Dante = zoom(1)
        if Dante is None: return False
    
    position(Dante)

    if check(pth("end", "victory.png"), region=(1478, 143, 296, 116), skip_wait=True): return False

    paths = directions()
    regions = [(624, 101 + i*275, 282, 275) for i in range(3) if paths[i]]

    ## data collection (Sorry I forgot to comment it earlier)
    # regions_screenshot = [(624, 101 + i*275, 282, 275) for i in range(3)]
    # for i, region in enumerate(regions_screenshot):
    #     gui.screenshot(f"data/{int(time.time())}_{i}.png", region=region) # debugging
    ## data collection end

    if len(regions) == 1:
        gui.moveTo(gui.center(regions[0]))
        gui.click()
        enter()
        return True

    for node in NODE_LIST:
        conf = 0.9
        if "event" in node:
            conf = 0.8
        
        for region in regions:
            if check(node, region=region, click=True, skip_wait=True, conf=conf, path=PATH):
                enter()

                logging.info(f"Entering {node}")
                
                return True
    else:
        gui.moveTo(gui.center(regions[0]))
        gui.click()
        enter()
        return True