# Linux (X11) port
# Extra dependencies: python-xlib, mss

import atexit, signal, threading, subprocess
import mss
import evdev
from evdev import UInput, ecodes as e
from Xlib import X, display
import numpy as np, time, math, random
from pathgenerator import PDPathGenerator
import source.utils.params as p
from source.utils.profiles import get_macro_profile, maybe_rhythm_jitter, randomize_with_profile

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
HZ = 1000

MOUSE_FALLBACK = {
    'name': 'Logitech USB Receiver',
    'vendor': 0x046d,
    'product': 0xc52b,
    'version': 0x0111,
    'bustype': 0x03,
    'phys': 'usb-0000:00:14.0-1.2/input0',
    'events': {
        e.EV_KEY: [e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE,
                   e.BTN_SIDE, e.BTN_EXTRA],
        e.EV_REL: [e.REL_X, e.REL_Y, e.REL_WHEEL, e.REL_HWHEEL]
    },
    'input_props': []
}

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

KEYBOARD_FALLBACK = {
    'name': 'Dell USB Keyboard',
    'vendor': 0x413c,
    'product': 0x2003,
    'version': 0x0111,
    'bustype': 0x03,
    'phys': 'usb-0000:00:14.0-1.3/input0',
    'events': {
        e.EV_KEY: _safe_keys,
    },
    'input_props': []
}

mouse = None
keyboard = None
_uinput_error = None
_uinput_init_started = False
_uinput_ready = threading.Event()
_uinput_lock = threading.Lock()

def _wait_until_ns(target_ns, spin_threshold_ns=250_000):
    """
    Wait until a monotonic timestamp using a sleep+spin strategy.
    
    Absolute-deadline waits prevent cumulative drift compared to repeatedly
    sleeping relative intervals in tight loops.
    """
    while True:
        now_ns = time.perf_counter_ns()
        remaining_ns = target_ns - now_ns
        if remaining_ns <= 0:
            return

        if remaining_ns > spin_threshold_ns:
            sleep_ns = remaining_ns - spin_threshold_ns
            time.sleep(sleep_ns / 1_000_000_000)
            continue

        while time.perf_counter_ns() < target_ns:
            pass
        return


def clone_device(path: str) -> UInput:
    """Clone a real evdev device into a uinput virtual device."""
    real = evdev.InputDevice(path)
    kwargs = {
        "name": real.name,
        "vendor": real.info.vendor,
        "product": real.info.product,
        "version": real.info.version,
        "bustype": real.info.bustype,
        "phys": real.phys,
        "input_props": real.input_props(),
    }
    print(kwargs)

    try:
        return UInput.from_device(real, **kwargs)
    except OSError as ex:
        # Some devices expose event types that can trigger EINVAL in uinput.
        if ex.errno != 22:
            raise
        filtered = (e.EV_SYN, e.EV_FF, e.EV_MSC)
        return UInput.from_device(real, filtered_types=filtered, **kwargs)


def _pick_device_paths():
    paths = list(evdev.list_devices())
    mouse_path = None
    keyboard_path = None

    # We'll store potential candidates to pick the "best" one
    kbd_candidates = []

    for path in paths:
        try:
            dev = evdev.InputDevice(path)
            caps = dev.capabilities()
            key_caps = set(caps.get(e.EV_KEY, []))
            rel_caps = set(caps.get(e.EV_REL, []))
            
            # 1. Is it a Mouse? 
            # It MUST have relative X/Y movement.
            if e.REL_X in rel_caps and e.REL_Y in rel_caps:
                if mouse_path is None:
                    mouse_path = path
                continue # If it moves like a mouse, don't even consider it for a keyboard

            # 2. Is it a Keyboard?
            # It should have a significant number of keys (usually > 50).
            # Ignore anything that has relative movement (already handled above).
            if len(key_caps) > 50:
                # We prioritize devices with "keyboard" in the name
                name = (dev.name or "").lower()
                score = 0
                if "keyboard" in name or "kbd" in name:
                    score += 10
                
                kbd_candidates.append((score, path))

        except Exception:
            continue

    # Pick the highest-scoring keyboard candidate
    if kbd_candidates:
        kbd_candidates.sort(key=lambda x: x[0], reverse=True)
        keyboard_path = kbd_candidates[0][1]

    return mouse_path, keyboard_path


