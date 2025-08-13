from source_app.utils import *


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

    def __init__(self, is_lux, count, count_exp, count_thd, teams, settings, hard, app):
        super().__init__()
        self.is_lux = is_lux
        self.count = count
        self.count_exp = count_exp
        self.count_thd = count_thd
        self.teams = teams
        self.settings = settings
        self.hard = hard
        self.app = app

    def run(self):
        try:
            Bot.execute_me(
                self.is_lux,
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
            self.error.emit(str(e))
        finally:
            self.finished.emit()