# Linux (X11) port
# Extra dependencies: python-xlib, mss

import atexit
import mss
from evdev import UInput, ecodes as e
from Xlib import X, display
import numpy as np, time, math, random
import source.utils.params as p

# Tweening functions
def linear(t):
    return t

def easeInOutQuad(t):
    return 2*t*t if t < 0.5 else -1 + (4 - 2*t)*t

def easeOutElastic(t):
    c4 = (2 * math.pi) / 3
    if t == 0:
        return 0
    elif t == 1:
        return 1
    return 2**(-10 * t) * math.sin((t * 10 - 0.75) * c4) + 1

# Display + root
_disp = display.Display()
_root = _disp.screen().root

FAILSAFE = True
FAILSAFE_ENABLED = True

def set_failsafe(state=True):
    global FAILSAFE_ENABLED
    FAILSAFE_ENABLED = state

def get_screen_size():
    """Return (width, height) of the X screen (root window)."""
    screen = _disp.screen()
    return screen.width_in_pixels, screen.height_in_pixels

def get_position():
    """Return (x, y) cursor position relative to root."""
    pointer = _root.query_pointer()
    return pointer.root_x, pointer.root_y

def _get_window_title(win):
    """Return window title attempting _NET_WM_NAME then WM_NAME."""
    try:
        atom_net_wm_name = _disp.intern_atom('_NET_WM_NAME')
        prop = win.get_full_property(atom_net_wm_name, X.AnyPropertyType)
        if prop and prop.value:
            # prop.value may be bytes -> decode
            if isinstance(prop.value, bytes):
                try:
                    return prop.value.decode('utf-8')
                except Exception:
                    return prop.value.decode('latin-1', errors='ignore')
            return prop.value

        # Fallback to WM_NAME
        prop2 = win.get_wm_name()
        if prop2:
            return prop2
    except Exception:
        pass
    return ""

def getActiveWindowTitle():
    """Return active window title, or empty string if none."""
    try:
        atom_net_active = _disp.intern_atom('_NET_ACTIVE_WINDOW')
        prop = _root.get_full_property(atom_net_active, X.AnyPropertyType)
        if not prop:
            return ""
        win_id = prop.value[0]
        win = _disp.create_resource_object('window', win_id)
        title = _get_window_title(win)
        return title or ""
    except Exception:
        return ""

# Helper to find a top-level window by title (exact or substring)
def _find_window_by_name(name):
    """Search _NET_CLIENT_LIST for a window whose title contains `name`."""
    try:
        atom_clients = _disp.intern_atom('_NET_CLIENT_LIST')
        prop = _root.get_full_property(atom_clients, X.AnyPropertyType)
        if not prop:
            return None
        for wid in prop.value:
            try:
                w = _disp.create_resource_object('window', wid)
                title = _get_window_title(w)
                if not title:
                    continue
                if title == name or name in title:
                    return w
            except Exception:
                continue
    except Exception:
        pass
    return None

