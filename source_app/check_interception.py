import platform

def _is_interception_driver_installed():
    # Interception driver is no longer used — replaced with Win32 SendInput.
    return True

def ensure_interception_driver(app_parent=None):
    return True
