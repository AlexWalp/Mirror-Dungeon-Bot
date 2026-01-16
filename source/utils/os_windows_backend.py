import ctypes
from ctypes import wintypes
import numpy as np
import time
import math
import random
import source.utils.params as p

ctypes.windll.user32.SetProcessDPIAware()

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

# Constants
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_ABSOLUTE = 0x8000

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002

if ctypes.sizeof(ctypes.c_void_p) == 8:  # 64-bit system
    ULONG_PTR = ctypes.c_ulonglong
else:  # 32-bit system
    ULONG_PTR = ctypes.c_ulong

# Structures
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR)
    ]

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR)
    ]

class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT)
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", INPUT_UNION)
    ]

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

def _to_absolute(x, y):
    width, height = get_screen_size()
    return int((x * 65535) / width), int((y * 65535) / height)

def _human_delay(min_delay=0.01, max_delay=0.03):
    time.sleep(random.uniform(min_delay, max_delay))

def mouseDown(button='left', delay=0.09):
    flags = {
        'left': MOUSEEVENTF_LEFTDOWN,
        'right': MOUSEEVENTF_RIGHTDOWN,
        'middle': MOUSEEVENTF_MIDDLEDOWN
    }.get(button.lower(), MOUSEEVENTF_LEFTDOWN)
    
    inputs = [
        INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=MOUSEINPUT(
            dx=0,
            dy=0,
            mouseData=0,
            dwFlags=flags | MOUSEEVENTF_ABSOLUTE,
            time=0,
            dwExtraInfo=0
        )))
    ]
    user32.SendInput(1, ctypes.byref(inputs[0]), ctypes.sizeof(INPUT))
    _human_delay(delay, delay + 0.02)

def mouseUp(button='left', delay=0.09):
    flags = {
        'left': MOUSEEVENTF_LEFTUP,
        'right': MOUSEEVENTF_RIGHTUP,
        'middle': MOUSEEVENTF_MIDDLEUP
    }.get(button.lower(), MOUSEEVENTF_LEFTUP)
    
    inputs = [
        INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=MOUSEINPUT(
            dx=0,
            dy=0,
            mouseData=0,
            dwFlags=flags | MOUSEEVENTF_ABSOLUTE,
            time=0,
            dwExtraInfo=0
        )))
    ]
    user32.SendInput(1, ctypes.byref(inputs[0]), ctypes.sizeof(INPUT))
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

def set_failsafe(state=True):
    """Enable or disable the fail-safe feature"""
    global FAILSAFE_ENABLED
    FAILSAFE_ENABLED = state


def _fail_safe_check():
    """Check if mouse is in fail-safe position and raise exception if needed"""
    if not FAILSAFE_ENABLED:
        return
    
    x, y = get_position()
    width, height = get_screen_size()
    name = getActiveWindowTitle()
    
    if name != p.LIMBUS_NAME:
        raise PauseException(name)


def moveTo(x, y, duration=0.0, tween=easeInOutQuad, delay=0.08, humanize=True):
    _fail_safe_check()
    
    duration += delay  # Emulating pyautogui delay
    start_x, start_y = get_position()
    steps = max(2, int(duration * 100))
    
    # Human-like movement parameters
    if humanize:
        curve_intensity = random.uniform(0.3, 0.7)  # How much the path curves
        jitter_frequency = random.randint(3, 7)     # How many small deviations
        jitter_magnitude = random.uniform(0.5, 2.0) # How strong the deviations are
    
    for i in range(steps):
        progress = tween(i / (steps - 1))
        
        # Base linear movement
        linear_x = start_x + (x - start_x) * progress
        linear_y = start_y + (y - start_y) * progress
        
        if humanize and duration > 0.1:  # Only humanize longer movements
            # Add curved path deviation
            curve_progress = math.sin(progress * math.pi)
            curve_offset_x = (y - start_y) * curve_intensity * curve_progress * 0.3
            curve_offset_y = (x - start_x) * curve_intensity * curve_progress * -0.3
            
            # Add small random jitters
            jitter_x = (math.sin(i * jitter_frequency) * 
                       (x - start_x) * 0.01 * jitter_magnitude)
            jitter_y = (math.cos(i * jitter_frequency) * 
                       (y - start_y) * 0.01 * jitter_magnitude)
            
            current_x = linear_x + curve_offset_x + jitter_x
            current_y = linear_y + curve_offset_y + jitter_y
        else:
            current_x = linear_x
            current_y = linear_y
        
        # Ensure we don't overshoot the target
        current_x = min(max(current_x, min(start_x, x)), max(start_x, x))
        current_y = min(max(current_y, min(start_y, y)), max(start_y, y))
        
        abs_x, abs_y = _to_absolute(current_x, current_y)
        inputs = [
            INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=MOUSEINPUT(
                dx=abs_x,
                dy=abs_y,
                mouseData=0,
                dwFlags=MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE,
                time=0,
                dwExtraInfo=0
            )))
        ]
        user32.SendInput(1, ctypes.byref(inputs[0]), ctypes.sizeof(INPUT))
        
        if i < steps - 1:
            # Variable speed during movement
            if humanize:
                # Randomize sleep time slightly
                sleep_time = duration / steps * random.uniform(0.8, 1.2)
                time.sleep(max(0.001, sleep_time))
            else:
                time.sleep(duration / steps)
    
    # Final small delay with randomization
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
    if x is not None and y is not None:
        moveTo(x, y)
    
    inputs = [
        INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=MOUSEINPUT(
            dx=0,
            dy=0,
            mouseData=clicks * 120,
            dwFlags=MOUSEEVENTF_WHEEL,
            time=0,
            dwExtraInfo=0
        )))
    ]
    user32.SendInput(1, ctypes.byref(inputs[0]), ctypes.sizeof(INPUT))
    _human_delay()

