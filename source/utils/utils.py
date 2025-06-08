import time, os

print("Loading...")
load_time = time.time()

import numpy as np, cv2, ctypes, random

import source.utils.windows_utils as gui
from source.utils.log_config import *
from source.utils.paths import *
import source.utils.params as p

from PyQt6.QtCore import QMetaObject, Qt

print(f"All packages imported in {(time.time() - load_time):.2f} seconds")


class StopExecution(Exception): pass
class WindowError(Exception): pass


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
            if "BURN" in do: p.TEAM = "BURN"; print_settings()
            elif "BLEED" in do: p.TEAM = "BLEED"; print_settings()
            elif "TREMOR" in do: p.TEAM = "TREMOR"; print_settings()
            elif "RUPTURE" in do: p.TEAM = "RUPTURE"; print_settings()
            elif "SINKING" in do: p.TEAM = "SINKING"; print_settings()
            elif "POISE" in do: p.TEAM = "POISE"; print_settings()
            elif "CHARGE" in do: p.TEAM = "CHARGE"; print_settings()
            else: print("Incorrect format for SELECTED")
        elif "SELECTED" in do:
            num = ''.join(filter(str.isdigit, do))
            num_list = parse_numbers(num)
            if num_list:
                list_of_sinners = list(SINNERS.keys())
                p.SELECTED = [list_of_sinners[i] for i in num_list]
                print_settings()
            else: print("Incorrect format for SELECTED")
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


def check_window():
    screen_width = ctypes.windll.user32.GetSystemMetrics(0)
    screen_height = ctypes.windll.user32.GetSystemMetrics(1)
        
    left, top, width, height = p.WINDOW
    in_bounds = (
        0 <= left <= screen_width and
        0 <= top <= screen_height and
        left + width <= screen_width and
        top + height <= screen_height
    )
    if not in_bounds:
        raise WindowError("Window is partially or completely out of screen bounds!")

def set_window():
    hwnd = ctypes.windll.user32.FindWindowW(None, "LimbusCompany")

    rect = ctypes.wintypes.RECT()
    ctypes.windll.user32.GetClientRect(hwnd, ctypes.byref(rect))

    pt = ctypes.wintypes.POINT(0, 0)
    ctypes.windll.user32.ClientToScreen(hwnd, ctypes.byref(pt))

    client_width = rect.right - rect.left
    client_height = rect.bottom - rect.top
    left, top = pt.x, pt.y

    target_ratio = 16 / 9
    if client_width / client_height > target_ratio:
        target_height = client_height
        target_width = int(target_height * target_ratio)
    elif client_width / client_height < target_ratio:
        target_width = client_width
        target_height = int(target_width / target_ratio)
    else:
        target_width = client_width
        target_height = client_height

    left += (client_width - target_width) // 2
    top += (client_height - target_height) // 2

    p.WINDOW = (left, top, target_width, target_height)
    check_window()

    if int(client_width / 16) != int(client_height / 9):
        p.WARNING(f"Game window ({client_width} x {client_height}) is not 16:9\nIt is recommended to set the game to either\n1920 x 1080 or 1280 x 720")

    print("WINDOW:", p.WINDOW)


def screenshot(region=(0, 0, 1920, 1080)): # works only for cv2!
    x, y, w, h = region
    comp = p.WINDOW[2] / 1920
    return np.array(gui.screenshot(region=(
        round(p.WINDOW[0] + x*comp),
        round(p.WINDOW[1] + y*comp),
        round(w*comp),
        round(h*comp)
    )))
    # if delay:
    #     elapsed = time.time() - start_time
    #     if elapsed < 0.03: time.sleep(0.03 - elapsed)
    # return image

def rectangle(image, point1, point2, color, type):
    comp = p.WINDOW[2] / 1920
    x1, y1 = point1
    x1, y1 = int(x1*comp), int(y1*comp)
    x2, y2 = point2
    x2, y2 = int(x2*comp), int(y2*comp)
    return cv2.rectangle(image, (x1, y1), (x2, y2), color, type)


