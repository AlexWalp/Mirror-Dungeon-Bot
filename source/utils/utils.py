import time, os, sys

print("Loading...")
load_time = time.time()

import numpy as np, pyautogui as gui, cv2, torchfree_ocr as myocr
from PIL import Image

from source.utils.log_config import *
from source.utils.paths import PTH, REG


ocr = myocr.Reader(["en"])

print(f"All packages imported in {(time.time() - load_time):.2f} seconds")


def connection():
    start_time = time.time()
    while LocateGray.check(PTH["connecting"], region=REG["connecting"], wait=False):
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
            sys.exit()
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


class Locate(): # if inputing np.ndarray, convert to BGR first!
    conf=0.9
    region=(0, 0, 1920, 1080)
    method=cv2.TM_CCOEFF_NORMED

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
    def _load_template(template, comp=None, v_comp=None):
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
        if comp and not (0 < comp <= 1):
            raise ValueError(f"Invalid compression value: '{comp}'")
        elif comp:
            new_size = (int(template.shape[1] * comp), int(template.shape[0] * comp))
            template = cv2.resize(template, new_size, interpolation=cv2.INTER_AREA)
        if v_comp and not (0 < v_comp <= 1):
            raise ValueError(f"Invalid vertical compression value: '{v_comp}'")
        elif v_comp:
            new_size = (int(template.shape[1]), int(template.shape[0] * v_comp))
            template = cv2.resize(template, new_size, interpolation=cv2.INTER_AREA)
        return template
    
    @classmethod
    def _compare(cls, result, conf, method):
        if method == cv2.TM_CCORR_NORMED:
            return zip(*np.where(result >= conf)[::-1])
        elif method == cv2.TM_CCOEFF_NORMED:
            return zip(*np.where((result + 1)/2 >= conf)[::-1])
        elif method == cv2.TM_SQDIFF_NORMED:
            return zip(*np.where(result <= 1 - conf)[::-1])
        else:
            raise ValueError(f"Matching method {method} is not supported")
    
    @classmethod
    def _normalize_conf(cls, max_val, min_val, method):
        if method == cv2.TM_CCORR_NORMED:
            return max_val
        elif method == cv2.TM_CCOEFF_NORMED:
            return (max_val + 1)/2
        elif method == cv2.TM_SQDIFF_NORMED:
            return 1 - min_val
        else:
            raise ValueError(f"Matching method {method} is not supported")

    @classmethod
    def _convert(cls, template, image):
        return template, image

    @classmethod
    def _match(cls, template, image, region, conf, method, **kwargs):
        x_off, y_off, _, _ = region
        template, image = cls._convert(template, image)
        result = cv2.matchTemplate(image, template, method)
        match_w, match_h = template.shape[1], template.shape[0]
        for (x, y) in cls._compare(result, conf, method):
            yield (x + x_off, y + y_off, match_w, match_h)

    @classmethod
    def _locate(cls, template, image=None, region=None, conf=None, method=None, **kwargs):
        region = region or cls.region
        conf = conf or cls.conf
        method = method or cls.method
        image = cls._prepare_image(image, region).astype(np.uint8)
        template = cls._load_template(template, **kwargs).astype(np.uint8)
        return cls._match(template, image, region, conf, method, **kwargs)
    
    @classmethod
    def get_conf(cls, template, image=None, region=None, method=None, **kwargs):
        region = region or cls.region
        method = method or cls.method
        image = cls._prepare_image(image, region).astype(np.uint8)
        template = cls._load_template(template, **kwargs).astype(np.uint8)
        template, image = cls._convert(template, image)
        min_val, max_val, _, _ = cv2.minMaxLoc(cv2.matchTemplate(image, template, method))
        return cls._normalize_conf(max_val, min_val, method)

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
    def check(cls, template, image=None, region=None, conf=None, click=False, wait=5, error=False, **kwargs):
        if not wait: wait = 0.1

        for i in range(int(wait * 10)):
            try:
                res = cls.try_locate(template, image, region, conf, **kwargs)
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
                if wait > 0.1:
                    time.sleep(0.1)
        if isinstance(template, str):
            print(f"image {os.path.splitext(os.path.basename(template))[0]} not found")
        else: print("image not found")
        if error:
            raise RuntimeError("Something unexpected happened. This code still needs debugging")
        return False


class LocateRGB(Locate):
    @classmethod
    def _convert(cls, template, image):
        if image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        if template.shape[2] == 4:
            template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)
        return template, image


class LocateGray(Locate):
    @classmethod
    def _convert(cls, template, image):
        if len(image.shape) != 2:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if len(template.shape) != 2:
            template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        return template, image


class LocateEdges(LocateGray):
    @classmethod
    def _convert(cls, template, image, th1=300, th2=300):
        template, image = super()._convert(template, image)
        image_edges = cv2.Canny(image, th1, th2)
        template_edges = cv2.Canny(template, th1, th2)
        return template_edges, image_edges


class LocatePreset:
    def __init__(self, region=None, comp=None, v_comp=None, conf=0.9, wait=5, click=False, error=False):
        self.params = {
            "region": region,
            "comp": comp,
            "v_comp": v_comp,
            "conf": conf,
            "wait": wait,
            "click": click,
            "error": error
        }

    def check(self, locate_cls, template, **overrides):
        params = self.params.copy()
        params.update(overrides)
        return locate_cls.check(template, **params)
    
    def button(self, path_key, region, **overrides):
        if isinstance(region, str):
            region = REG[region]
        params = self.params.copy()
        params.update(overrides)
        params["region"] = region
        return LocateGray.check(PTH[path_key], **params)