# Keyboard functions
VK_MAP = {
    'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45, 'f': 0x46,
    'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A, 'k': 0x4B, 'l': 0x4C,
    'm': 0x4D, 'n': 0x4E, 'o': 0x4F, 'p': 0x50, 'q': 0x51, 'r': 0x52,
    's': 0x53, 't': 0x54, 'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58,
    'y': 0x59, 'z': 0x5A,
    '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34, '5': 0x35,
    '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,
    'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73, 'f5': 0x74, 'f6': 0x75,
    'f7': 0x76, 'f8': 0x77, 'f9': 0x78, 'f10': 0x79, 'f11': 0x7A, 'f12': 0x7B,
    'esc': 0x1B, 'enter': 0x0D, 'tab': 0x09, 'space': 0x20, 'backspace': 0x08,
    'delete': 0x2E, 'insert': 0x2D, 'home': 0x24, 'end': 0x23, 'pageup': 0x21,
    'pagedown': 0x22, 'shift': 0x10, 'ctrl': 0x11, 'alt': 0x12, 'win': 0x5B,
    'up': 0x26, 'down': 0x28, 'left': 0x25, 'right': 0x27
}

def press(keys, presses=1, interval=0.1, delay=0.01):
    for _ in range(presses):
        if isinstance(keys, str):
            keys = [keys]
        
        # Press down
        for key in keys:
            vk = VK_MAP.get(key.lower(), 0)
            if vk:
                inputs = [
                    INPUT(type=INPUT_KEYBOARD, union=INPUT_UNION(ki=KEYBDINPUT(
                        wVk=vk,
                        wScan=0,
                        dwFlags=0,
                        time=0,
                        dwExtraInfo=0
                    )))
                ]
                user32.SendInput(1, ctypes.byref(inputs[0]), ctypes.sizeof(INPUT))
                time.sleep(delay)
        
        # Release keys in reverse order
        for key in reversed(keys):
            vk = VK_MAP.get(key.lower(), 0)
            if vk:
                inputs = [
                    INPUT(type=INPUT_KEYBOARD, union=INPUT_UNION(ki=KEYBDINPUT(
                        wVk=vk,
                        wScan=0,
                        dwFlags=KEYEVENTF_KEYUP,
                        time=0,
                        dwExtraInfo=0
                    )))
                ]
                user32.SendInput(1, ctypes.byref(inputs[0]), ctypes.sizeof(INPUT))
                time.sleep(delay)
        
        if interval > 0 and _ < presses - 1:
            time.sleep(interval)

def hotkey(*args, **kwargs):
    press(list(args), **kwargs)

# Anti-cheat enhancements
def add_mouse_jitter(max_offset=5):
    """Add small random movement to avoid perfect straight lines"""
    x, y = get_position()
    jitter = random.randint(-max_offset, max_offset)
    moveTo(x + jitter, y + jitter, duration=0.05)

def randomize_delay(base_delay):
    """Add randomness to timing patterns"""
    return base_delay * random.uniform(0.8, 1.2)


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