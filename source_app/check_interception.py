import platform

def _is_interception_driver_installed():
    # Interception driver is no longer used — replaced with PostMessage-based input.
    return True

def ensure_interception_driver(app_parent=None):
    return True
