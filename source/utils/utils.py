import time, os

print("Loading...")
load_time = time.time()

import numpy as np, pyautogui as gui, cv2
from PIL import Image

from source.utils.log_config import *
from source.utils.paths import *
import source.utils.params as p

from PyQt6.QtCore import QMetaObject, Qt

# ocr = myocr.Reader(["en"])

print(f"All packages imported in {(time.time() - load_time):.2f} seconds")


class StopExecution(Exception): pass


def print_settings():
    print("\nCurrent Settings:")
    print("─" * 66)
    settings = {
        "TEAM":     p.TEAM,
        "SELECTED": p.SELECTED,
        "BONUS":    p.BONUS,
        "RESTART":  p.RESTART,
        "ALTF4":    p.ALTF4,
        "LOG":      p.LOG
    }
    for key, value in settings.items():
        if isinstance(value, list):
            value = ", ".join(str(v) for v in value)
        print(f"{key:<9}: {str(value):<53}")
    print("─" * 66)

def parse_numbers(s):
    nums = []
    for i in range(1, 13):
        if s.startswith(str(i)):
            nums.append(i - 1)
            s = s[len(str(i)):]
    if len(nums) != 6 or s !="":
        return None
    return nums

def setup():
    print_settings()
    print("Type 'help' if you need a description of each")
    while True:
        do = input("Type 1 to confirm your settings: ")
        if "help" in do:
            print("""
Available Commands:
──────────────────────────────────────────────────────────────────
TEAM - Choose a build type (currently only 'BURN' is supported).
    ➤ Usage: TEAM <TYPE>

SELECTED - Default sinners the bot will pick if not manually selected.
    ➤ Usage: SELECTED 1 2 3 4 5 6 (six in ascending order)
    ➤ Note: Type 'SINNERS' to view sinner numbers.

BONUS - Collect weekly bonuses automatically.
    ➤ Usage: BONUS TRUE / BONUS FALSE

RESTART - Restart failed runs automatically.
    ➤ Usage: RESTART TRUE / RESTART FALSE

ALTF4 - Close Limbus Company when done or stuck.
    ➤ Usage: ALTF4 TRUE / ALTF4 FALSE

LOG - Save events and errors to 'game.log'.
    ➤ Usage: LOG TRUE / LOG FALSE
──────────────────────────────────────────────────────────────────
""")
        elif "SINNERS" in do:
            print("""
 Sinners List
────────────────────────────────────
 1. YISANG        7. HEATHCLIFF
 2. FAUST         8. ISHMAEL
 3. DONQUIXOTE    9. RODION
 4. RYOSHU       10. SINCLAIR
 5. MEURSAULT    11. OUTIS
 6. HONGLU       12. GREGOR
────────────────────────────────────
Select six sinners in ascending order when using the 'SELECTED' command.
""")
        elif "TEAM" in do:
            if "BURN" in do:
                p.TEAM = "BURN"
                print_settings()
            else:
                print("This setting is not supported yet")
        elif "SELECTED" in do:
            num = ''.join(filter(str.isdigit, do))
            num_list = parse_numbers(num)
            if num_list:
                list_of_sinners = list(SINNERS.keys())
                p.SELECTED = [list_of_sinners[i] for i in num_list]
                print_settings()
            else:
                print("Incorrect format for SELECTED")
        elif "BONUS" in do:
            if "TRUE" in do: p.BONUS = True; print_settings()
            elif "FALSE" in do: p.BONUS = False; print_settings()
            else: print("Incorrect format for BONUS")
        elif "RESTART" in do:
            if "TRUE" in do: p.RESTART = True; print_settings()
            elif "FALSE" in do: p.RESTART = False; print_settings()
            else: print("Incorrect format for RESTART")
        elif "ALTF4" in do:
            if "TRUE" in do: p.ALTF4 = True; print_settings()
            elif "FALSE" in do: p.ALTF4 = False; print_settings()
            else: print("Incorrect format for ALTF4")
        elif "LOG" in do:
            if "TRUE" in do: p.LOG = True; print_settings()
            elif "FALSE" in do: p.LOG = False; print_settings()
            else: print("Incorrect format for LOG")
        elif do == "0":
            raise StopExecution()
        elif do == "1":
            break


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
    if p.APP:
        QMetaObject.invokeMethod(p.APP, "to_pause", Qt.ConnectionType.QueuedConnection)
        p.pause_event.clear()
        p.pause_event.wait()
        if p.stop_event.is_set():
            raise StopExecution()
        countdown(5)
    else:
        while True:
            print("The bot is paused...")
            do = input("Press 1 to continue or press 0 to exit: ")
            if do == "0":
                raise StopExecution()
            if do == "1":
                countdown(5)
                break


def close_limbus():
    if gui.getActiveWindowTitle() == 'LimbusCompany':
        gui.hotkey('alt', 'f4')

    raise StopExecution()


