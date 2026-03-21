from .utils import *
import platform

def _is_interception_driver_installed():
    try:
        import interception
        return interception.inputs._g_context.valid
    except Exception:
        return False

def ensure_interception_driver(app_parent=None):
    if platform.system() != "Windows" or _is_interception_driver_installed():
        return True

    driver_download_url = "https://github.com/oblitum/Interception/releases"

    msg = QMessageBox(app_parent)
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowTitle("Interception Driver Required")
    msg.setText("Interception driver is not installed.")
    msg.setInformativeText("Open the official Interception download page now?")
    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    if msg.exec() != QMessageBox.StandardButton.Yes:
        return False

    QMessageBox.information(
        app_parent,
        "Download Interception Driver",
        "A browser page will open. Install the driver manually, reboot your PC, then relaunch ChargeGrinder."
    )

    try:
        webbrowser.open(driver_download_url)
    except Exception:
        QMessageBox.warning(
            app_parent,
            "Open Browser Failed",
            f"Could not open the browser automatically. Please visit:\n{driver_download_url}"
        )

    return False