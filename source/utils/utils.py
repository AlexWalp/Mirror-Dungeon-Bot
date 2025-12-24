import numpy as np, cv2, random, time, os, platform, logging
from source.utils.paths import *
import source.utils.params as p

from PyQt6.QtCore import QMetaObject, Qt

if platform.system() == "Windows":
    import source.utils.os_windows_backend as gui
elif platform.system() == "Linux":
    if os.environ.get("XDG_SESSION_TYPE") == "x11":
        import source.utils.os_x11_backend as gui
    else:
        raise RuntimeError("Wayland is not supported. Use Plasma (X11).")
else:
    raise RuntimeError("Unsupported OS")


class StopExecution(Exception): pass


def screenshot(region=(0, 0, 1920, 1080)): # works only for cv2!
    x, y, w, h = region
    comp = p.WINDOW[2] / 1920
    return np.array(gui.screenshot(region=(
        round(p.WINDOW[0] + x*comp),
        round(p.WINDOW[1] + y*comp),
        round(w*comp),
        round(h*comp)
    )))

def rectangle(image, point1, point2, color, type):
    comp = p.WINDOW[2] / 1920
    x1, y1 = point1
    x1, y1 = int(x1*comp), int(y1*comp)
    x2, y2 = point2
    x2, y2 = int(x2*comp), int(y2*comp)
    return cv2.rectangle(image, (x1, y1), (x2, y2), color, type)

def win_get_position():
    x, y = gui.get_position()
    inv_comp = 1920 / p.WINDOW[2]
    return int(x*inv_comp - p.WINDOW[0]), int(y*inv_comp - p.WINDOW[1])

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

def pause(other_win):
    print(f"Switched to window: {other_win}")
    logging.info(f"Execution paused")
    if p.APP:
        QMetaObject.invokeMethod(p.APP, "to_pause", Qt.ConnectionType.QueuedConnection)
        p.pause_event.clear()
        p.pause_event.wait()
        if p.stop_event.is_set():
            raise StopExecution
        countdown(5)
    else: raise StopExecution
    gui.set_window()
    logging.info("Execution resumed")


def close_limbus(error=None):
    if gui.getActiveWindowTitle() == p.LIMBUS_NAME:
        gui.hotkey('alt', 'f4')
    if p.APP: QMetaObject.invokeMethod(p.APP, "stop_execution", Qt.ConnectionType.QueuedConnection)
    if error is None:
        raise StopExecution
    else: raise error


def wait_for_condition(condition, action=None, interval=0.5, timer=20):
    start_time = time.time()
    while condition():
        if time.time() - start_time > timer:
            return False # exit inf loop
        if action:
            action()
        time.sleep(interval)
    return True


def generate_packs_pr(input_priority):
    priority, priority_f = input_priority
    
    packs = {f"floor{i}": [] for i in range(1, 6 + p.EXTREME*10)}
    floors = HARD_FLOORS if p.HARD else FLOORS

    for i in range(1, 6 + p.EXTREME*10):
        for pack in priority:
            assigned_on_this_floor = {pack for pack, fl in priority_f.items() if fl == i}
            if (pack in floors[format_lvl(i)] and (
               (pack in priority_f and priority_f[pack] == i) or
               (pack not in priority_f and not assigned_on_this_floor))):
                packs[f"floor{i}"].append(pack)
    return packs

def generate_packs_av(input_avoid):
    avoid, priority_f, avoid_f = input_avoid
    
    packs = {f"floor{i}": [] for i in range(1, 6 + p.EXTREME*10)}
    floors = HARD_FLOORS if p.HARD else FLOORS

    for i in range(1, 6 + p.EXTREME*10):
        for pack in avoid:
            if (pack in floors[format_lvl(i)] and (
               (pack in avoid_f and avoid_f[pack] == i) or
               (pack not in avoid_f))):
                packs[f"floor{i}"].append(pack)
        for pack in priority_f.keys():
            if pack in floors[format_lvl(i)] and priority_f[pack] != i:
                packs[f"floor{i}"].append(pack)
    return packs

def format_lvl(lvl):
    if lvl < 6: return lvl
    elif lvl < 11: return 5
    else: return 15

