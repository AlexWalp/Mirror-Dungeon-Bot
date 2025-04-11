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

logging.basicConfig(
    filename='game.log',  # Log file name
    level=logging.INFO,   # Logging level
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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


def locateAllOnScreenRGBA(button, region=(0, 0, 1920, 1080), confidence=0.8, grayscale=True, path=UI_PATH, screenshot=None, A=False):
    if screenshot is None:
        screenshot = gui.screenshot(region=region)
        screenshot = np.array(screenshot)

    template = cv2.imread(pth(path, button), cv2.IMREAD_UNCHANGED)
    x, y, _, _ = region

    if template.shape[-1] == 4:
        b, g, r, alpha = cv2.split(template)
    else:
        b, g, r = cv2.split(template)
        alpha = np.full_like(b, 255, dtype=np.uint8)

    mask = alpha > 0
    mask_uint8 = (mask * 255).astype(np.uint8)

    if grayscale:
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
        template_gray = cv2.cvtColor(cv2.merge([b, g, r]), cv2.COLOR_BGR2GRAY)
        if A and not np.all(mask):
            result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED, mask=mask_uint8)
        else:
            template_gray[~mask] = 0
            result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    else:
        screenshot_rgb = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        template_rgb = cv2.merge([b, g, r])
        if A and not np.all(mask):
            result = cv2.matchTemplate(screenshot_rgb, template_rgb, cv2.TM_CCOEFF_NORMED, mask=mask_uint8)
        else:
            template_rgb[~mask] = 0
            result = cv2.matchTemplate(screenshot_rgb, template_rgb, cv2.TM_CCOEFF_NORMED)


    locations = np.where(result >= confidence)
    matches = zip(*locations[::-1])

    match_w, match_h = template.shape[1], template.shape[0]

    for match_x, match_y in matches:
        if region:
            match_x += x
            match_y += y
        yield Box(match_x, match_y, match_w, match_h)


def locateOnScreenRGBA(button, region=(0, 0, 1920, 1080), confidence=0.8, grayscale=True, path=UI_PATH, A=False, screenshot=None):
    match = next(locateAllOnScreenRGBA(button, region, confidence, grayscale, path, A=A, screenshot=screenshot), None)
    
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


def locate_all(imagefullpath, conf, region=(0, 0, 1920, 1080), path=UI_PATH, screenshot=None, threshold = 8):
    positions = []

    try:
        seen = set()
        boxes = locateAllOnScreenRGBA(imagefullpath, confidence=conf, grayscale=False, region=region, path=path, screenshot=screenshot)
        for x, y, w, h in boxes:
            if any((abs(x - fx) <= threshold and abs(y - fy) <= threshold) for fx, fy, _, _ in positions):
                continue
            positions.append(Box(x, y, w, h))
            seen.add((x, y))
    finally: 
        return positions
    

def check(button: str, path=UI_PATH, click=False, region=(0, 0, 1920, 1080), conf=0.8, skip_wait=False, wait=5, error=False, grayscale=True, A=False, screenshot=None):
    if skip_wait:
        wait = 0.1

    for i in range(int(wait * 10)):
        try:
            res = locateOnScreenRGBA(button, region=region, confidence=conf, path=path, grayscale=grayscale, A=A, screenshot=screenshot)
            print(f"located {button[:-4]}")

            if click:
                gui.moveTo(gui.center(res), duration=0.1)
                gui.doubleClick(duration=0.1)
                print(f"clicked {button[:-4]}")
    
            return True
        
        except gui.ImageNotFoundException:
            if not skip_wait:
                time.sleep(0.1)
    
    print(f"image {button} not found")
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



def find_image_with_brightness_filter(image_path, region, threshold=80, click=False): # for shop

    screenshot = gui.screenshot(region=region)
    screenshot = np.array(screenshot)

    hsv = cv2.cvtColor(screenshot, cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(hsv)

    mask = v >= threshold
    v[~mask] = 0

    hsv_filtered = cv2.merge([h, s, v])
    screenshot_filtered = cv2.cvtColor(hsv_filtered, cv2.COLOR_HSV2BGR)
    cv2.imshow("eblanishe", screenshot_filtered)
    cv2.waitKey()

    template = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    if template.shape[-1] == 4:
        template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)

    screenshot_filtered = screenshot_filtered.astype(np.uint8)
    template = template.astype(np.uint8)

    result = cv2.matchTemplate(screenshot_filtered, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    confidence_threshold = 0.8  
    if max_val >= confidence_threshold:
        found_x, found_y = max_loc[0] + region[0], max_loc[1] + region[1]
        if click:
            gui.click(found_x, found_y, duration=0.1)
        return found_x, found_y

    raise gui.ImageNotFoundException


def create_filtered_template(image_path, output_path, threshold=80): # template creation

    template = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    if template.shape[-1] == 4:
        template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)

    hsv = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    mask = v >= threshold
    v[~mask] = 0

    hsv_filtered = cv2.merge([h, s, v])
    filtered_template = cv2.cvtColor(hsv_filtered, cv2.COLOR_HSV2BGR)

    cv2.imwrite(output_path, filtered_template)
    print(f"Filtered template saved to: {output_path}")


def locateOnScreenEdges(button, region=(0, 0, 1920, 1080), confidence=0.8, path=f"{UI_PATH}/", canny_thresh1=300, canny_thresh2=300):
    screenshot = gui.screenshot(region=region)
    screenshot = np.array(screenshot)
    
    template = cv2.imread(pth(path, button), cv2.IMREAD_UNCHANGED)
    x, y, _, _ = region
    
    if template.shape[-1] == 4:
        b, g, r, alpha = cv2.split(template)
    else:
        b, g, r = cv2.split(template)
        alpha = np.full_like(b, 255, dtype=np.uint8)
    
    mask = alpha > 0
    
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
    
    template_merged = cv2.merge([b, g, r])
    template_gray = cv2.cvtColor(template_merged, cv2.COLOR_BGR2GRAY)
    
    template_gray[~mask] = 0

    screenshot_edges = cv2.Canny(screenshot_gray, canny_thresh1, canny_thresh2)
    template_edges = cv2.Canny(template_gray, canny_thresh1, canny_thresh2)
    result = cv2.matchTemplate(screenshot_edges, template_edges, cv2.TM_CCOEFF_NORMED)
    
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    if max_val < confidence:
        print(f"No match found with confidence >= {confidence} (max: {max_val})")
        raise gui.ImageNotFoundException
    
    match_x, match_y = max_loc
    
    print(f"Edge match at ({match_x}, {match_y}) with confidence: {max_val}")
    
    match_x += x
    match_y += y
    
    match_w, match_h = template.shape[1], template.shape[0]
    return Box(int(match_x), int(match_y), int(match_w), int(match_h))