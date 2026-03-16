import ctypes
from ctypes import wintypes
import numpy as np
import time
import math
import random
import source.utils.params as p
from source.utils.profiles import get_macro_profile, maybe_rhythm_jitter, randomize_with_profile

import interception
from pathgenerator import PDPathGenerator


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD),
        ("biWidth", wintypes.LONG),
        ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", wintypes.LONG),
        ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD)
    ]

class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ("bmiHeader", BITMAPINFOHEADER),
        ("bmiColors", wintypes.DWORD * 3)
    ]

def screenshot(imageFilename=None, region=None, allScreens=False):
    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    
    if allScreens:
        width = user32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
        height = user32.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN
        x, y = user32.GetSystemMetrics(76), user32.GetSystemMetrics(77)  # SM_XVIRTUALSCREEN, SM_YVIRTUALSCREEN
    else:
        width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
        height = user32.GetSystemMetrics(1)  # SM_CYSCREEN
        x = y = 0
    
    if region:
        x, y, rwidth, rheight = region
        width, height = rwidth, rheight
    else:
        region = (x, y, width, height)
    
    hdc = user32.GetDC(None)
    mfc_dc = gdi32.CreateCompatibleDC(hdc)
    bitmap = gdi32.CreateCompatibleBitmap(hdc, width, height)
    gdi32.SelectObject(mfc_dc, bitmap)
    
    gdi32.BitBlt(mfc_dc, 0, 0, width, height, hdc, x, y, 0x00CC0020)  # SRCCOPY
    
    try:
        bmpinfo = BITMAPINFO()
        bmpinfo.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmpinfo.bmiHeader.biWidth = width
        bmpinfo.bmiHeader.biHeight = -height
        bmpinfo.bmiHeader.biPlanes = 1
        bmpinfo.bmiHeader.biBitCount = 32
        bmpinfo.bmiHeader.biCompression = 0
        
        buffer_len = width * height * 4
        buffer = ctypes.create_string_buffer(buffer_len)
        gdi32.GetDIBits(mfc_dc, bitmap, 0, height, buffer, ctypes.byref(bmpinfo), 0)
        
        arr = np.frombuffer(buffer, dtype=np.uint8).reshape((height, width, 4))
        arr = arr[:, :, :3]  # Remove alpha channel
        
        if imageFilename:
            import cv2  # Will raise error if not available
            cv2.imwrite(imageFilename, arr)
        return arr

    finally:
        # Cleanup
        gdi32.DeleteObject(bitmap)
        gdi32.DeleteDC(mfc_dc)
        user32.ReleaseDC(None, hdc)


user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

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

# Helper functions
def get_screen_size():
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

def get_position():
    point = wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(point))
    return point.x, point.y

def getActiveWindowTitle():
    hwnd = user32.GetForegroundWindow()
    length = user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    return buff.value