def center(target=None):
    """
    Returns the center coordinates of:
     - A window (if target is string title)
     - A region (if target is a box tuple (left, top, width, height))
     - The primary screen (if no target)
    """
    if isinstance(target, str):
        w = _find_window_by_name(target)
        if not w:
            raise ValueError(f"Window not found: {target}")
        geom = w.get_geometry()
        # translate window coords to root coords
        try:
            tx = w.translate_coords(_root, 0, 0)
            left, top = tx.x, tx.y
        except Exception:
            left, top = geom.x, geom.y
        center_x = left + geom.width // 2
        center_y = top + geom.height // 2
        return center_x, center_y

    elif isinstance(target, (tuple, list)) and len(target) >= 4:
        left, top, width, height = target[:4]
        return (left + width // 2, top + height // 2)

    else:
        width, height = get_screen_size()
        return (width // 2, height // 2)
    

def get_virtual_screen_bounds():
    """
    Returns (min_x, min_y, max_x, max_y) of the virtual desktop.
    Equivalent to Windows' SM_XVIRTUALSCREEN / SM_CXVIRTUALSCREEN.
    Coordinates may be negative.
    """
    from Xlib.ext import randr

    res = randr.get_screen_resources(_root)

    min_x = min_y = float("inf")
    max_x = max_y = float("-inf")

    for crtc in res.crtcs:
        info = randr.get_crtc_info(_root, crtc, res.config_timestamp)

        # Skip disabled CRTCs
        if info.width == 0 or info.height == 0:
            continue

        min_x = min(min_x, info.x)
        min_y = min(min_y, info.y)
        max_x = max(max_x, info.x + info.width)
        max_y = max(max_y, info.y + info.height)

    # Fallback: no RandR info
    if min_x == float("inf"):
        geom = _root.get_geometry()
        min_x = geom.x
        min_y = geom.y
        max_x = geom.x + geom.width
        max_y = geom.y + geom.height

    return int(min_x), int(min_y), int(max_x), int(max_y)
    

def clip_region_to_virtual(region):
    x, y, w, h = region
    min_x, min_y, max_x, max_y = p.SCREEN

    x2 = max(x, min_x)
    y2 = max(y, min_y)

    x_end = min(x + w, max_x)
    y_end = min(y + h, max_y)

    w2 = x_end - x2
    h2 = y_end - y2

    if w2 <= 0 or h2 <= 0:
        return None

    return x2, y2, w2, h2
  

def screenshot(imageFilename=None, region=None):
    """
    Capture screenshot using XShm via mss (falls back to XGetImage if needed).
    region: (x, y, width, height)
    Returns numpy array in BGR order (height, width, 3) for cv2 compatibility.
    """
    with mss.mss() as sct:
        if region:
            min_x, min_y, _, _ = p.SCREEN
            left, top, width, height = region

            x0 = left - min_x
            y0 = top - min_y

            monitor = {"left": x0, "top": y0, "width": width, "height": height}
        else:
            monitor = sct.monitors[0]

        full = sct.grab(monitor)
        img = np.array(full)[:, :, :3]

        if imageFilename:
            import cv2
            cv2.imwrite(imageFilename, img)

        return img


# --- UINPUT VIRTUAL DEVICE SETUP ---
_EVDEV_KEYSYM_MAP = {
    'enter': e.KEY_ENTER, 'esc': e.KEY_ESC, 'space': e.KEY_SPACE,
    'tab': e.KEY_TAB, 'backspace': e.KEY_BACKSPACE, 'delete': e.KEY_DELETE,
    'insert': e.KEY_INSERT, 'home': e.KEY_HOME, 'end': e.KEY_END,
    'pageup': e.KEY_PAGEUP, 'pagedown': e.KEY_PAGEDOWN, 'shift': e.KEY_LEFTSHIFT,
    'ctrl': e.KEY_LEFTCTRL, 'alt': e.KEY_LEFTALT, 'win': e.KEY_LEFTMETA,
    'up': e.KEY_UP, 'down': e.KEY_DOWN, 'left': e.KEY_LEFT, 'right': e.KEY_RIGHT,
    'f1': e.KEY_F1, 'f2': e.KEY_F2, 'f3': e.KEY_F3, 'f4': e.KEY_F4,
    'f5': e.KEY_F5, 'f6': e.KEY_F6, 'f7': e.KEY_F7, 'f8': e.KEY_F8,
    'f9': e.KEY_F9, 'f10': e.KEY_F10, 'f11': e.KEY_F11, 'f12': e.KEY_F12,
}

for char in "abcdefghijklmnopqrstuvwxyz":
    _EVDEV_KEYSYM_MAP[char] = getattr(e, f"KEY_{char.upper()}")
for num in "0123456789":
    _EVDEV_KEYSYM_MAP[num] = getattr(e, f"KEY_{num}")

_safe_keys = list(set(_EVDEV_KEYSYM_MAP.values()))

_events = {
    e.EV_KEY: [e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE] + _safe_keys,
    e.EV_REL: [e.REL_X, e.REL_Y, e.REL_WHEEL]
}

try:
    _ui = UInput(_events, name="Virtual_Index_Device")
except Exception as ex:
    print("ERROR: Cannot create uinput device. Run script with sudo.")
    raise ex

# Map logical buttons
_BUTTON_MAP = {'left': e.BTN_LEFT, 'middle': e.BTN_MIDDLE, 'right': e.BTN_RIGHT}

def release_all():
    for btn in _BUTTON_MAP.values():
        _ui.write(e.EV_KEY, btn, 0)
    
    for key_code in _safe_keys:
        _ui.write(e.EV_KEY, key_code, 0)
    _ui.syn()

atexit.register(release_all)

def _fail_safe_check():
    """Check fail-safe"""
    if not FAILSAFE_ENABLED:
        return

    name = getActiveWindowTitle()

    if p.LIMBUS_NAME not in name:
        release_all()
        raise PauseException(name)

class WindowError(Exception): pass
class FailSafeException(Exception): pass
class ImageNotFoundException(Exception): pass
class PauseException(Exception):
    def __init__(self, name):
        super().__init__(name)
        self.window = name


def mouseDown(button='left', delay=0.09):
    _btn = _BUTTON_MAP.get(button.lower(), e.BTN_LEFT)
    _ui.write(e.EV_KEY, _btn, 1)
    _ui.syn()
    time.sleep(delay)

def mouseUp(button='left', delay=0.09):
    _btn = _BUTTON_MAP.get(button.lower(), e.BTN_LEFT)
    _ui.write(e.EV_KEY, _btn, 0)
    _ui.syn()
    time.sleep(delay)

def _to_absolute(x, y):
    """For X, absolute coords are pixel coordinates (no 0..65535 scaling)."""
    return int(round(x)), int(round(y))

def _human_delay(min_delay=0.01, max_delay=0.03):
    time.sleep(random.uniform(min_delay, max_delay))

def moveTo(x, y, duration=0.0, tween=easeInOutQuad, delay=0.08, humanize=True):
    _fail_safe_check()

    duration += delay  # emulate pyautogui delay
    start_x, start_y = get_position()
    steps = max(2, int(duration * 100))

    # Human-like movement parameters
    if humanize:
        curve_intensity = random.uniform(0.3, 0.7)
        jitter_frequency = random.randint(3, 7)
        jitter_magnitude = random.uniform(0.5, 2.0)

    for i in range(steps):
        progress = tween(i / (steps - 1))

        linear_x = start_x + (x - start_x) * progress
        linear_y = start_y + (y - start_y) * progress

        if humanize and duration > 0.1:
            curve_progress = math.sin(progress * math.pi)
            curve_offset_x = (y - start_y) * curve_intensity * curve_progress * 0.3
            curve_offset_y = (x - start_x) * curve_intensity * curve_progress * -0.3

            jitter_x = (math.sin(i * jitter_frequency) *
                       (x - start_x) * 0.01 * jitter_magnitude)
            jitter_y = (math.cos(i * jitter_frequency) *
                       (y - start_y) * 0.01 * jitter_magnitude)

            current_x = linear_x + curve_offset_x + jitter_x
            current_y = linear_y + curve_offset_y + jitter_y
        else:
            current_x = linear_x
            current_y = linear_y

        # clamp
        current_x = min(max(current_x, min(start_x, x)), max(start_x, x))
        current_y = min(max(current_y, min(start_y, y)), max(start_y, y))

        target_abs_x, target_abs_y = _to_absolute(current_x, current_y)
        actual_x, actual_y = get_position() 
        
        dx = target_abs_x - actual_x
        dy = target_abs_y - actual_y
        
        if dx != 0 or dy != 0:
            _ui.write(e.EV_REL, e.REL_X, dx)
            _ui.write(e.EV_REL, e.REL_Y, dy)
            _ui.syn()
            time.sleep(0.002)

        if i < steps - 1:
            if humanize:
                sleep_time = duration / steps * random.uniform(0.8, 1.2)
                time.sleep(max(0.001, sleep_time))
            else:
                time.sleep(duration / steps)

    timeout_start = time.time()
    while time.time() - timeout_start < 0.5:
        actual_x, actual_y = get_position()
        if (actual_x, actual_y) == (x, y):
            break
            
        dx = x - actual_x
        dy = y - actual_y
        
        _ui.write(e.EV_REL, e.REL_X, dx)
        _ui.write(e.EV_REL, e.REL_Y, dy)
        _ui.syn()
        
        time.sleep(0.005)

    final_delay = random.uniform(0.02, 0.05) if humanize else 0.03
    time.sleep(final_delay)
    _fail_safe_check()

def click(x=None, y=None, button='left', clicks=1, interval=0.1, duration=0.0, tween=easeInOutQuad, delay=0.03):
    _fail_safe_check()
    if x is not None and y is not None:
        moveTo(x, y, duration, tween, delay=delay+0.02)
    elif duration > 0:
        current_x, current_y = get_position()
        moveTo(current_x, current_y, duration, tween, delay=delay+0.02)
    else:
        time.sleep(0.02)

    for i in range(clicks):
        _fail_safe_check()
        mouseDown(button, delay=delay)
        mouseUp(button, delay=delay)
        if interval > 0 and i < clicks - 1:
            time.sleep(interval)
            _fail_safe_check()

def dragTo(x, y, duration=0.1, tween=easeInOutQuad, button='left', start_x=None, start_y=None):
    _fail_safe_check()
    if start_x is not None and start_y is not None:
        moveTo(start_x, start_y)
    mouseDown(button, delay=0.03)
    moveTo(x, y, duration, tween, humanize=False)
    mouseUp(button, delay=0.03)
    _fail_safe_check()

def scroll(clicks, x=None, y=None):
    """Scroll vertically: positive clicks -> up, negative -> down."""
    if x is not None and y is not None:
        moveTo(x, y)
    direction = 1 if clicks > 0 else -1
    count = abs(int(clicks))
    
    for _ in range(count):
        _ui.write(e.EV_REL, e.REL_WHEEL, direction)
        _ui.syn()
        time.sleep(0.02)
        
    _human_delay()

# Keyboard functions
def _key_to_ecode(key):
    return _EVDEV_KEYSYM_MAP.get(key.lower(), None)

def press(keys, presses=1, interval=0.1, delay=0.01):
    for _p in range(presses):
        if isinstance(keys, str):
            keys = [keys]

        ecodes = []
        for key in keys:
            kc = _key_to_ecode(key)
            if not kc:
                continue
            ecodes.append(kc)
            _ui.write(e.EV_KEY, kc, 1) # Press
            _ui.syn()
            time.sleep(delay)

        for kc in reversed(ecodes):
            _ui.write(e.EV_KEY, kc, 0) # Release
            _ui.syn()
            time.sleep(delay)

        if interval > 0 and _p < presses - 1:
            time.sleep(interval)

def hotkey(*args, **kwargs):
    press(list(args), **kwargs)

# Anti-cheat enhancements
def add_mouse_jitter(max_offset=5):
    x, y = get_position()
    jitter_x = random.randint(-max_offset, max_offset)
    jitter_y = random.randint(-max_offset, max_offset)
    moveTo(x + jitter_x, y + jitter_y, duration=0.05)

def randomize_delay(base_delay):
    return base_delay * random.uniform(0.8, 1.2)


def get_absolute_position(win):
    x = y = 0
    while True: # Ugly!!!
        geom = win.get_geometry()
        x += geom.x
        y += geom.y
        parent = win.query_tree().parent
        if parent.id == _root.id:
            break
        win = parent
    return x, y


def check_window():
    min_x, min_y, max_x, max_y = p.SCREEN
    left, top, width, height = p.WINDOW
    in_bounds = (
        left >= min_x and
        top >= min_y and
        left + width <= max_x and
        top + height <= max_y
    )
    if not in_bounds:
        raise WindowError("Window is partially or completely out of screen bounds!")


def set_window():
    """
    Find window by p.LIMBUS_NAME, calculate its client center and set p.WINDOW
    to a centered 16:9 region inside the client area (like Windows module).
    """
    w = _find_window_by_name(p.LIMBUS_NAME)
    if not w:
        raise WindowError(f"Window '{p.LIMBUS_NAME}' not found.")

    _disp.sync()
    try:
        geom = w.get_geometry()
    except Exception:
        raise WindowError(f"Window '{p.LIMBUS_NAME}' not found.")

    client_width, client_height = geom.width, geom.height

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

    left, top = get_absolute_position(w)
    left += (client_width - target_width) // 2
    top += (client_height - target_height) // 2

    p.WINDOW = (left, top, target_width, target_height)
    p.SCREEN = get_virtual_screen_bounds()
    check_window()

    if int(client_width / 16) != int(client_height / 9):
        p.WARNING(f"Game window ({client_width} x {client_height}) is not 16:9\nIt is recommended to set the game to either\n1920 x 1080 or 1280 x 720")

    print("WINDOW:", p.WINDOW)