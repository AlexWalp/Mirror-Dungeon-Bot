import time, os, sys

print("Loading...")
load_time = time.time()

import numpy as np, pyautogui as gui, cv2, logging
from pyscreeze import Box
import torchfree_ocr as myocr

try:
    BASE_PATH = sys._MEIPASS
except:
    BASE_PATH = os.path.abspath(".")

ocr = myocr.Reader(["en"])

print(f"All packages imported in {(time.time() - load_time):.2f} seconds")


def pth(*args):
    return os.path.join(*args)

### Log config for game.log
logging.basicConfig(
    filename='game.log',  # Log file name
    level=logging.INFO,   # Logging level
    format='%(asctime)s - %(levelname)s - %(message)s'
)

original_excepthook = sys.excepthook

def log_uncaught_exceptions(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    original_excepthook(exc_type, exc_value, exc_traceback)

sys.excepthook = log_uncaught_exceptions
### Log config for game.log end


UI_PATH = pth(BASE_PATH, "ObjectDetection", "UI")


def connection():
    start_time = time.time()
    while check("connecting.png", region=(1548, 66, 293, 74), skip_wait=True):
        if time.time() - start_time > 20: raise RuntimeError("Infinite loop exited")
        time.sleep(0.1)


def detect_char(region=(0, 0, 1920, 1080), digit = False):
    data = np.array(gui.screenshot(region=region))
    results = ocr.readtext(data, decoder='greedy')
    res = ''.join((i[1] for i in results))
    if digit:
        try:
            res = int(''.join(char for char in res if char.isdigit()))
        except ValueError:
            res = None
    return res


def locateAllOnScreenRGBA(image, region=(0, 0, 1920, 1080), conf=0.9, grayscale=True, path=UI_PATH, screenshot=None, A=False):
    if screenshot is None:
        screenshot = gui.screenshot(region=region)
        screenshot = np.array(screenshot)

    if isinstance(image, str):
        template = cv2.imread(pth(path, image), cv2.IMREAD_UNCHANGED)
    else:
        template = image
    x, y, _, _ = region

    if template.shape[-1] == 4:
        b, g, r, alpha = cv2.split(template)
    elif template.shape[-1] == 3:
        b, g, r = cv2.split(template)
        alpha = np.full_like(b, 255, dtype=np.uint8)
    elif len(template.shape) == 2:  # Grayscale image
        alpha = np.full_like(template, 255, dtype=np.uint8)
        bgr_template = cv2.cvtColor(template, cv2.COLOR_GRAY2BGR)
        b, g, r = cv2.split(bgr_template)

    mask = alpha > 0
    mask_uint8 = (mask * 255).astype(np.uint8)

    if grayscale:
        if len(screenshot.shape) != 2:
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
        if len(template.shape) != 2:
            template_gray = cv2.cvtColor(cv2.merge([b, g, r]), cv2.COLOR_BGR2GRAY)
        else:
            template_gray = template
        if A and not np.all(mask):
            result = cv2.matchTemplate(screenshot, template_gray, cv2.TM_CCOEFF_NORMED, mask=mask_uint8)
        else:
            template_gray[~mask] = 0
            result = cv2.matchTemplate(screenshot, template_gray, cv2.TM_CCOEFF_NORMED)
    else:
        screenshot_rgb = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        template_rgb = cv2.merge([b, g, r])
        if A and not np.all(mask):
            result = cv2.matchTemplate(screenshot_rgb, template_rgb, cv2.TM_CCOEFF_NORMED, mask=mask_uint8)
        else:
            template_rgb[~mask] = 0
            result = cv2.matchTemplate(screenshot_rgb, template_rgb, cv2.TM_CCOEFF_NORMED)


    locations = np.where((result + 1)/2 >= conf)
    matches = zip(*locations[::-1])

    match_w, match_h = template.shape[1], template.shape[0]

    for match_x, match_y in matches:
        if region:
            match_x += x
            match_y += y
        yield Box(match_x, match_y, match_w, match_h)


def locateOnScreenRGBA(image, region=(0, 0, 1920, 1080), conf=0.9, grayscale=True, path=UI_PATH, A=False, screenshot=None):
    match = next(locateAllOnScreenRGBA(image, region, conf, grayscale, path, A=A, screenshot=screenshot), None)
    
    if match is None:
        raise gui.ImageNotFoundException
    
    return match


def countdown(seconds): # no more than 99 seconds!
    for i in range(seconds, 0, -1):
        progress = (seconds - i) / seconds
        bar_length = 20
        bar = "[" + "#" * int(bar_length * progress) + "-" * (bar_length - int(bar_length * progress)) + "]"
        
        print(f"Starting in: {i:2} {bar}", end="\r")
        time.sleep(1)
    
    print(" " * (len(f"Starting in: {seconds:2} [--------------------]")), end="\r")
    print("Grinding Time!")


def locate_all(image, conf=0.9, region=(0, 0, 1920, 1080), path=UI_PATH, screenshot=None, threshold = 8):
    positions = []

    try:
        seen = set()
        boxes = locateAllOnScreenRGBA(image, conf=conf, grayscale=False, region=region, path=path, screenshot=screenshot)
        for x, y, w, h in boxes:
            if any((abs(x - fx) <= threshold and abs(y - fy) <= threshold) for fx, fy, _, _ in positions):
                continue
            positions.append(Box(x, y, w, h))
            seen.add((x, y))
    finally: 
        return positions
    

def check(image: str, path=UI_PATH, click=False, region=(0, 0, 1920, 1080), conf=0.9, skip_wait=False, wait=5, error=False, grayscale=True, A=False, screenshot=None):
    if skip_wait:
        wait = 0.1

    for i in range(int(wait * 10)):
        try:
            res = locateOnScreenRGBA(image, region=region, conf=conf, path=path, grayscale=grayscale, A=A, screenshot=screenshot)
            print(f"located {image[:-4]}")

            if click:
                gui.moveTo(gui.center(res), duration=0.1)
                gui.doubleClick(duration=0.1)
                print(f"clicked {image[:-4]}")
    
            return True
        
        except gui.ImageNotFoundException:
            if not skip_wait:
                time.sleep(0.1)
    
    print(f"image {image} not found")
    if error:
        raise RuntimeError("Something unexpected happened. This code still needs debugging")

    return False


def pause():
    while True:
        print("The game is paused...")
        do = input("Press 1 to continue or press 0 to exit: ")
        if do == "0":
            exit()
        if do == "1":
            countdown(5)
            break


def close_limbus():
    if gui.getActiveWindowTitle() == 'LimbusCompany':
        gui.hotkey('alt', 'f4')

    exit()


def locateOnScreenEdges(template, region=(0, 0, 1920, 1080), conf=0.9, path=f"{UI_PATH}/", canny_thresh1=300, canny_thresh2=300, screenshot=None, adaptive=False):
    x, y, w, h = region
    if screenshot is None:
        screenshot = gui.screenshot(region=region)
        screenshot = np.array(screenshot)
    else:
        screenshot = screenshot[y:h, x:w]
    
    template = cv2.imread(pth(path, template), cv2.IMREAD_UNCHANGED)
    
    if template.shape[-1] == 4:
        b, g, r, alpha = cv2.split(template)
    else:
        b, g, r = cv2.split(template)
        alpha = np.full_like(b, 255, dtype=np.uint8)
    
    mask = alpha > 0
    
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)

    if adaptive:
        blurred = cv2.GaussianBlur(screenshot_gray, (5, 5), 0)
        median = np.median(blurred)
        canny_thresh1 = int(max(0, 0.7 * median))
        canny_thresh2 = int(min(255, 1.3 * median))
        print(canny_thresh1, canny_thresh2)
    
    template_merged = cv2.merge([b, g, r])
    template_gray = cv2.cvtColor(template_merged, cv2.COLOR_BGR2GRAY)
    
    template_gray[~mask] = 0

    screenshot_edges = cv2.Canny(screenshot_gray, canny_thresh1, canny_thresh2)
    template_edges = cv2.Canny(template_gray, canny_thresh1, canny_thresh2)
    result = cv2.matchTemplate(screenshot_edges, template_edges, cv2.TM_CCOEFF_NORMED)
    
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    if (max_val + 1) / 2 < conf:
        print(f"No match found with confidence >= {conf} (max: {(max_val + 1) / 2})")
        raise gui.ImageNotFoundException
    
    match_x, match_y = max_loc
    
    print(f"Edge match at ({match_x}, {match_y}) with confidence: {(max_val + 1) / 2}")
    
    match_x += x
    match_y += y
    
    match_w, match_h = template.shape[1], template.shape[0]
    return Box(int(match_x), int(match_y), int(match_w), int(match_h))