def _disable_mouse_accel_x11(device_name):
    """Best-effort: set flat accel profile for matching XInput devices."""
    if not device_name:
        return

    try:
        out = subprocess.check_output(
            ["xinput", "list", "--id-only", device_name],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return

    ids = [line.strip() for line in out.splitlines() if line.strip().isdigit()]
    for dev_id in ids:
        subprocess.run(
            ["xinput", "set-prop", dev_id, "libinput Accel Profile Enabled", "0", "1"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            ["xinput", "set-prop", dev_id, "libinput Accel Speed", "0"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def _init_uinput_devices():
    """Initialize uinput devices once and publish result to globals."""
    global mouse, keyboard, _uinput_error
    try:
        mouse_path, keyboard_path = _pick_device_paths()

        if mouse_path:
            try:
                local_mouse = clone_device(mouse_path)
                print(f"Cloning mouse from {mouse_path}")
            except Exception as ex:
                print(f"[!] Mouse clone failed ({mouse_path}): {ex}")
                print("No mouse found – using fallback.")
                local_mouse = UInput(**MOUSE_FALLBACK)
        else:
            print("No mouse found – using fallback.")
            local_mouse = UInput(**MOUSE_FALLBACK)

        _disable_mouse_accel_x11(getattr(local_mouse, "name", None))

        if keyboard_path:
            try:
                local_keyboard = clone_device(keyboard_path)
                print(f"Cloning keyboard from {keyboard_path}")
            except Exception as ex:
                print(f"[!] Keyboard clone failed ({keyboard_path}): {ex}")
                print("No keyboard found – using fallback.")
                local_keyboard = UInput(**KEYBOARD_FALLBACK)
        else:
            print("No keyboard found – using fallback.")
            local_keyboard = UInput(**KEYBOARD_FALLBACK)

        with _uinput_lock:
            mouse = local_mouse
            keyboard = local_keyboard
    except Exception as ex:
        _uinput_error = ex
    finally:
        _uinput_ready.set()

def _prewarm_uinput_async():
    """Start async uinput init so startup can continue immediately."""
    global _uinput_init_started
    with _uinput_lock:
        if _uinput_init_started:
            return
        _uinput_init_started = True
    threading.Thread(target=_init_uinput_devices, name="uinput-init", daemon=True).start()

def _ensure_uinput_ready():
    _prewarm_uinput_async()
    _uinput_ready.wait()
    if _uinput_error is not None:
        raise _uinput_error


def _get_mouse():
    _ensure_uinput_ready()
    return mouse

def _get_keyboard():
    _ensure_uinput_ready()
    return keyboard

# Map logical buttons
_BUTTON_MAP = {'left': e.BTN_LEFT, 'middle': e.BTN_MIDDLE, 'right': e.BTN_RIGHT}

def release_all(signum=None, frame=None):
    for dev in (mouse, keyboard):
        if dev is None:
            continue
        for btn in  _BUTTON_MAP.values():
            try:
                dev.write(e.EV_KEY, btn, 0)
            except Exception:
                pass
        for key in _safe_keys:
            try:
                dev.write(e.EV_KEY, key, 0)
            except Exception:
                pass
        try:
            dev.syn()
        except Exception:
            pass

signal.signal(signal.SIGINT, release_all)
signal.signal(signal.SIGTERM, release_all)
atexit.register(release_all)

# Kick off async init immediately; first input call blocks only if still warming up.
_prewarm_uinput_async()

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

def _human_delay(min_delay=0.01, max_delay=0.03):
    time.sleep(random.uniform(min_delay, max_delay))

def mouseDown(button='left', delay=0.16):
    _fail_safe_check()
    dev = _get_mouse()
    _btn = _BUTTON_MAP.get(button.lower(), e.BTN_LEFT)
    dev.write(e.EV_KEY, _btn, 1)
    dev.syn()
    _human_delay(delay, delay + 0.04)
    _fail_safe_check()

def mouseUp(button='left', delay=0.16):
    _fail_safe_check()
    dev = _get_mouse()
    _btn = _BUTTON_MAP.get(button.lower(), e.BTN_LEFT)
    dev.write(e.EV_KEY, _btn, 0)
    dev.syn()
    _human_delay(delay, delay + 0.05)
    _fail_safe_check()

def _to_absolute(x, y):
    """For X, absolute coords are pixel coordinates (no 0..65535 scaling)."""
    return int(round(x)), int(round(y))

def _cap_rel_delta(dx, dy, max_step=22):
    """Limit a single relative write to avoid visible jumpy corrections."""
    capped_dx = max(-max_step, min(max_step, dx))
    capped_dy = max(-max_step, min(max_step, dy))
    return capped_dx, capped_dy


def _emit_rel_open_loop(dev, dx, dy):
    """Emit a relative movement step using rounded carry to preserve sub-pixel intent."""
    ix = int(round(dx))
    iy = int(round(dy))
    if ix == 0 and iy == 0:
        return
    dev.write(e.EV_REL, e.REL_X, ix)
    dev.write(e.EV_REL, e.REL_Y, iy)
    dev.syn()


def _apply_macro_rhythm(profile=None):
    _fail_safe_check()
    profile = profile or get_macro_profile()
    pause, (dx, dy) = maybe_rhythm_jitter(profile)
    dev = _get_mouse()

    if dx != 0 or dy != 0:
        dev.write(e.EV_REL, e.REL_X, dx)
        dev.write(e.EV_REL, e.REL_Y, dy)
        dev.syn()
        _human_delay(0.004, 0.012)

    if pause > 0:
        time.sleep(pause)
    _fail_safe_check()

def moveTo(x, y, duration=0.0, tween=easeInOutQuad, delay=0.09, humanize=True,
           mouse_velocity=0.65, noise=2.6, offset_x=0, offset_y=0):
    _fail_safe_check()
    dev = _get_mouse()

    profile = get_macro_profile()
    if humanize:
        delay = randomize_with_profile(delay, profile=profile, key="delay_jitter")
    
    duration += delay
    start_x, start_y = get_position()

    if mouse_velocity == 0.65:
        mouse_velocity = profile["mouse_velocity"]
    if noise == 2.6:
        noise = profile["noise"]

    if humanize:
        endpoint_jitter = profile["endpoint_jitter_px"]
        x += random.randint(-endpoint_jitter, endpoint_jitter)
        y += random.randint(-endpoint_jitter, endpoint_jitter)

        gen = PDPathGenerator()
        path, progress, steps, params = gen.generate_path(
            start_x=start_x, start_y=start_y,
            end_x=x, end_y=y,
            mouse_velocity=mouse_velocity,
            noise=noise,
            offset_x=offset_x, offset_y=offset_y
        )
        steps = max(10, steps*5)
        
        if duration > delay:
            total_duration = duration
        else:
            total_duration = params.get('duration', duration)
        
        total_duration *= 5
        step_delay = total_duration / steps if steps > 0 else 0.01
        step_jitter_min, step_jitter_max = profile["step_sleep_jitter"]

        poll_period_ns = max(1, int(1_000_000_000 / HZ))
        next_tick_ns = time.perf_counter_ns()
        prev_plan_x, prev_plan_y = _to_absolute(start_x, start_y)

        for i, (cur_x, cur_y) in enumerate(path):
            target_abs_x, target_abs_y = _to_absolute(cur_x, cur_y)
            dx = target_abs_x - prev_plan_x
            dy = target_abs_y - prev_plan_y
            _emit_rel_open_loop(dev, dx, dy)
            prev_plan_x, prev_plan_y = target_abs_x, target_abs_y

            if i < steps - 1:
                sleep_time = step_delay * random.uniform(step_jitter_min, step_jitter_max)
                step_ns = max(poll_period_ns, int(max(0.0, sleep_time) * 1_000_000_000))
                next_tick_ns += step_ns
                _wait_until_ns(next_tick_ns)
    else:
        distance = math.hypot(x - start_x, y - start_y)
        time_steps = max(2, int(duration * 400))
        distance_steps = int(distance / 1)
        steps = max(3, min(max(time_steps, distance_steps), 1000))

        poll_period_ns = max(1, int(1_000_000_000 / HZ))
        next_tick_ns = time.perf_counter_ns()
        prev_plan_x, prev_plan_y = _to_absolute(start_x, start_y)

        for i in range(steps):
            progress = tween(i / (steps - 1))
            current_x = start_x + (x - start_x) * progress
            current_y = start_y + (y - start_y) * progress

            # Clamp to avoid overshoot.
            current_x = min(max(current_x, min(start_x, x)), max(start_x, x))
            current_y = min(max(current_y, min(start_y, y)), max(start_y, y))

            target_abs_x, target_abs_y = _to_absolute(current_x, current_y)
            dx = target_abs_x - prev_plan_x
            dy = target_abs_y - prev_plan_y
            _emit_rel_open_loop(dev, dx, dy)
            prev_plan_x, prev_plan_y = target_abs_x, target_abs_y

            step_sleep = duration / (steps - 1)
            if i < steps - 1 and step_sleep > 0:
                step_ns = max(poll_period_ns, int(step_sleep * 1_000_000_000))
                next_tick_ns += step_ns
                _wait_until_ns(next_tick_ns)

    target_x, target_y = _to_absolute(x, y)
    timeout_start = time.time()
    while time.time() - timeout_start < 0.08:
        actual_x, actual_y = get_position()
        dx = target_x - actual_x
        dy = target_y - actual_y

        if abs(dx) <= 1 and abs(dy) <= 1:
            break

        dx, dy = _cap_rel_delta(dx, dy, max_step=10)
        
        dev.write(e.EV_REL, e.REL_X, dx)
        dev.write(e.EV_REL, e.REL_Y, dy)
        dev.syn()

        _wait_until_ns(time.perf_counter_ns() + max(1, int(1_000_000_000 / HZ)))

    human_final_min, human_final_max = profile["final_delay_human"]
    nonhuman_final_min, nonhuman_final_max = profile["final_delay_nonhuman"]
    final_delay = (
        random.uniform(human_final_min, human_final_max)
        if humanize
        else random.uniform(nonhuman_final_min, nonhuman_final_max)
    )
    time.sleep(final_delay)
    _fail_safe_check()

def click(x=None, y=None, button='left', clicks=1, interval=0.1, duration=0.0, tween=easeInOutQuad, delay=0.03):
    _fail_safe_check()
    profile = get_macro_profile()
    _apply_macro_rhythm(profile)
    delay = randomize_with_profile(delay, profile=profile, key="delay_jitter")
    interval += 0.05

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
            time.sleep(randomize_with_profile(interval, profile=profile, key="click_interval_jitter"))
            _fail_safe_check()

def dragTo(x, y, duration=0.1, tween=easeInOutQuad, button='left', start_x=None, start_y=None):
    _fail_safe_check()
    _apply_macro_rhythm()
    if start_x is not None and start_y is not None:
        moveTo(start_x, start_y)
    mouseDown(button, delay=0.03)
    moveTo(x, y, duration, tween, humanize=False)
    mouseUp(button, delay=0.03)
    _fail_safe_check()

def scroll(clicks, x=None, y=None):
    """Scroll vertically: positive clicks -> up, negative -> down."""
    _fail_safe_check()
    dev = _get_mouse()
    _apply_macro_rhythm()
    if x is not None and y is not None:
        moveTo(x, y)
    direction = 1 if clicks > 0 else -1
    count = abs(int(clicks))
    
    for _ in range(count):
        _fail_safe_check()
        dev.write(e.EV_REL, e.REL_WHEEL, direction)
        dev.syn()
        time.sleep(0.02)
        
    _human_delay()

# Keyboard functions
def _key_to_ecode(key):
    return _EVDEV_KEYSYM_MAP.get(key.lower(), None)

def press(keys, presses=1, interval=0.1, delay=0.01):
    _fail_safe_check()
    dev = _get_keyboard()
    profile = get_macro_profile()
    _apply_macro_rhythm(profile)
    time.sleep(randomize_with_profile(delay, profile=profile, key="delay_jitter"))
    delay = randomize_with_profile(delay, profile=profile, key="delay_jitter")
    interval = randomize_with_profile(interval, profile=profile, key="key_interval_jitter")

    for _p in range(presses):
        if isinstance(keys, str):
            keys = [keys]

        ecodes = []
        for key in keys:
            _fail_safe_check()
            kc = _key_to_ecode(key)
            if not kc:
                continue
            ecodes.append(kc)
            dev.write(e.EV_KEY, kc, 1) # Press
            dev.syn()
            time.sleep(delay)

        for kc in reversed(ecodes):
            _fail_safe_check()
            dev.write(e.EV_KEY, kc, 0) # Release
            dev.syn()
            time.sleep(delay)

        if interval > 0 and _p < presses - 1:
            time.sleep(interval)
            _fail_safe_check()

def hotkey(*args, **kwargs):
    press(list(args), **kwargs)


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