def win_click(*args, **kwargs):
    if len(args) == 1: x, y = args[0]
    else: x, y = args
    comp = p.WINDOW[2] / 1920
    x, y = int(p.WINDOW[0] + x*comp), int(p.WINDOW[1] + y*comp)
    gui.click(x, y, **kwargs)

def win_moveTo(*args, **kwargs):
    if len(args) == 1: x, y = args[0]
    else: x, y = args
    comp = p.WINDOW[2] / 1920
    x, y = int(p.WINDOW[0] + x*comp), int(p.WINDOW[1] + y*comp)
    gui.moveTo(x, y, **kwargs)

def win_dragTo(*args, **kwargs):
    if len(args) == 1: x, y = args[0]
    else: x, y = args
    comp = p.WINDOW[2] / 1920
    x, y = int(p.WINDOW[0] + x*comp), int(p.WINDOW[1] + y*comp)
    gui.dragTo(x, y, **kwargs)


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
    set_window()


def close_limbus():
    if gui.getActiveWindowTitle() == 'LimbusCompany':
        gui.hotkey('alt', 'f4')
    if p.APP: QMetaObject.invokeMethod(p.APP, "stop_execution", Qt.ConnectionType.QueuedConnection)
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


def generate_packs(priority):
    packs = {f"floor{i}": [] for i in range(1, 6)}
    for i in range(1, 6):
        for pack in priority:
            if pack in FLOORS[i]:
                packs[f"floor{i}"].append(pack)
    return packs


class Locate(): # if inputing np.ndarray, convert to BGR first!
    conf=0.9
    region=(0, 0, 1920, 1080)
    method=cv2.TM_CCOEFF_NORMED

    @staticmethod
    def _prepare_image(image, region):
        if isinstance(image, str):
            image = cv2.imread(image)
        if image is None:
            image = screenshot(region=region)
        if not isinstance(image, np.ndarray):
            raise TypeError(f"Locate doesn't support image type '{type(image).__name__}'")
        return image

    @staticmethod
    def _load_template(template, comp=1, v_comp=None):
        if isinstance(template, str):
            template = cv2.imread(template)
        elif not isinstance(template, np.ndarray):
            raise TypeError(f"Locate doesn't support template type '{type(template).__name__}'")
    
        comp = comp*(p.WINDOW[2] / 1920)
        if comp != 1:
            template = cv2.resize(template, None, fx=comp, fy=comp, interpolation=cv2.INTER_LINEAR)
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
            comp = 1920 / p.WINDOW[2]
            x_fullhd = int(x*comp) + x_off
            y_fullhd = int(y*comp) + y_off
            yield (x_fullhd, y_fullhd, int(match_w*comp), int(match_h*comp))

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
            boxes = cls._locate(template, image, region, conf, **kwargs)
            for x, y, w, h in boxes:
                if any((abs(x - fx) <= threshold and abs(y - fy) <= threshold) for fx, fy, _, _ in positions):
                    continue
                positions.append((x, y, w, h))
        finally: 
            return positions
    
    @classmethod
    def check(cls, template, image=None, region=None, conf=None, click=False, wait=5, error=False, **kwargs):
        if not wait: wait = 0.1

        for i in range(int(wait * 10)):
            try:
                res = cls.try_locate(template, image, region, conf, **kwargs)
                # if isinstance(template, str):
                #     print(f"located {os.path.splitext(os.path.basename(template))[0]}", res)
                # else: print("located image")

                if click:
                    if isinstance(click, tuple) and len(click) == 2:
                        res = click
                    else:
                        res = gui.center(res)
                    win_moveTo(res, duration=0.1)
                    gui.click(duration=0.1)
                    # if isinstance(template, str):
                    #     print(f"clicked {os.path.splitext(os.path.basename(template))[0]}")
                    # else: print("clicked image")
                return True         
            except gui.ImageNotFoundException:
                if wait > 0.1:
                    time.sleep(0.1)
        # if isinstance(template, str):
        #     print(f"image {os.path.splitext(os.path.basename(template))[0]} not found")
        # else: print("image not found")
        if error:
            raise RuntimeError("Something unexpected happened. This code still needs debugging")
        return False


