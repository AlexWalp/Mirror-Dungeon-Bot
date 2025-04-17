import logging, sys

logging.basicConfig(
    filename='game.log',  # Log file name
    level=logging.INFO,   # Logging level
    format='%(asctime)s - %(levelname)s - %(message)s'
)

original_excepthook = sys.excepthook

def log_uncaught_exceptions(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    original_excepthook(exc_type, exc_value, exc_traceback)

sys.excepthook = log_uncaught_exceptions