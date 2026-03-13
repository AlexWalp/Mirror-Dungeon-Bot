import logging, sys, os

from source.utils.discord_webhook import WebhookLogHandler, create_handler_from_env


def _detach_webhook_handlers():
    root_logger = logging.getLogger()
    for handler in list(root_logger.handlers):
        if isinstance(handler, WebhookLogHandler):
            root_logger.removeHandler(handler)
            handler.close()


def _attach_webhook_handler():
    handler, error_message = create_handler_from_env()
    if error_message:
        logging.warning(error_message)
        return

    if handler:
        logging.info("Discord webhook notifications enabled.")
        logging.getLogger().addHandler(handler)

def setup_logging(enable_logging: bool = True, log_file: str = "game.log", log_level=logging.INFO):
    _detach_webhook_handlers()

    if not enable_logging:
        logging.disable(logging.CRITICAL)
        return

    logging.disable(logging.NOTSET)
    
    appimage_path = os.environ.get("APPIMAGE")
    if appimage_path:
        # Linux AppImage
        base_path = os.path.dirname(appimage_path)
    elif getattr(sys, "frozen", False):
        # Normal PyInstaller exe
        base_path = os.path.dirname(sys.executable)
    else:
        # Running from source
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    log_path = os.path.join(base_path, log_file)

    logging.basicConfig(
        filename=str(log_path),
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    _attach_webhook_handler()

    original_excepthook = sys.excepthook

    def log_uncaught_exceptions(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        original_excepthook(exc_type, exc_value, exc_traceback)

    sys.excepthook = log_uncaught_exceptions