class LocateRGB(Locate):
    pass


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
    

def SIFT_matching(template, kp2, des2, search_region, min_matches=40, nfeatures=2000):
    comp = p.WINDOW[2] / 1920
    if comp != 1:
        template = cv2.resize(template, None, fx=comp, fy=comp, interpolation=cv2.INTER_LINEAR)

    sift = cv2.SIFT_create(nfeatures=nfeatures, contrastThreshold=0)
    kp1, des1 = sift.detectAndCompute(template, None)

    if des1 is None or des2 is None: return None

    bf = cv2.BFMatcher(cv2.NORM_L2)
    good = bf.match(des1, des2)

    if len(good) >= min_matches:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, maxIters=200)
        if M is not None and mask is not None:
            matches_mask = mask.ravel().tolist()
            if sum(matches_mask) >= 0.25 * len(good):
                h, w = template.shape
                pts = np.float32([[0,0], [0,h], [w,h], [w,0]]).reshape(-1, 1, 2)
                dst = cv2.perspectiveTransform(pts, M)

                x_coords = dst[:,0,0]
                y_coords = dst[:,0,1]
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)

                if (x_max - x_min < 2 * w) and (y_max - y_min < 2 * h):
                    comp_inv = 1920 / p.WINDOW[2]
                    x_fullhd = int(x_min*comp_inv) + search_region[0]
                    y_fullhd = int(y_min*comp_inv) + search_region[1]
                    return (x_fullhd, y_fullhd, int((x_max - x_min)*comp), int((y_max - y_min)*comp))
    return None


class LocatePreset:
    def __init__(self, cl=LocateGray, image=None, region=None, comp=1, v_comp=None, conf=0.9, wait=5, click=False, error=False, method=None):
        self.cl = cl
        self.params = {
            "image": image,
            "region": region,
            "comp": comp,
            "v_comp": v_comp,
            "conf": conf,
            "method": method,
            "wait": wait,
            "click": click,
            "error": error,
        }

    def __call__(self, **overrides):
        params = self.params.copy()
        params.update(overrides)
        return LocatePreset(cl=self.cl, **params)

    def try_find(self, *args, **overrides):
        if   len(args) == 1: key, region_key = args[0], args[0]
        elif len(args) == 2: key, region_key = args
        else: raise ValueError("Invalid arguments")
        path = PTH[key.split('.')[0]]
        region = REG[region_key] if isinstance(region_key, str) else region_key

        params = dict(list(self.params.items())[:6])
        params.update(overrides)
        params["region"] = region
        result = self.cl.try_locate(path, **params)
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
            action = lambda: self.cl.check(path, **params)
        else:
            x, y = overrides["click"] # assuming that click is specified correctly
            action = lambda: (win_click(x, y), True)[1]
        
        if isinstance(ver, str) and "!" in ver:
            ver = REG[ver]

        if isinstance(ver, tuple):
            state0 = screenshot(region=ver)

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
                    condition = lambda: LocateGray.check(state0, image=screenshot(region=ver), wait=False, conf=0.98)
                    # print(LocateGray.get_conf(state0, image=gui.screenshot(region=ver)))

                verified = wait_for_condition(condition, interval=0.1, timer=3)
                if not verified:
                    print(f"Verifier failed (attempt {i}), reclicking...")
                    # Reclick the original target
                    if len(args) == 0:
                        win_click(x, y)
                        result = True
                    else:
                        result = self.cl.check(path, **params)

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

loc_rgb = LocatePreset(cl=LocateRGB)

click_rgb = loc_rgb(click=True)
try_rgb   = loc_rgb(error=True)
now_rgb   = loc_rgb(wait=False)

def loading_halt():
    wait_for_condition(
        condition=lambda: not now.button("loading"),
        timer=3,
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
        set_window()
        win_moveTo(1509, 978)
        gui.press("Esc")
        gui.press("Esc")
        if loc.button("forfeit", wait=1):
            gui.press("Esc")