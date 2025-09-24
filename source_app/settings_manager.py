from source_app.utils import *

class SettingsManager:
    def __init__(self):
        self.username = self.get_username()
        self.user_hash = self.hash_username(self.username)
        self.path = self.get_settings_path()
        self.data = self.load_settings()
        self.config = "CONFIG"

    def update_name(self, mode):
        if mode:
            self.config = "HARD"
        else:
            self.config = "CONFIG"

    def set_version(self, version):
        self.data["V"] = version
        self.save_settings()

    def is_version(self, last_version):
        if "V" not in self.data:
            return False
        else:
            v1 = list(map(int, last_version.split('.')))
            v2 = list(map(int, self.data["V"].split('.')))
            return v1 <= v2

    def get_username(self):
        return os.path.basename(os.path.expanduser("~"))

    def hash_username(self, username):
        hash_obj = hashlib.sha256(username.encode("utf-8"))
        return str(int(hash_obj.hexdigest(), 16))[:6]

    def get_settings_path(self):
        filename = f"settings{self.user_hash}.json"
        return os.path.join(os.path.expanduser("~"), filename)

    def load_settings(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("Settings file is corrupted.")
                return {}
        return {}
    
    def get_team(self, key):
        teams = self.data.get("TEAMS", {})
        return teams.get(str(key), [])
    
    def get_aff(self):
        return self.data.get("AFFINITY", {})
    
    def get_config(self, key):
        config = self.data.get(self.config, {})
        return config.get(str(key), [])

    def save_settings(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=4)

    def save_team(self, key, value_list):
        if "TEAMS" not in self.data:
            self.data["TEAMS"] = {}

        self.data["TEAMS"][str(key)] = value_list
        self.save_settings()

    def save_aff(self, state):
        self.data["AFFINITY"] = state
        self.save_settings()

    def save_config(self, key, value_list, all=False):
        if all: configs = ["CONFIG", "HARD"]
        else: configs = [self.config]

        for config in configs:
            if config not in self.data:
                self.data[config] = {}
            self.data[config][str(key)] = value_list

        self.save_settings()

    def delete_config(self):
        if self.config in self.data:
            del self.data[self.config]
            self.save_settings()

    def config_exists(self, key):
        return str(key) in self.data.get(self.config, {})