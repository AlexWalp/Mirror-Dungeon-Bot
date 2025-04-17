import time, os, sys

print("Loading...")
load_time = time.time()

from abc import ABC, abstractmethod
import numpy as np, pyautogui as gui, cv2, torchfree_ocr as myocr
from PIL import Image

from .log_config import *
from .paths import PTH


ocr = myocr.Reader(["en"])

print(f"All packages imported in {(time.time() - load_time):.2f} seconds")


def connection():
    start_time = time.time()
    while LocateGray.check(PTH["connecting"], region=(1548, 66, 293, 74), wait=False):
        if time.time() - start_time > 20: raise RuntimeError("Infinite loop exited")
        time.sleep(0.1)


def countdown(seconds): # no more than 99 seconds!
    for i in range(seconds, 0, -1):
        progress = (seconds - i) / seconds
        bar_length = 20
        bar = "[" + "#" * int(bar_length * progress) + "-" * (bar_length - int(bar_length * progress)) + "]"
        
        print(f"Starting in: {i:2} {bar}", end="\r")
        time.sleep(1)
    
    print(" " * (len(f"Starting in: {seconds:2} [--------------------]")), end="\r")
    print("Grinding Time!")


def pause():
    while True:
        print("The bot is paused...")
        do = input("Press 1 to continue or press 0 to exit: ")
        if do == "0":
            exit()
        if do == "1":
            countdown(5)
            break


def close_limbus():
    if gui.getActiveWindowTitle() == 'LimbusCompany':
        gui.hotkey('alt', 'f4')

    sys.exit()


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