def center(target=None):
    """
    Returns the center coordinates of:
    - A window (if target is a string title)
    - A screen region (if target is a box tuple (left, top, width, height))
    - The primary screen (if no target)
    """
    if isinstance(target, str):  # Window title
        hwnd = user32.FindWindowW(None, target)
        if not hwnd:
            raise ValueError(f"Window not found: {target}")
        rect = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        return (
            (rect.left + rect.right) // 2,
            (rect.top + rect.bottom) // 2
        )
    elif isinstance(target, (tuple, list)) and len(target) >= 4:  # Region box
        left, top, width, height = target[:4]
        return (left + width // 2, top + height // 2)
    else:  # Primary screen center
        width, height = get_screen_size()
        return (width // 2, height // 2)

def _human_delay(min_delay=0.01, max_delay=0.03):
    time.sleep(random.uniform(min_delay, max_delay))

def mouseDown(button='left', delay=0.09):
    interception.mouse_down(button=button, delay=delay)
    _human_delay(delay, delay + 0.02)

def mouseUp(button='left', delay=0.09):
    interception.mouse_up(button=button, delay=delay)
    _human_delay(delay, delay + 0.02)


class WindowError(Exception): pass
class FailSafeException(Exception): pass
class ImageNotFoundException(Exception): pass
class PauseException(Exception):
    def __init__(self, name):
        super().__init__(name)
        self.window = name

# Global fail-safe settings
FAILSAFE = True
FAILSAFE_ENABLED = True

def randomize_delay(base_delay):
    """Add randomness to timing patterns"""
    return randomize_with_profile(base_delay)


def _apply_macro_rhythm(profile=None):
    profile = profile or get_macro_profile()
    pause, (dx, dy) = maybe_rhythm_jitter(profile)

    if dx != 0 or dy != 0:
        cur_x, cur_y = get_position()
        interception.move_to(cur_x + dx, cur_y + dy, allow_global_params=False)
        _human_delay(0.004, 0.012)

    if pause > 0:
        time.sleep(pause)

def set_failsafe(state=True):
    """Enable or disable the fail-safe feature"""
    global FAILSAFE_ENABLED
    FAILSAFE_ENABLED = state


def _fail_safe_check():
    """Check if mouse is in fail-safe position and raise exception if needed"""
    if not FAILSAFE_ENABLED:
        return
    
    name = getActiveWindowTitle()
    
    if p.LIMBUS_NAME not in name:
        raise PauseException(name)


def moveTo(x, y, duration=0.0, tween=easeInOutQuad, delay=0.11, humanize=True,
           mouse_velocity=0.65, noise=2.6, offset_x=0, offset_y=0):
    _fail_safe_check()

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

        total_duration = params.get('duration', duration)
        step_delay = total_duration / steps if steps > 0 else 0.01
        step_jitter_min, step_jitter_max = profile["step_sleep_jitter"]

        for i, (cur_x, cur_y) in enumerate(path):
            interception.move_to(cur_x, cur_y, allow_global_params=False)

            if i < steps - 1:
                sleep_time = step_delay * random.uniform(step_jitter_min, step_jitter_max)
                time.sleep(max(0.001, sleep_time))

    else:
        distance = math.hypot(x - start_x, y - start_y)
        time_steps = max(2, int(duration * 400))
        distance_steps = int(distance / 1)
        steps = max(3, min(max(time_steps, distance_steps), 1000))

        for i in range(steps):
            progress = tween(i / (steps - 1))
            current_x = start_x + (x - start_x) * progress
            current_y = start_y + (y - start_y) * progress

            # Clamp to avoid overshoot
            current_x = min(max(current_x, min(start_x, x)), max(start_x, x))
            current_y = min(max(current_y, min(start_y, y)), max(start_y, y))

            interception.move_to(current_x, current_y, allow_global_params=False)

            step_sleep = duration / (steps - 1)
            if i < steps - 1 and step_sleep > 0:
                time.sleep(step_sleep)

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
    _apply_macro_rhythm()
    if x is not None and y is not None:
        moveTo(x, y)
    
    direction = "up" if clicks > 0 else "down"
    interception.scroll(direction)
    _human_delay()


def press(keys, presses=1, interval=0.1, delay=0.01):
    profile = get_macro_profile()
    _apply_macro_rhythm(profile)
    time.sleep(randomize_with_profile(delay, profile=profile, key="delay_jitter"))
    interval = randomize_with_profile(interval, profile=profile, key="key_interval_jitter")
    interception.press(keys, presses=presses, interval=interval)

def hotkey(*args, **kwargs):
    press(list(args), **kwargs)


def check_window():
    user32 = ctypes.windll.user32

    vx = user32.GetSystemMetrics(76)
    vy = user32.GetSystemMetrics(77)
    vw = user32.GetSystemMetrics(78)
    vh = user32.GetSystemMetrics(79)

    vright = vx + vw
    vbottom = vy + vh

    left, top, width, height = p.WINDOW
    right = left + width
    bottom = top + height

    in_bounds = (
        left >= vx and
        top >= vy and
        right <= vright and
        bottom <= vbottom
    )
    if not in_bounds:
        raise WindowError("Window is partially or completely out of screen bounds!")

def set_window():
    hwnd = ctypes.windll.user32.FindWindowW(None, p.LIMBUS_NAME)

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