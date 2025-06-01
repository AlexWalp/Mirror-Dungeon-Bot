import logging, sys, os

def setup_logging(enable_logging: bool = True, log_file = 'game.log', log_level=logging.INFO):
    if not enable_logging:
        logging.disable(logging.CRITICAL)
        return

    documents_path = os.path.join(os.environ["USERPROFILE"], "Documents", "ChargeGrinder")
    if not os.path.exists(documents_path):
        os.makedirs(documents_path)

    logging.basicConfig(
        filename=f"{documents_path}/{log_file}",
        level=log_level,
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