class Locate(ABC): # if inputing np.ndarray, convert to BGR first!
    conf=0.8
    region=(0, 0, 1920, 1080)

    @staticmethod
    def _prepare_image(image, region):
        if isinstance(image, str):
            image = cv2.imread(image, cv2.IMREAD_UNCHANGED)
        if image is None:
            image = gui.screenshot(region=region)
        if isinstance(image, Image.Image):
            image = np.array(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if not isinstance(image, np.ndarray):
            raise TypeError(f"Locate doesn't support image type '{type(image).__name__}'")
        return image

    @staticmethod
    def _load_template(template):
        if isinstance(template, str):
            template = cv2.imread(template, cv2.IMREAD_UNCHANGED)
        elif isinstance(template, Image.Image):
            template = np.array(template)
            if template.shape[-1] == 4:
                template = cv2.cvtColor(template, cv2.COLOR_RGBA2BGRA)
            else:
                template = cv2.cvtColor(template, cv2.COLOR_RGB2BGR)
        elif not isinstance(template, np.ndarray):
            raise TypeError(f"Locate doesn't support template type '{type(template).__name__}'")
        return template
    
    @staticmethod
    def _compare(result, conf, method):
        if method == cv2.TM_CCORR_NORMED:
            return zip(*np.where(result >= conf)[::-1])
        elif method == cv2.TM_CCOEFF_NORMED:
            return zip(*np.where((result + 1)/2 >= conf)[::-1])
        elif method == cv2.TM_SQDIFF_NORMED:
            return zip(*np.where(result <= 1 - conf)[::-1])
        else:
            raise ValueError(f"Matching method {method} is not supported")

    @classmethod
    @abstractmethod
    def match(cls, template, image, **kwargs):
        ...

    @classmethod
    def _locate(cls, template, image=None, region=None, conf=None, **kwargs):
        region = region or cls.region
        conf = conf or cls.conf
        image = cls._prepare_image(image, region).astype(np.uint8)
        template = cls._load_template(template).astype(np.uint8)
        return cls.match(template, image, region, conf, **kwargs)

    @classmethod
    def locate(cls, template, image=None, region=None, conf=None, **kwargs):
        match = next(cls._locate(template, image, region, conf, **kwargs), None)
        return match

    @classmethod
    def try_locate(cls, template, image=None, region=None, conf=None, **kwargs):
        match = next(cls._locate(template, image, region, conf, **kwargs), None)
        if match is None:
            raise gui.ImageNotFoundException
        return match

    @classmethod
    def locate_all(cls, template, image=None, region=None, conf=None, threshold = 8, **kwargs):
        positions = []

        try:
            seen = set()
            boxes = cls._locate(template, image, region, conf, **kwargs)
            for x, y, w, h in boxes:
                if any((abs(x - fx) <= threshold and abs(y - fy) <= threshold) for fx, fy, _, _ in positions):
                    continue
                positions.append((x, y, w, h))
                seen.add((x, y))
        finally: 
            return positions
    
    @classmethod
    def check(cls, template, image=None, region=None, conf=None, click=False, wait=5, error=False):
        if not wait: wait = 0.1

        for i in range(int(wait * 10)):
            try:
                res = cls.try_locate(template, image, region, conf)
                if isinstance(template, str):
                    print(f"located {os.path.splitext(os.path.basename(template))[0]}")
                else: print("located image")

                if click:
                    gui.moveTo(gui.center(res), duration=0.1)
                    gui.doubleClick(duration=0.1)
                    if isinstance(template, str):
                        print(f"clicked {os.path.splitext(os.path.basename(template))[0]}")
                    else: print("clicked image")
                return True         
            except gui.ImageNotFoundException:
                if wait:
                    time.sleep(0.1)
        if isinstance(template, str):
            print(f"image {os.path.splitext(os.path.basename(template))[0]} not found")
        else: print("image not found")
        if error:
            raise RuntimeError("Something unexpected happened. This code still needs debugging")
        return False


class LocateRGBA(Locate):
    @classmethod
    def _convert(cls, template, image):
        if image.shape[2] != 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        if template.shape[2] != 4:
            template = cv2.cvtColor(template, cv2.COLOR_BGR2BGRA)
        return template, image
    
    @classmethod
    def match(cls, template, image, region, conf, method=cv2.TM_CCORR_NORMED):
        x_off, y_off, _, _ = region
        # b, g, r, a = cv2.split(template)
        # mask = a > 0
        # mask_uint8 = (mask * 255).astype(np.uint8)
        # template = cv2.merge([b, g, r])
        template, image = cls._convert(template, image)
        result = cv2.matchTemplate(image, template, method, mask=template)
        match_w, match_h = template.shape[1], template.shape[0]
        for (x, y) in cls._compare(result, conf, method):
            yield (x + x_off, y + y_off, match_w, match_h)


class LocateRGB(Locate):
    @classmethod
    def _convert(cls, template, image):
        if image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        if template.shape[2] == 4:
            template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)
        return template, image
    
    @classmethod
    def match(cls, template, image, region, conf, method=cv2.TM_CCOEFF_NORMED):
        x_off, y_off, _, _ = region
        template, image = cls._convert(template, image)
        result = cv2.matchTemplate(image, template, method)
        match_w, match_h = template.shape[1], template.shape[0]
        for (x, y) in cls._compare(result, conf, method):
            yield (x + x_off, y + y_off, match_w, match_h)


class LocateGray(Locate):
    @classmethod
    def _convert(cls, template, image):
        if len(image.shape) != 2:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if len(template.shape) != 2:
            template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        return template, image
    
    @classmethod
    def match(cls, template, image, region, conf, method=cv2.TM_CCOEFF_NORMED):
        x_off, y_off, _, _ = region
        template, image = cls._convert(template, image)
        result = cv2.matchTemplate(image, template, method)
        match_w, match_h = template.shape[1], template.shape[0]
        for (x, y) in cls._compare(result, conf, method):
            yield (x + x_off, y + y_off, match_w, match_h)


class LocateEdges(LocateGray):
    @classmethod
    def match(cls, template, image, region, conf, th1=300, th2=300, method=cv2.TM_CCOEFF_NORMED):
        x_off, y_off, _, _ = region
        template, image = cls._convert(template, image)

        image_edges = cv2.Canny(image, th1, th2)
        template_edges = cv2.Canny(template, th1, th2)

        result = cv2.matchTemplate(image_edges, template_edges, method)
        match_w, match_h = template.shape[1], template.shape[0]
        for (x, y) in cls._compare(result, conf, method):
            yield (x + x_off, y + y_off, match_w, match_h)


