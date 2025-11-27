from source_app.utils import *
from source_app.cache import CacheWorker


class VersionChecker(QThread):
    versionFetched = pyqtSignal(bool)  # Emits True if current version is up to date

    def run(self):
        url = 'https://api.github.com/repos/AlexWalp/Mirror-Dungeon-Bot/releases/latest'
        try:
            with urlopen(url, timeout=5) as response:
                data = response.read()
                release_info = json.loads(data)
                latest_version = str(release_info["tag_name"][1:])
        except Exception:
            self.versionFetched.emit(True)
            return

        try:
            v1 = list(map(int, latest_version.split('.')))
            v2 = list(map(int, p.V.split('.')))
            is_up_to_date = v1 <= v2
        except Exception:
            is_up_to_date = True

        self.versionFetched.emit(is_up_to_date)

# Handle bot proccess
class BotWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    warning = pyqtSignal(str)

    def __init__(self, count, count_exp, count_thd, teams, settings, hard, app):
        super().__init__()
        self.count = count
        self.count_exp = count_exp
        self.count_thd = count_thd
        self.teams = teams
        self.settings = settings
        self.hard = hard
        self.app = app

        self.cache_thread = None
        self.cache_worker = None

    def run(self):
        try:
            teams_filtered = {k: v for k, v in self.teams.items() if k < 7}
            if teams_filtered:
                self.start_cache_thread(teams_filtered, self.settings, self.hard)

            Bot.execute_me(
                self.count,
                self.count_exp,
                self.count_thd,
                self.teams,
                self.settings,
                self.hard,
                self.app,
                warning=self.warning.emit
            )
        except Exception as e:
            logging.exception("Uncaught exception in BotWorker thread")  
            self.error.emit(str(e))
        finally:
            self.finished.emit()

    def start_cache_thread(self, teams, settings, hard):
        self.cache_thread = QThread()
        self.cache_worker = CacheWorker(teams, settings, hard)

        self.cache_worker.moveToThread(self.cache_thread)
        self.cache_thread.started.connect(self.cache_worker.run)
        self.cache_worker.finished.connect(self.cache_thread.quit)
        self.cache_worker.finished.connect(self.cache_worker.deleteLater)
        self.cache_thread.finished.connect(self.cache_thread.deleteLater)

        self.cache_thread.start()