def generate_packs_all(input_priority):
    priority, priority_f = input_priority
    packs = {f"floor{i}": [] for i in range(1, 6 + p.EXTREME*10)}
    floors = HARD_FLOORS if p.HARD else FLOORS

    for i in range(1, 6 + p.EXTREME*10):
        packs[f"floor{i}"] = list((set(priority) - set(priority_f.keys())) & set(floors[format_lvl(i)]))
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
    def _distort(image, w, h, shift):
        src_pts = np.float32([
            [0, 0],
            [w - 1, 0],
            [w - 1, h - 1],
            [0, h - 1]
        ])
        dst_pts = np.float32([
            [0 + shift, 0],
            [w - 1 + shift, 0], 
            [w - 1 - shift, h - 1],
            [0 - shift, h - 1]
        ])
        M = cv2.getPerspectiveTransform(src_pts, dst_pts)
        translation = np.array([
            [1, 0, -shift//2],
            [0, 1, 0],
            [0, 0, 1]
        ], dtype=np.float32)
        M_combined = translation @ M
        return cv2.warpPerspective(image, M_combined, (w + 1, h))

    @staticmethod
    def _load_template(template, comp=1, v_comp=None, h_comp=None, distort=None):
        if isinstance(template, str):
            template = cv2.imread(template)
        elif not isinstance(template, np.ndarray):
            raise TypeError(f"Locate doesn't support template type '{type(template).__name__}'")
    
        comp = comp*(p.WINDOW[2] / 1920)
        if comp != 1:
            template = cv2.resize(template, None, fx=comp, fy=comp, interpolation=cv2.INTER_AREA)
        if v_comp and not (0 < v_comp <= 1):
            raise ValueError(f"Invalid vertical compression value: '{v_comp}'")
        elif v_comp:
            new_size = (int(template.shape[1]), int(template.shape[0] * v_comp))
            template = cv2.resize(template, new_size, interpolation=cv2.INTER_AREA)
        if h_comp and not (0 < h_comp):
            raise ValueError(f"Invalid horizontal compression value: '{h_comp}'")
        elif h_comp:
            new_size = (int(template.shape[1] * h_comp), int(template.shape[0]))
            template = cv2.resize(template, new_size, interpolation=cv2.INTER_CUBIC)
        if distort:
            h, w = template.shape[:2]
            shift = int(w * distort)
            template = Locate._distort(template, w, h, shift)
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


def amplify(img, sigma_list=[15, 80, 250], alpha=0.1, beta=0.3, gamma=2.4):
    """
    Enhanced Multi-Scale Retinex with improved contrast control
    Parameters:
    - alpha: Blend factor (0.0 = original, 1.0 = full retinex)
    - beta: Brightness control (0.0-1.0)
    - gamma: Final gamma correction
    """
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l_float = l.astype(np.float32) / 255.0
    msr = np.zeros_like(l_float)
    
    for sigma in sigma_list:
        blurred = cv2.GaussianBlur(l_float, (0, 0), sigma)
        msr += np.log(l_float + 1e-6) - np.log(blurred + 1e-6)
    
    msr /= len(sigma_list)
    
    l_msr = beta * msr
    l_result = alpha * l_msr + (1 - alpha) * l_float
    l_result = np.clip(l_result, 0, 1)
    l_result = l_result ** (1.0/gamma)
    l_result = (l_result * 255).astype(np.uint8)
    lab_result = cv2.merge([l_result, a, b])
    return cv2.cvtColor(lab_result, cv2.COLOR_LAB2BGR)

def create_mask(image, target_hsv, tolerance):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower = np.array([max(0, target_hsv[0] - tolerance),
                     max(0, target_hsv[1] - tolerance),
                     max(0, target_hsv[2] - tolerance)])
    upper = np.array([min(255, target_hsv[0] + tolerance),
                        min(255, target_hsv[1] + tolerance),
                        min(255, target_hsv[2] + tolerance)])
    mask = cv2.inRange(hsv, lower, upper)
    return mask


class SIFTMatcher: # unlike other modules, this works only with 1920x1080
    def __init__(self, image=None, region=(0, 0, 1920, 1080), **sift_params):
        self.region = region
        self.base_image = self._prepare_image(image, region)
        self.sift = cv2.SIFT_create(**sift_params)
        self.kp_base, self.des_base = self.sift.detectAndCompute(self.base_image, None)
    
    @staticmethod
    def _prepare_image(image, region):
        x, y, w, h = region
        comp = p.WINDOW[2] / 1920
        x_d, y_d, w_d, h_d = round(p.WINDOW[0] + x*comp), round(p.WINDOW[1] + y*comp), round(w*comp), round(h*comp)

        if isinstance(image, str):
            img = cv2.imread(image)
            if img is None:
                raise FileNotFoundError(f"Image not found: {image}")
            img = img[y_d:y_d+h_d, x_d:x_d+w_d]
        elif image is None:
            img = screenshot(region=region)
        elif isinstance(image, np.ndarray):
            img = image[y_d:y_d+h_d, x_d:x_d+w_d]
        else:
            raise TypeError(f"Unsupported image type: {type(image)}")

        h_img, w_img = img.shape[:2]
        if w_img != w:
            scale = w / w_img
            img = cv2.resize(img, (w, int(h_img * scale)), interpolation=cv2.INTER_LINEAR)
        return img
    
    @staticmethod
    def _load_template(template):
        if isinstance(template, str):
            tpl = cv2.imread(template, cv2.IMREAD_GRAYSCALE)
            if tpl is None:
                raise FileNotFoundError(f"Template not found: {template}")
            return tpl
        elif isinstance(template, np.ndarray):
            return template
        else:
            raise TypeError(f"Unsupported template type: {type(template)}")
    
    def _match_template(self, template, min_matches=40, inlier_ratio=0.25):
        # comp = p.WINDOW[2] / 1920
        template = SIFTMatcher._load_template(template)
        # if comp != 1:
        #     template = cv2.resize(template, None, fx=comp, fy=comp, interpolation=cv2.INTER_LINEAR)
        
        kp1, des1 = self.sift.detectAndCompute(template, None)

        if des1 is None or self.des_base is None: return None
        
        bf = cv2.BFMatcher(cv2.NORM_L2)
        good = bf.match(des1, self.des_base)
        
        if len(good) < min_matches: return None

        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([self.kp_base[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, maxIters=200)
        if M is None or mask is None: return None
        
        matches_mask = mask.ravel().tolist()
        # inlier_matches = [m for i, m in enumerate(good) if matches_mask[i]]
        # img_matches = cv2.drawMatches(template, kp1, screenshot(region=search_region), kp2, inlier_matches, None, flags=2)
        # cv2.imwrite(f"{time.time()}.png", img_matches)
        
        if sum(matches_mask) < inlier_ratio * len(good): return None
        
        h, w = template.shape
        pts = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)
        
        x_coords = dst[:, 0, 0]
        y_coords = dst[:, 0, 1]
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        if (x_max - x_min < 2 * w) and (y_max - y_min < 2 * h):
            x_full = int(x_min + self.region[0])
            y_full = int(y_min + self.region[1])
            width = int(x_max - x_min)
            height = int(y_max - y_min)
            
            return (x_full, y_full, width, height)
    
    def locate(self, template, **kwargs):
        return self._match_template(template, **kwargs)
    
    def try_locate(self, template, **kwargs):
        match = self._match_template(template, **kwargs)
        if match is None:
            raise gui.ImageNotFoundException
        return match


class LocatePreset:
    def __init__(self, cl=LocateGray, image=None, region=None, comp=1, v_comp=None, distort=None, conf=0.9, wait=5, click=False, error=False, method=None):
        self.cl = cl
        self.params = {
            "image": image,
            "region": region,
            "comp": comp,
            "v_comp": v_comp,
            "distort": distort,
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

        params = dict(list(self.params.items())[:7])
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
                if (win := gui.getActiveWindowTitle()) != p.LIMBUS_NAME: pause(win)
                if isinstance(ver, str):
                    condition = lambda: not self.button(ver, wait=False, click=False, error=False)
                else:
                    condition = lambda: LocateGray.check(state0, image=screenshot(region=ver), wait=False, conf=0.98, method=1)
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
    if gui.getActiveWindowTitle() == p.LIMBUS_NAME:
        gui.set_window()
        win_click(1888, 901)
        gui.press("Esc")
        gui.press("Esc")
        if loc.button("forfeit", wait=1):
            gui.press("Esc")