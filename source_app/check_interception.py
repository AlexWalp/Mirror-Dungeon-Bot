from .utils import *
import ctypes, platform

DRIVER_INSTALLER = os.path.join(Bot.BASE_PATH, "drivers/install-interception.exe")

def _is_interception_driver_installed():
    try:
        import interception
        return interception.inputs._g_context.valid
    except Exception:
        return False

def ensure_interception_driver(app_parent=None):
    if platform.system() != "Windows" or _is_interception_driver_installed():
        return True

    msg = QMessageBox(app_parent)
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowTitle("Interception Driver Required")
    msg.setText("Interception driver is not installed.")
    msg.setInformativeText("Install it now? The installer will request administrator permission.")
    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    if msg.exec() != QMessageBox.StandardButton.Yes:
        return False

    if not os.path.exists(DRIVER_INSTALLER):
        QMessageBox.critical(
            app_parent,
            "Installer Not Found",
            "Could not find drivers/install-interception.exe"
        )
        return False

    # ShellExecuteW returns a value > 32 when launch succeeds.
    result = ctypes.windll.shell32.ShellExecuteW(None, "runas", DRIVER_INSTALLER, "/install", None, 1)
    if int(result) <= 32:
        QMessageBox.critical(
            app_parent,
            "Installation Failed",
            "Interception driver installation was canceled or failed."
        )
        return False

    QMessageBox.information(
        app_parent,
        "Reboot Required",
        "Interception driver installation finished. Please reboot your PC before using ChargeGrinder."
    )
    return False