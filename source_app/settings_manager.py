from source_app.utils import *
from source.utils.paths import PACKS, WORDLESS

class SettingsManager(QObject):
    import_error = pyqtSignal(str)

    def __init__(self, error_handler=None, hard=False):
        super().__init__()
        self.username = self.get_username()
        self.user_hash = self.hash_username(self.username)
        self.path = self.get_settings_path()
        if error_handler: self.import_error.connect(error_handler)
        self._hard = hard
        self.data = self.load_settings()

        self._thread = QThread()
        self._worker = SaveWorker(self.path)
        self._worker.moveToThread(self._thread)
        self._thread.start()

    @property
    def config(self):
        hard_value = self._hard() if callable(self._hard) else self._hard
        return "HARD" if hard_value else "CONFIG"

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
                    data = json.load(f)
                    data, corrpution = self.verify_file_data(data)
                    if corrpution:
                        self.import_error.emit(f"Some config data was outdated/corrupted. This might include: {', '.join(map(str, corrpution))}")
                    return data
            except json.JSONDecodeError:
                print("Settings file is corrupted.")
                self.import_error.emit("The config file is corrupted.\nAll settings have been reset to defaults.")
                return {}
        return {}
    
    def get_team(self, key):
        teams = self.data.get("TEAMS", {})
        return teams.get(str(key), [])
    
    def get_aff(self):
        return self.data.get("AFFINITY", {})
    
    def get_extra(self):
        return self.data.get("EXTRA", [])
    
    def get_config(self, key):
        config = self.data.get(self.config, {})
        return config.get(str(key), [] if key != 7 else {})

    def get_webhook(self):
        data = self.data.get("WEBHOOK", {})
        if not isinstance(data, dict):
            return {
                "enabled": False,
                "url": "",
                "thread_id": "",
                "compact_mode": False,
                "ping_on_finish": False,
                "ping_role_id": ""
            }

        enabled = data.get("enabled", False)
        url = data.get("url", "")
        thread_id = data.get("thread_id", "")
        compact_mode = data.get("compact_mode", False)
        ping_on_finish = data.get("ping_on_finish", False)
        ping_role_id = data.get("ping_role_id", "")

        if not isinstance(enabled, bool):
            enabled = False
        if not isinstance(url, str):
            url = ""
        if not isinstance(thread_id, str):
            thread_id = ""
        if not isinstance(compact_mode, bool):
            compact_mode = False
        if not isinstance(ping_on_finish, bool):
            ping_on_finish = False
        if not isinstance(ping_role_id, str):
            ping_role_id = ""

        return {
            "enabled": enabled,
            "url": url.strip(),
            "thread_id": thread_id.strip(),
            "compact_mode": compact_mode,
            "ping_on_finish": ping_on_finish,
            "ping_role_id": ping_role_id.strip()
        }

    def save_settings(self):
        self._worker.save_requested.emit(self.data)

    def set_team(self, key, value_list):
        if "TEAMS" not in self.data:
            self.data["TEAMS"] = {}
        self.data["TEAMS"][str(key)] = value_list

    def set_extra(self, state):
        self.data["EXTRA"] = state

    def set_aff(self, state):
        self.data["AFFINITY"] = state

    def set_config(self, key, value_list):
        name = self.config
        if name not in self.data:
            self.data[name] = {}
        self.data[name][str(key)] = value_list

    def set_webhook(self, value):
        if not isinstance(value, dict):
            value = {}

        enabled = value.get("enabled", False)
        url = value.get("url", "")
        thread_id = value.get("thread_id", "")
        compact_mode = value.get("compact_mode", False)
        ping_on_finish = value.get("ping_on_finish", False)
        ping_role_id = value.get("ping_role_id", "")

        if not isinstance(enabled, bool):
            enabled = False
        if not isinstance(url, str):
            url = ""
        if not isinstance(thread_id, str):
            thread_id = ""
        if not isinstance(compact_mode, bool):
            compact_mode = False
        if not isinstance(ping_on_finish, bool):
            ping_on_finish = False
        if not isinstance(ping_role_id, str):
            ping_role_id = ""

        self.data["WEBHOOK"] = {
            "enabled": enabled,
            "url": url.strip(),
            "thread_id": thread_id.strip(),
            "compact_mode": compact_mode,
            "ping_on_finish": ping_on_finish,
            "ping_role_id": ping_role_id.strip()
        }

    def delete_config(self):
        name = self.config
        if name in self.data:
            del self.data[name]

    def config_exists(self, key):
        return str(key) in self.data.get(self.config, {})
    
    def clean_entries(self, some_data, keys_allowed):
        current_keys = set(some_data.keys())

        invalid_keys = list(current_keys - keys_allowed)
        for key in invalid_keys: del some_data[key]
        return some_data
    
    def verify_file_data(self, data):
        corrupted_data = set()
        main_entries = {"CONFIG", "HARD", "TEAMS", "AFFINITY", "EXTRA", "WEBHOOK"}
        data = self.clean_entries(data, main_entries)

        configs = set(data.keys()) & {"CONFIG", "HARD"}

        def is_valid_config_floor_structure(value):
            if not (isinstance(value, list) and len(value) == 4): return False

            for i in (0, 1):
                if not isinstance(value[i], list): return False
                if not all(isinstance(item, str) for item in value[i]): return False

            if not isinstance(value[2], dict): return False
            if not isinstance(value[3], dict): return False
            return True
        
        def validate_config_floor(floor_value, config_name):
            index = 0 if config_name == "CONFIG" else 1
            list1, list2, dict1, dict2 = floor_value

            def valid_pack_in_lists(pack):
                if pack not in PACKS: return False
                allowed_floors = PACKS[pack][index]
                return bool(allowed_floors)

            list1 = [p for p in list1 if valid_pack_in_lists(p)]
            list2 = [p for p in list2 if valid_pack_in_lists(p)]

            list1 = list(set(list1))
            list2 = [p for p in list2 if p not in list1]

            def valid_dict_item(pack, value):
                if pack not in PACKS: return False

                allowed_floors = PACKS[pack][index]
                return value in allowed_floors

            dict1 = {
                pack: v
                for pack, v in dict1.items()
                if valid_dict_item(pack, v)
            }

            dict2 = {
                pack: v
                for pack, v in dict2.items()
                if valid_dict_item(pack, v)
            }

            for pack in list(dict2.keys()):
                if pack in dict1:
                    del dict2[pack]

            return [list1, list2, dict1, dict2]
        
        def is_valid_settings_structure(value):
            if not (isinstance(value, list) and len(value) == 17): return False

            for i in range(17):
                if i < 7 and not isinstance(value[i], bool):
                    return False
                elif not (isinstance(value[i], int) and 0 <= value[i] <= 3):
                    return False
            return True
        
        def is_valid_cards_structure(value):
            if not (isinstance(value, list) and len(value) == 5):
                return False
            if not (all(isinstance(x, int) for x in value) and set(value) == set(range(5))):
                return False
            return True

        for config in configs:
            if not isinstance(data[config], dict):
                corrupted_data.add("all config data")
                del data[config]
                continue

            # 7 team floors + keywodless gifts + grace/extra + reward cards
            config_entires = {f"{i}" for i in range(10)}
            data[config] = self.clean_entries(data[config], config_entires)

            for key in list(data[config].keys()):
                idx = int(key)
                if idx < 7:
                    if not is_valid_config_floor_structure(data[config][key]):
                        corrupted_data.add("priority floors")
                        del data[config][key]
                    else: data[config][key] = validate_config_floor(data[config][key], config)
                elif idx == 7:
                    if not isinstance(data[config][key], dict): 
                        corrupted_data.add("keywordless EGO selection")
                        del data[config][key]
                        continue
                    keywordless_entries = {f"{i}" for i in WORDLESS.keys()}
                    data[config][key] = self.clean_entries(data[config][key], keywordless_entries)
                    for id in list(data[config][key].keys()):
                        state = data[config][key][id]
                        max_state = WORDLESS[int(id)]["state"]
                        if not isinstance(state, int) or not (0 < state <= max_state):
                            corrupted_data.add("keywordless EGO selection")
                            del data[config][key][id]
                elif idx == 8:
                    if not is_valid_settings_structure(data[config][key]):
                        corrupted_data.add("grace selection, other settings")
                        del data[config][key]
                        continue
                elif idx == 9:
                    if not is_valid_cards_structure(data[config][key]):
                        corrupted_data.add("reward card priority")
                        del data[config][key]
                        continue
        
        if "TEAMS" not in data: pass
        elif not isinstance(data["TEAMS"], dict):
            corrupted_data.add("sinner selections")
            del data["TEAMS"]
        else: 
            valid_keys = {str(i) for i in range(17)}
            valid_values = set(range(12))
            for key in list(data["TEAMS"]):
                value = data["TEAMS"][key]
                if key not in valid_keys or not isinstance(value, list):
                    corrupted_data.add("sinner selections")
                    del data["TEAMS"][key]
                    continue
                
                value_filtered = [x for x in value if isinstance(x, int) and x in valid_values]
                if set(value_filtered) != set(value):
                    corrupted_data.add("sinner selections")
                    del data["TEAMS"][key]
                    continue
            if not data["TEAMS"]: del data["TEAMS"]

        def is_valid_affinity_structure(affinity_data):
            valid_keys = {str(i) for i in range(8)}
            if set(affinity_data) != valid_keys: return False
            
            for key in {str(i) for i in range(7)}:
                val = affinity_data[key]
                if not (isinstance(val, list) and len(val) == 2): return False
                boolean, lst = val
                if (not isinstance(boolean, bool) or
                    not (isinstance(lst, list) and all(isinstance(x, int) and 0 <= x <= 9 for x in lst)) or 
                    len(lst) != len(set(lst))):
                    return False
            
            val7 = affinity_data["7"]
            if not (isinstance(val7, int) and 0 <= val7 <= 6) or not affinity_data[str(val7)][0]:
                return False
            return True

        if "AFFINITY" not in data: pass 
        elif not isinstance(data["AFFINITY"], dict) or not is_valid_affinity_structure(data["AFFINITY"]):
            corrupted_data.add("team/affinity selection")
            del data["AFFINITY"]

        def is_valid_extra_structure(extra_data):
            if not (isinstance(extra_data, list) and len(extra_data) == 8):
                return False
            counts = extra_data[:3]
            if counts[0] == -1: counts[0] = 9999 # only needed for checks
            if not all(isinstance(x, int) and x in range(10000) for x in counts):
                return False
            settings = extra_data[3:]
            if not all(isinstance(x, bool) for x in settings): 
                return False
            if settings[1] and settings[4]: return False
            return True

        if "EXTRA" not in data: pass 
        elif not is_valid_extra_structure(data["EXTRA"]):
            corrupted_data.add("lux settings")
            del data["EXTRA"]

        def is_valid_webhook_structure(webhook_data):
            if not isinstance(webhook_data, dict):
                return False

            allowed_keys = {"enabled", "url", "thread_id", "compact_mode", "ping_on_finish", "ping_role_id"}
            webhook_data = self.clean_entries(webhook_data, allowed_keys)

            enabled = webhook_data.get("enabled", False)
            url = webhook_data.get("url", "")
            thread_id = webhook_data.get("thread_id", "")
            compact_mode = webhook_data.get("compact_mode", False)
            ping_on_finish = webhook_data.get("ping_on_finish", False)
            ping_role_id = webhook_data.get("ping_role_id", "")

            return (
                isinstance(enabled, bool) and
                isinstance(url, str) and
                isinstance(thread_id, str) and
                isinstance(compact_mode, bool) and
                isinstance(ping_on_finish, bool) and
                isinstance(ping_role_id, str)
            )

        if "WEBHOOK" not in data:
            pass
        elif not is_valid_webhook_structure(data["WEBHOOK"]):
            corrupted_data.add("discord webhook settings")
            del data["WEBHOOK"]
        else:
            # keep only known keys and normalize trivial whitespace
            data["WEBHOOK"] = self.clean_entries(
                data["WEBHOOK"],
                {"enabled", "url", "thread_id", "compact_mode", "ping_on_finish", "ping_role_id"}
            )
            data["WEBHOOK"]["url"] = data["WEBHOOK"].get("url", "").strip()
            data["WEBHOOK"]["thread_id"] = data["WEBHOOK"].get("thread_id", "").strip()
            data["WEBHOOK"]["enabled"] = data["WEBHOOK"].get("enabled", False)
            data["WEBHOOK"]["compact_mode"] = data["WEBHOOK"].get("compact_mode", False)
            data["WEBHOOK"]["ping_on_finish"] = data["WEBHOOK"].get("ping_on_finish", False)
            data["WEBHOOK"]["ping_role_id"] = data["WEBHOOK"].get("ping_role_id", "").strip()

        return data, corrupted_data
    

class SaveWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    save_requested = pyqtSignal(dict)

    def __init__(self, path):
        super().__init__()
        self.path = path
        self._queue = []

        self.save_requested.connect(self._on_save_requested)

    def _on_save_requested(self, data):
        self._queue.append(copy.deepcopy(data))
        if len(self._queue) == 1:
            self._process_next()

    def _process_next(self):
        if not self._queue:
            return
        data = self._queue[0]
        try:
            with open(self.path, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self._queue.pop(0)
            if self._queue:
                QTimer.singleShot(0, self._process_next)
            else:
                self.finished.emit()
