from .utils.utils import *


NODE_LIST = ["event", "eventSmall", 
             "eventNew", "eventNewSmall", # Order MATTERS!!!
             "risk",  "riskSmall", 
             "human", "humanSmall", 
             "focus", "focusSmall"]


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
        Bus = LocateRGBA.try_locate(PTH["Bus"], conf=0.77)
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

def get_prob(template_path, image_obj):
    template_obj = cv2.imread(template_path, cv2.COLOR_RGB2GRAY)
    image_obj = cv2.cvtColor(image_obj, cv2.COLOR_RGB2GRAY)
    result = cv2.matchTemplate(template_obj, image_obj, cv2.TM_CCOEFF_NORMED)
    _, res_max, _, _ = cv2.minMaxLoc(result)
    return ((res_max + 1)/2)

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


    Dante = find_danteh()
    if Dante is None: 
        Dante = zoom(-1)
        if Dante is None and find_bus(): hook()
        if Dante is None: Dante = zoom(1)
        if Dante is None: return False
    
    position(Dante)

    if LocateGray.check(PTH["victory"], region=(1478, 143, 296, 116), wait=False): return False

    paths = directions()
    regions = [(624, 101 + i*275, 282, 275) for i in range(3) if paths[i]]

    ## data collection
    # regions_screenshot = [(624, 101 + i*275, 282, 275) for i in range(3)]
    # for i, region in enumerate(regions_screenshot):
    #     gui.screenshot(f"data/{int(time.time())}_{i}", region=region) # debugging
    ## data collection end

    # import random
    # random.shuffle(regions_screenshot)
    # for region in regions_screenshot:
    #     gui.click(gui.center(region))
    #     if enter():
    #         return True
    #     continue

    # for i, region in enumerate(regions):
    #     area = np.array(gui.screenshot(region=region))

    #     coin_prob = get_prob(PTH["coin"], area)
    #     shop_prob = get_prob(PTH["shop"], area)
    #     boss_prob = get_prob(PTH["boss"], area)

    if len(regions) == 1:
        gui.moveTo(gui.center(regions[0]))
        gui.click()
        enter()
        return True

    for node in NODE_LIST:
        conf = 0.95
        if "event" in node:
            conf = 0.9
        
        for region in regions:
            if LocateGray.check(PTH[str(node)], conf=conf, region=region, click=True, wait=False):
                enter()

                logging.info(f"Entering {node}")
                
                return True
    else:
        gui.moveTo(gui.center(regions[0]))
        gui.click()
        enter()
        return True