def wait_for_condition(condition, action=None, interval=0.5, timer=20):
    start_time = time.time()
    while condition():
        if time.time() - start_time > timer:
            return False # exit inf loop
        if action:
            action()
        time.sleep(interval)
    return True


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
                    if isinstance(click, tuple) and len(click) == 2:
                        res = click
                    else:
                        res = gui.center(res)
                    gui.moveTo(res, duration=0.1)
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
    def __init__(self, method=LocateGray, image=None, region=None, comp=None, v_comp=None, conf=0.9, wait=5, click=False, error=False):
        self.method = method
        self.params = {
            "image": image,
            "region": region,
            "comp": comp,
            "v_comp": v_comp,
            "conf": conf,
            "wait": wait,
            "click": click,
            "error": error,
        }

    def __call__(self, **overrides):
        params = self.params.copy()
        params.update(overrides)
        return LocatePreset(method=self.method, **params)

    def try_find(self, *args, **overrides):
        if   len(args) == 1: key, region_key = args[0], args[0]
        elif len(args) == 2: key, region_key = args
        else: raise ValueError("Invalid arguments")
        path = PTH[key.split('.')[0]]
        region = REG[region_key] if isinstance(region_key, str) else region_key

        params = dict(list(self.params.items())[:5])
        params.update(overrides)
        params["region"] = region
        result = self.method.try_locate(path, **params)
        return gui.center(result)
    
    def button(self, *args, ver=False, **overrides):
        if   len(args) == 1: key, region_key = args[0], args[0]
        elif len(args) == 2: key, region_key = args
        elif len(args) != 0: raise ValueError("Invalid arguments")
        
        if len(args) != 0:
            path = PTH[key.split('.')[0]]
            region = REG[region_key] if isinstance(region_key, str) else region_key

            params = self.params.copy()
            params.update(overrides)
            params["region"] = region
            action = lambda: self.method.check(path, **params)
        else:
            x, y = overrides["click"] # assuming that click is specified correctly
            action = lambda: (gui.click(x, y), True)[1]
        
        if isinstance(ver, str) and "!" in ver:
            ver = REG[ver]

        if isinstance(ver, tuple):
            state0 = gui.screenshot(region=ver)

        result = action()

        if ver and result:
            if len(args) != 0:
                if not params["click"]:
                    raise AssertionError("Verification reqires action to verify")
                params["wait"] = False
            for i in range(3):
                if gui.getActiveWindowTitle() != 'LimbusCompany': pause()
                if isinstance(ver, str):
                    condition = lambda: not self.button(ver, wait=False, click=False, error=False)
                else:
                    condition = lambda: LocateGray.check(state0, image=gui.screenshot(region=ver), wait=False, conf=0.98)
                    # print(LocateGray.get_conf(state0, image=gui.screenshot(region=ver)))

                verified = wait_for_condition(condition, timer=3)
                if not verified:
                    print(f"Verifier failed (attempt {i}), reclicking...")
                    # Reclick the original target
                    if len(args) == 0:
                        gui.click(x, y)
                        result = True
                    else:
                        result = self.method.check(path, **params)

                    if not result:
                        # Button disappeared + verifier false — unrecoverable
                        raise RuntimeError(f"Click retry failed")
                else:
                    break  # verifier passed
            else:
                raise RuntimeError(f"Verification failed after 3 retries.")
        return result


loc       = LocatePreset()

click     = loc(click=True)
try_loc   = loc(error=True)
now       = loc(wait=False)

try_click = click(error=True)
now_click = click(wait=False)

loc_rgb = LocatePreset(method=LocateRGB)

click_rgb = loc_rgb(click=True)
try_rgb   = loc_rgb(error=True)
now_rgb   = loc_rgb(wait=False)

def loading_halt():
    wait_for_condition(
        condition=lambda: not now.button("loading"),
        timer=2,
        interval=0.1
    )
    wait_for_condition(
        condition=lambda: now.button("loading"),
    )

def connection():
    wait_for_condition(
        condition=lambda: not now.button("loading"),
        timer=0.5,
        interval=0.1
    )
    wait_for_condition(
        condition=lambda: now.button("connecting"),
    )
    

class BaseAction:
    def should_execute(self, next_action=None) -> bool:
        raise NotImplementedError

    def execute(self, preset: LocatePreset, ver=None):
        raise NotImplementedError


class Action(BaseAction):
    def __init__(self, key, region=None, click=None, ver=None):
        self.key = key
        self.region = region
        self.click = click
        self.ver = ver

    def should_execute(self, _=None):
        return True  # Always executed

    def execute(self, preset: LocatePreset, ver=None):
        args = (self.key,) if self.region is None else (self.key, self.region)
        kwargs = {}
        if self.click is not None:
            kwargs["click"] = self.click
        return preset.button(*args, ver=self.ver or ver, **kwargs)


class ClickAction(BaseAction):
    def __init__(self, click: tuple, ver: tuple | str = None):
        self.click = click
        self.ver = ver

    def should_execute(self, _=None):
        return True

    def execute(self, preset: LocatePreset, ver=None):
        return preset.button(click=self.click, ver=self.ver or ver)
    

def chain_actions(preset: LocatePreset, actions: list):
    for i in range(len(actions)):
        curr = actions[i]
        if callable(curr) and not isinstance(curr, BaseAction):
            curr()
            continue

        next_action = actions[i + 1] if i + 1 < len(actions) else None
        ver = None
        if getattr(curr, "ver", None) is None and next_action:
            if isinstance(next_action, Action):
                ver = next_action.key
            elif isinstance(next_action, ClickAction):
                ver = next_action.ver  # Could still be set explicitly

        curr.execute(preset, ver=ver)

def handle_fuckup():
    if gui.getActiveWindowTitle() == 'LimbusCompany':
        gui.moveTo(1509, 978)
        gui.press("Esc")
        gui.press("Esc")
        if loc.button("forfeit", wait=1):
            gui.press("Esc")