def locateAllOnScreenRGBA(image, region=(0, 0, 1920, 1080), conf=0.9, grayscale=True, screenshot=None, A=False):
    if screenshot is None:
        screenshot = gui.screenshot(region=region)
        screenshot = np.array(screenshot)

    if isinstance(screenshot, str):
        screenshot = cv2.imread(screenshot, cv2.IMREAD_UNCHANGED)

    if isinstance(image, str):
        template = cv2.imread(image, cv2.IMREAD_UNCHANGED)
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
        yield (match_x, match_y, match_w, match_h)


def locateOnScreenRGBA(image, region=(0, 0, 1920, 1080), conf=0.9, grayscale=True, A=False, screenshot=None):
    match = next(locateAllOnScreenRGBA(image, region, conf, grayscale, A=A, screenshot=screenshot), None)
    
    if match is None:
        raise gui.ImageNotFoundException
    
    return match


# def locate_all(image, conf=0.9, region=(0, 0, 1920, 1080), path=UI_PATH, screenshot=None, threshold = 8):
#     positions = []

#     try:
#         seen = set()
#         boxes = locateAllOnScreenRGBA(image, conf=conf, grayscale=False, region=region, path=path, screenshot=screenshot)
#         for x, y, w, h in boxes:
#             if any((abs(x - fx) <= threshold and abs(y - fy) <= threshold) for fx, fy, _, _ in positions):
#                 continue
#             positions.append(Box(x, y, w, h))
#             seen.add((x, y))
#     finally: 
#         return positions
    

def check(image: str, click=False, region=(0, 0, 1920, 1080), conf=0.9, skip_wait=False, wait=5, error=False, grayscale=True, A=False, screenshot=None):
    if skip_wait:
        wait = 0.1

    for i in range(int(wait * 10)):
        try:
            res = locateOnScreenRGBA(image, region=region, conf=conf, grayscale=grayscale, A=A, screenshot=screenshot)
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

#     return False
# def locateOnScreenEdges(template, region=(0, 0, 1920, 1080), conf=0.9, path=f"{UI_PATH}/", canny_thresh1=300, canny_thresh2=300, screenshot=None, adaptive=False):
#     x, y, w, h = region
#     if screenshot is None:
#         screenshot = gui.screenshot(region=region)
#         screenshot = np.array(screenshot)
#     else:
#         screenshot = screenshot[y:h, x:w]
    
#     template = cv2.imread(pth(path, template), cv2.IMREAD_UNCHANGED)
    
#     if template.shape[-1] == 4:
#         b, g, r, alpha = cv2.split(template)
#     else:
#         b, g, r = cv2.split(template)
#         alpha = np.full_like(b, 255, dtype=np.uint8)
    
#     mask = alpha > 0
    
#     screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)

#     if adaptive:
#         blurred = cv2.GaussianBlur(screenshot_gray, (5, 5), 0)
#         median = np.median(blurred)
#         canny_thresh1 = int(max(0, 0.7 * median))
#         canny_thresh2 = int(min(255, 1.3 * median))
#         print(canny_thresh1, canny_thresh2)
    
#     template_merged = cv2.merge([b, g, r])
#     template_gray = cv2.cvtColor(template_merged, cv2.COLOR_BGR2GRAY)
    
#     template_gray[~mask] = 0

#     screenshot_edges = cv2.Canny(screenshot_gray, canny_thresh1, canny_thresh2)
#     template_edges = cv2.Canny(template_gray, canny_thresh1, canny_thresh2)
#     result = cv2.matchTemplate(screenshot_edges, template_edges, cv2.TM_CCOEFF_NORMED)
    
#     min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
#     if (max_val + 1) / 2 < conf:
#         print(f"No match found with confidence >= {conf} (max: {(max_val + 1) / 2})")
#         raise gui.ImageNotFoundException
    
#     match_x, match_y = max_loc
    
#     print(f"Edge match at ({match_x}, {match_y}) with confidence: {(max_val + 1) / 2}")
    
#     match_x += x
#     match_y += y
    
#     match_w, match_h = template.shape[1], template.shape[0]
#     return Box(int(match_x), int(match_y), int(match_w), int(match_h))