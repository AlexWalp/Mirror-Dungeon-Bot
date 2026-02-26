# Linux (X11) port
# Extra dependencies: python-xlib, mss

import mss
from Xlib import X, XK, display
from Xlib.ext import xtest
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


# Map logical buttons to X button numbers
_BUTTON_MAP = {'left': 1, 'middle': 2, 'right': 3}

def _fail_safe_check():
    """Check fail-safe"""
    if not FAILSAFE_ENABLED:
        return

    x, y = get_position()
    width, height = get_screen_size()
    name = getActiveWindowTitle()

    if p.LIMBUS_NAME not in name: 
        raise PauseException(name)
    if (x == 0 or x == width - 1) and (y == 0 or y == height - 1):
        raise FailSafeException(f"Mouse out of screen bounds at ({x}, {y})")

class WindowError(Exception): pass
class FailSafeException(Exception): pass
class ImageNotFoundException(Exception): pass
class PauseException(Exception):
    def __init__(self, name):
        super().__init__(name)
        self.window = name

# Mouse functions using XTest
def mouseDown(button='left', delay=0.09):
    _button = _BUTTON_MAP.get(button.lower(), 1)
    xtest.fake_input(_disp, X.ButtonPress, _button)
    _disp.sync()
    time.sleep(delay)

def mouseUp(button='left', delay=0.09):
    _button = _BUTTON_MAP.get(button.lower(), 1)
    xtest.fake_input(_disp, X.ButtonRelease, _button)
    _disp.sync()
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

        abs_x, abs_y = _to_absolute(current_x, current_y)
        xtest.fake_input(_disp, X.MotionNotify, x=abs_x, y=abs_y)
        _disp.sync()

        if i < steps - 1:
            if humanize:
                sleep_time = duration / steps * random.uniform(0.8, 1.2)
                time.sleep(max(0.001, sleep_time))
            else:
                time.sleep(duration / steps)

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

    button_up = 4   # wheel up
    button_down = 5 # wheel down
    count = abs(int(clicks))
    if clicks > 0:
        for _ in range(count):
            xtest.fake_input(_disp, X.ButtonPress, button_up)
            xtest.fake_input(_disp, X.ButtonRelease, button_up)
    elif clicks < 0:
        for _ in range(count):
            xtest.fake_input(_disp, X.ButtonPress, button_down)
            xtest.fake_input(_disp, X.ButtonRelease, button_down)
    _disp.sync()
    _human_delay()

# Keyboard functions
_BASIC_KEYSYM_MAP = {
    'enter': 'Return',
    'esc': 'Escape',
    'space': 'space',
    'tab': 'Tab',
    'backspace': 'BackSpace',
    'delete': 'Delete',
    'insert': 'Insert',
    'home': 'Home',
    'end': 'End',
    'pageup': 'Page_Up',
    'pagedown': 'Page_Down',
    'shift': 'Shift_L',
    'ctrl': 'Control_L',
    'alt': 'Alt_L',
    'win': 'Super_L',
    'up': 'Up',
    'down': 'Down',
    'left': 'Left',
    'right': 'Right',
    'f1': 'F1', 'f2': 'F2', 'f3': 'F3', 'f4': 'F4',
    'f5': 'F5', 'f6': 'F6', 'f7': 'F7', 'f8': 'F8',
    'f9': 'F9', 'f10': 'F10', 'f11': 'F11', 'f12': 'F12',
}

def _key_to_keycode(key):
    """Convert a logical key (like 'a', 'enter') to an X keycode."""
    # letters and digits: use the character directly
    if len(key) == 1:
        ks = XK.string_to_keysym(key)
    else:
        mapped = _BASIC_KEYSYM_MAP.get(key.lower(), None)
        if mapped:
            ks = XK.string_to_keysym(mapped)
        else:
            # try raw
            ks = XK.string_to_keysym(key)
    if ks == 0:
        return None
    return _disp.keysym_to_keycode(ks)

def press(keys, presses=1, interval=0.1, delay=0.01):
    """
    Press keys. keys may be a string or list of strings.
    For multi-key combos pass list e.g. ['ctrl', 'c']
    """
    for _p in range(presses):
        if isinstance(keys, str):
            keys = [keys]

        # Press down
        keycodes = []
        for key in keys:
            kc = _key_to_keycode(key)
            if not kc:
                continue
            keycodes.append(kc)
            xtest.fake_input(_disp, X.KeyPress, kc)
            _disp.sync()
            time.sleep(delay)

        # Release in reverse order
        for kc in reversed(keycodes):
            xtest.fake_input(_disp, X.KeyRelease, kc)
            _disp.sync()
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