from source_app.utils import *
from source_app.settings_manager import SettingsManager
from source_app.widget import SelectizeWidget
from source_app.button import CustomButton
from source_app.run import VersionChecker, BotWorker

sm = SettingsManager()


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        # params
        self.count = 0
        self.team = 0
        self.sinners = []
        self.hard = False

        self.is_lux = False
        self.count_exp = 1
        self.count_thd = 3

        self.sinner_selections = {i: sm.get_team(i) for i in range(17)}
        self.selected_affinity = {i: [i] for i in range(7)}
        self.team_lux = self._day()
        self.team_lux_buttons = [self.team_lux, 3 + self._day(sin=True)]
        self.keywordless = {}

        self._init_ui()
        self._create_buttons()
    
    #     self.debug_timer = QTimer()
    #     self.debug_timer.timeout.connect(self.print_state)
    #     self.debug_timer.start(2000)  # 2000 ms = 2 sec

    # def print_state(self):
    #     print(f"Current state - Affinity: {self.team}, Priority: {self.priority}")

    def _init_ui(self):
        """Initialize main window settings"""
        self.setWindowTitle(f"ChargeGrinder v{p.V}")
        self.setWindowIcon(QIcon(Bot.ICON))
        self.setFixedSize(700, 785)
        self.background = QPixmap(Bot.APP_PTH["UI"])
        
        self.inputField = QLineEdit(self)
        font_id = QFontDatabase.addApplicationFont(Bot.APP_PTH["ExcelsiorSans"])
        if font_id != -1: self.family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.inputField.setFont(QFont(self.family, 30))
        self.inputField.setGeometry(108, 100, 90, 50)
        self.inputField.setValidator(QIntValidator(0, 1000))
        self.inputField.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.inputField.setStyleSheet('color: #EDD1AC; background: transparent; border: none;')
        self.inputField.setText("1")

        self.overlay = QLabel(self)
        overlay_pixmap = QPixmap(Bot.APP_PTH['frames'])
        self.overlay.setPixmap(overlay_pixmap)
        self.overlay.setGeometry(48, 444, 601, 296)
        self.overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.guide = QLabel(self)
        self.guide.setPixmap(QPixmap(Bot.APP_PTH['guide']))
        self.guide.setGeometry(0, 0, 700, 785)
        self.guide.hide()
        self.guide_close_btn = QPushButton(self.guide)
        self.guide_close_btn.setGeometry(214, 662, 241, 74)
        self.guide_close_btn.clicked.connect(self.guide.hide)
        self.guide_close_btn.setStyleSheet('background: transparent; border: none;')

        self.progress = QLabel(self)
        self.progress.setPixmap(QPixmap(Bot.APP_PTH['progress']))
        self.progress.setGeometry(0, 0, 700, 785)
        self.progress.hide()

        self.run = QLabel(self.progress)
        self.run.setPixmap(QPixmap(Bot.APP_PTH['run']))
        self.run.hide()

        self.rerun = QLabel(self.progress)
        self.rerun.setPixmap(QPixmap(Bot.APP_PTH['rerun']))
        self.rerun.hide()

        self.pause = QLabel(self.progress)
        self.pause.setPixmap(QPixmap(Bot.APP_PTH['pause']))
        self.pause.hide()
        self.stop = QPushButton(self.pause)
        self.stop.setGeometry(358, 382, 73, 69)
        self.stop.clicked.connect(self.stop_execution)
        self.stop.setStyleSheet('background: transparent; border: none;')
        self.play = QPushButton(self.pause)
        self.play.setGeometry(268, 382, 73, 69)
        self.play.clicked.connect(self.proceed)
        self.play.setStyleSheet('background: transparent; border: none;')

        self.warn = QLabel(self.progress)
        self.warn.setPixmap(QPixmap(Bot.APP_PTH['warning']))
        self.warn.hide()

        self.warn_txt = QLabel(self.warn)
        self.warn_txt.setFont(QFont(self.family, 25))
        self.warn_txt.setGeometry(80, 630, 540, 100)
        self.warn_txt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.warn_txt.setStyleSheet('color: #FF8080; background: transparent; border: none;')

        self.selected_button_order = []
        self.selected_card_order = []
        self.config_widgets = []

        self.config = QLabel(self)
        self.config.setPixmap(QPixmap(Bot.APP_PTH["config"]))
        self.config.setGeometry(0, 92, 700, 693)
        self.config.hide()

        self.priority_team = QLabel(self.config)
        self.priority_team.setPixmap(QPixmap(Bot.APP_PTH[f'team{self.selected_affinity[self.team][0]}']))
        self.priority_team.setGeometry(38, 121, 301, 247)
        self.priority_team.show()

        self.combo_boxes = []
        self.selectize_widgets = []

        self.hard_conf = QLabel(self.config)
        self.hard_conf.setPixmap(QPixmap(Bot.APP_PTH["OffHard"]))
        self.hard_conf.setGeometry(43, 565, 43, 31)
        self.hard_conf.hide()
        self.hard_conf2 = QLabel(self.config)
        self.hard_conf2.setPixmap(QPixmap(Bot.APP_PTH["hard_conf2"]))
        self.hard_conf2.setGeometry(87, 31, 149, 27)
        self.hard_conf2.hide()
        self.hard_conf3 = QLabel(self.config)
        self.hard_conf3.setPixmap(QPixmap(Bot.APP_PTH["infinity"]))
        self.hard_conf3.setGeometry(366, 623, 128, 26)
        self.hard_conf3.hide()

        self.ego_panel = QLabel(self.config)
        self.ego_panel.setPixmap(QPixmap(Bot.APP_PTH["config_panel"]))
        self.ego_panel.setGeometry(0, 87, 700, 605)
        self.ego_panel.hide()

        self.lux = QLabel(self)
        self.lux.setPixmap(QPixmap(Bot.APP_PTH["Lux"]))
        self.lux.setGeometry(0, 92, 700, 295)
        self.lux.hide()

        self.exp = QLineEdit(self.lux)
        self.exp.setFont(QFont(self.family, 30))
        self.exp.setGeometry(108, 8, 90, 50)
        self.exp.setValidator(QIntValidator(0, 1000))
        self.exp.setText(str(self.count_exp))
        self.exp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.exp.setStyleSheet('color: #EDD1AC; background: transparent; border: none;')

        self.thd = QLineEdit(self.lux)
        self.thd.setFont(QFont(self.family, 30))
        self.thd.setGeometry(108, 78, 90, 50)
        self.thd.setValidator(QIntValidator(0, 1000))
        self.thd.setText(str(self.count_thd))
        self.thd.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thd.setStyleSheet('color: #EDD1AC; background: transparent; border: none;')

        # self.test = QPushButton(self)
        # self.test.setText("Test")
        # self.test.setGeometry(228, 514, 169, 26)
        # self.test.show()

    def set_priority(self, team=None):
        if team is None:
            team = self.team

        self.priority, self.avoid = self.get_packs(team)
        self.all = self.get_all()
    
    def get_packs(self, team):
        if sm.config_exists(team):
            data = sm.get_config(team)
            if len(data) == 2 and all(isinstance(x, list) for x in data):
                priority = data[0]
                avoid = data[1]
            else: # old format
                priority = data
                if sm.config_exists(7):
                    avoid = sm.get_config(7)
                else:
                    avoid = self.get_avoid()
        else: 
            priority = self.get_priority(team)
            avoid = self.get_avoid()
        return priority, avoid

    def set_widgets(self):
        for widget in self.config_widgets:
            widget.deleteLater()
        self.config_widgets.clear()
        self.combo_boxes.clear()
        self.selectize_widgets.clear()
        items_to_remove = set(self.priority) | set(self.avoid)
        self.available_items = [item for item in self.all if item not in items_to_remove]
        self.all = self.available_items.copy()
        for i in range(2):
            combo = QComboBox()
            combo.addItems(self.available_items)
            combo.setFont(QFont(self.family, 18))
            combo.setStyleSheet('color: #EDD1AC;')
            combo.setFixedSize(185, 32)

            btn_add = QPushButton("Add")
            btn_add.setFont(QFont(self.family, 20))
            btn_add.setStyleSheet('color: #EDD1AC;')
            btn_add.setFixedSize(52, 32)  # narrower than combo

            selectize = SelectizeWidget(font=QFont(self.family, 15))
            selectize.itemAdded.connect(self.handle_item_added)
            selectize.itemRemoved.connect(self.handle_item_removed)

            if i == 0:
                for item in self.priority:
                    selectize.add_item(item)
            else:
                for item in self.avoid:
                    selectize.add_item(item)

            def make_handler(selectize_widget, combo_box, index):
                def handler():
                    text = combo_box.currentText()
                    # Prevent adding empty items
                    if not text or text not in self.available_items:
                        return
                    selectize_widget.add_item(text)
                    if index == 0:
                        self.priority = selectize_widget.getItems()
                    else:
                        self.avoid = selectize_widget.getItems()
                return handler

            btn_add.clicked.connect(make_handler(selectize, combo, i))

            # Parent widget
            widget = QWidget(self.config)
            widget.setStyleSheet("background: transparent;")
            widget.setGeometry(46 + i * 323, 172, 287, 187)

            # Layout setup
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)

            top_row = QWidget()
            top_row.setFixedSize(263, 32)
            top_layout = QHBoxLayout(top_row)
            top_layout.setContentsMargins(0, 0, 0, 0)
            top_layout.setSpacing(26)  # space between combo and button
            top_layout.addWidget(combo)
            top_layout.addWidget(btn_add)
            top_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            layout.addWidget(top_row, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
            layout.addWidget(selectize)

            widget.show()

            self.combo_boxes.append(combo)
            self.selectize_widgets.append(selectize)
            self.config_widgets.append(widget)

    def handle_item_added(self, item):
        if item in self.available_items:
            self.available_items.remove(item)
        
        if item in self.priority:
            self.avoid = [i for i in self.avoid if i != item]
        if item in self.avoid:
            self.priority = [i for i in self.priority if i != item]
        
        for combo in self.combo_boxes:
            current_text = combo.currentText()
            combo.clear()
            combo.addItems(self.available_items)
            if current_text in self.available_items:
                combo.setCurrentText(current_text)

    def handle_item_removed(self, item):
        # Remove from both lists (if present)
        if item in self.priority:
            self.priority.remove(item)  # ACTUALLY remove from priority
        if item in self.avoid:
            self.avoid.remove(item)  # ACTUALLY remove from avoid
        
        if item not in self.available_items:
            orig_index = next((i for i, x in enumerate(self.all) if x == item), -1)
            if orig_index >= 0:
                self.available_items.insert(orig_index, item)
            else:
                self.available_items.append(item)
        
        for combo in self.combo_boxes:
            current_text = combo.currentText()
            combo.clear()
            combo.addItems(self.available_items)
            if current_text in self.available_items:
                combo.setCurrentText(current_text)
    
    def reset_to_defaults(self, team, default=True):
        # Reset the data lists to defaults
        if default:
            self.priority = self.get_priority(team)
            self.avoid = self.get_avoid()
            self.set_card_buttons([])
            self.activate_ego_gifts({})
            buff = [True, True, True, True]
            if self.hard:
                on = [False, True, False, False, False, False, False]
                self.set_buttons_active(on + buff)
            else:
                on = [False, True, False, False, True, False, False]
                self.set_buttons_active(on + buff)
            sm.delete_config()
        else:
            self.set_priority(team)
        
        # Clear all selectize widgets
        for widget in self.selectize_widgets:
            while widget.scroll_layout.count():
                child = widget.scroll_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            widget.items = []
        
        # Rebuild the available items list
        items_to_remove = set(self.priority) | set(self.avoid)
        self.available_items = [item for item in self.all if item not in items_to_remove]
        
        # Reinitialize the widgets with default values
        for i, widget in enumerate(self.selectize_widgets):
            items_to_add = self.priority if i == 0 else self.avoid
            for item in items_to_add:
                widget.add_item(item)
        
        # Update all combo boxes
        for combo in self.combo_boxes:
            current_text = combo.currentText()
            combo.clear()
            combo.addItems(self.available_items)
            if current_text in self.available_items:
                combo.setCurrentText(current_text)

    def _day(self, sin=False):
        # perfect timezone that refreshes dailies at 12 AM
        gmt_plus_3 = timezone(timedelta(hours=3))
        now_gmt3 = datetime.now(gmt_plus_3)
        day_number = now_gmt3.weekday()
        if sin:
            return (day_number + 1) % 7
        else:
            return (day_number > 1) + (day_number > 3) - (day_number == 6)
    
    def get_priority(self, team):
        affinity = self.selected_affinity[team][0]
        if self.hard:
            team_data = Bot.TEAMS[list(Bot.TEAMS.keys())[affinity]]
        else:
            team_data = Bot.HARD[list(Bot.HARD.keys())[affinity]]
        return team_data.get(f"floors", [])
    
    def get_all(self):
        if self.hard:
            return Bot.HARD_UNIQUE
        else:
            return Bot.FLOORS_UNIQUE

    def get_avoid(self):
        if self.hard:
            return Bot.HARD_BANNED
        else:
            return Bot.BANNED

    def _get_button_lux(self):
        return [
            (f'team_lux{i}', {
                'geometry': (30 + 63*i + i//2, 221, 64, 68),
                'checkable': True,
                'checked': i == self._day(),
                'click_handler': self.activate_lux_teams,
                'icon': Bot.APP_PTH['affinity']
            }) for i in range(3)
        ] + [
            (f'team_lux{i + 3}', {
                'geometry': (30 + 63*(i + 3) + (i + 3)//2, 221, 64, 68),
                'checkable': True,
                'checked': i == self._day(sin=True),
                'click_handler': self.activate_lux_teams,
                'icon': Bot.APP_PTH['affinity_support']
            }) for i in range(7)
        ]
    
    def _get_button_keyword(self):
        return [
            (f'keyword{i}', {
                'geometry': (30 + 63*i + i//2 + 191 - (i > 6)*(191 + 444), 313, 64, 68),
                'checkable': True,
                'checked': i == 0,
                'id': i,
                'click_handler': self.activate_keyword_button,
                'icon': Bot.APP_PTH['affinity'],
            }) for i in range(10)
        ]
    
    def _get_keyword_icon(self):
        return [
            (f'icon{i}', {
                'geometry': (221 + 63*i + (i)//2 - i//4, 242, 64, 68),
                'id': i,
                'icon': Bot.APP_PTH[f't{i}'],
            }) for i in range(7)
        ]

    def _get_button_affinity(self):
        return [
            (f'team{i}', {
                'geometry': (220 + 63*i + (i + 1)//2, 241, 64, 68),
                'checkable': True,
                'checked': i == 0,
                'click_handler': self.activate_permanent_button,
                'icon': Bot.APP_PTH['affinity'],
            }) for i in range(7)
        ]
    
    def _get_button_on(self):
        return [
            (f'on{i}', {
                'geometry': (30 + 162*i - (162*4 - 2)*(i > 3) - i//2, 557 + 55*(i > 3), 154, 49),
                'checkable': True,
                'checked': i == 1 or i == 4,
                'click_handler': self.update_button_icons,
                'icon': Bot.APP_PTH[f'sel{"1"*(i == 0)}_extra'],
                'glow': Bot.APP_PTH['sel_extra'],
            }) for i in range(7)
        ] + [
            (f'on{i+7}', {
                'geometry': (223 + 148*i, 155, 144, 56),
                'checkable': True,
                'checked': i % 2 == 0,
                'click_handler': self.update_button_icons,
                'icon': Bot.APP_PTH['sel_lux']
            }) for i in range(3)
        ]
    
    def _get_buff(self):
        return [
            (f'buff{i}', {
                'geometry': (35 + 65*i, 416, 64, 68),
                'checkable': True,
                'checked': True,
                'click_handler': self.update_button_icons,
                'icon': Bot.APP_PTH['affinity_support']
            }) for i in range(4)
        ]
    
    def _get_button_selected(self):
        return [
            (f'sel{i+1}', {
                'geometry': (51 + 99*(i - 6*(i > 5)), 443 + 149*(i > 5), 103, 147),
                'checkable': True,
                'checked': False,
                'id': i,
                'click_handler': self.update_selected_buttons,
            }) for i in range(12)
        ]
    
    def _get_card_order(self):
        return [
            (f'card{i+1}', {
                'geometry': (343 + 65*i - (i > 1), 416, 64, 68),
                'checkable': True,
                'checked': False,
                'id': i,
                'click_handler': self.update_card_buttons,
            }) for i in range(5)
        ]
    
    def _get_ego_buttons(self):
        return [
            (f'ego{i}', {
                'geometry': (41 + 105*i - (105*6)*(i//6), 99 + 103*(i//6), 88, 87),
                'checkable': True,
                'checked': False,
                'id': i,
                'state': 0,
                'click_handler': self.update_ego_icons,
                'icon': Bot.APP_PTH['select_gift1']
            }) for i in range(23)
        ]

    def _create_buttons(self):
        """Create and configure all buttons using the CustomButton class"""
        self.buttons = {
            'update': CustomButton(self, {
                'geometry': (202, 24, 298, 53),
                'click_handler': lambda: webbrowser.open('https://github.com/AlexWalp/Mirror-Dungeon-Bot/releases/latest'),
                'checkable': True,
                'checked': True,
                'icon': Bot.APP_PTH['update'],
                'glow': Bot.APP_PTH['glow_update'],
                'filter': False
            }),

            'lux': CustomButton(self, {
                'geometry': (475, 95, 196, 57),
                'click_handler': self.set_lux,
                'glow': Bot.APP_PTH['luxbtn']
            }),

            'save': CustomButton(self, {
                'geometry': (90, 394, 125, 43),
                'click_handler': self.save,
                'glow': Bot.APP_PTH['save']
            }),

            'reset': CustomButton(self, {
                'geometry': (481, 394, 125, 43),
                'click_handler': self.reset,
                'glow': Bot.APP_PTH['clear']
            }),

            'MD': CustomButton(self.lux, {
                'geometry': (475, 3, 196, 57),
                'click_handler': self.lux_hide,
                'glow': Bot.APP_PTH['md']
            }),

            'config': CustomButton(self, {
                'geometry': (209, 164, 217, 55),
                'click_handler': lambda: (self.config.show(), self.config.raise_()),
                'glow': Bot.APP_PTH['settings']
            }),

            'save_config': CustomButton(self.config, {
                'geometry': (265, 13, 254, 63),
                'click_handler': self.save_config,
                'glow': Bot.APP_PTH['saveconf']
            }),

            'del_config': CustomButton(self.config, {
                'geometry': (530, 13, 150, 63),
                'click_handler': lambda: self.reset_to_defaults(self.team),
                'glow': Bot.APP_PTH['del']
            }),

            'ego_panel_open': CustomButton(self.config, {
                'geometry': (515, 611, 154, 49),
                'click_handler': self.toggle_ego_panel,
                'glow': Bot.APP_PTH['sel_extra']
            }),

            'ego_panel_close': CustomButton(self.ego_panel, {
                'geometry': (515, 524, 154, 49),
                'click_handler': self.toggle_ego_panel,
                'glow': Bot.APP_PTH['sel_extra']
            }),

            'hard': CustomButton(self, {
                'geometry': (24, 166, 178, 58),
                'checkable': True,
                'checked': False,
                'click_handler': self.set_hardmode,
                'icon': Bot.APP_PTH['hard']
            }),

            'log': CustomButton(self, {
                'geometry': (564, 29, 41, 40),
                'checkable': True,
                'checked': True,
                'click_handler': self.update_button_icons,
                'icon': Bot.APP_PTH['log_on']
            }),
            'csv': CustomButton(self, {
                'geometry': (523, 35, 41, 28),
                'click_handler': self.ask_csv,
                'glow': Bot.APP_PTH['csv']
            }),

            'guide_icon': CustomButton(self, {
                'geometry': (45, 25, 135, 49),
                'click_handler': self.show_guide,
                'glow': Bot.APP_PTH['guide_icon'],
            }),

            'start': CustomButton(self, {
                'geometry': (453, 165, 216, 65),
                'click_handler': self.start,
                'glow': Bot.APP_PTH['start'],
            }),

            'githubButton': CustomButton(self, {
                'geometry': (615, 33, 35, 35),
                'glow': Bot.APP_PTH['me'],
                'glow_geometry': (610, 26, 47, 47),
                'click_handler': lambda: webbrowser.open('https://github.com/AlexWalp/Mirror-Dungeon-Bot')
            })
        }
        all_buttons = self._get_keyword_icon() + self._get_button_affinity() + self._get_button_selected() + self._get_button_keyword()
        for name, settings in all_buttons:
            self.buttons[name] = CustomButton(self, settings)

        for name, settings in self._get_button_on()[:7] + self._get_card_order() + self._get_buff():
            self.buttons[name] = CustomButton(self.config, settings)
        for name, settings in self._get_button_on()[7:]:
            self.buttons[name] = CustomButton(self.lux, settings)

        for name, settings in self._get_button_lux():
            self.buttons[name] = CustomButton(self.lux, settings)

        for name, settings in self._get_ego_buttons():
            self.buttons[name] = CustomButton(self.ego_panel, settings)

        self.buttons['update'].hide()
        self.check_version()

        self.set_team()
        self.priority_team.setPixmap(QPixmap(Bot.APP_PTH[f'team{self.selected_affinity[self.team][0]}']))
        self.set_priority()

        self.set_widgets()
        self.set_selected_buttons(self.sinner_selections[self.team])
        self.set_affinity_buttons(self.selected_affinity[self.team])
        self.activate_ego_gifts(sm.get_config(7))
        self.set_buttons_active(sm.get_config(8))
        self.set_card_buttons(sm.get_config(9))
        self.overlay.raise_()

    def set_team(self):
        # first 7 values - whether button is activated, last - team index
        state = sm.get_aff()
        if state:
            self.team = state["7"]
            for i in range(7):
                data = state[str(i)]
                if isinstance(data, list) and len(data) == 2:
                    self.selected_affinity[i] = data[1]
                    self.buttons[f"icon{i}"].setIcon(QIcon(Bot.APP_PTH[f"t{self.selected_affinity[i][0]}"]))
                    is_selected = data[0]
                else: # old version
                    is_selected = data
                if is_selected:
                    self.buttons[f"team{i}"].setChecked(True)
                    if i == self.team:
                        self.buttons[f"team{i}"].setIcon(QIcon(Bot.APP_PTH["affinity"]))
                    else:
                        self.buttons[f"team{i}"].setIcon(QIcon(Bot.APP_PTH["affinity_support"]))
                else:
                    self.buttons[f"team{i}"].setChecked(False)
                    self.buttons[f"team{i}"].setIcon(QIcon())
    
    def save_affinity(self):
        state = dict()
        for i in range(7):
            state[str(i)] = (self.buttons[f"team{i}"].isChecked(), self.selected_affinity[i])
        state[str(7)] = self.team
        sm.save_aff(state)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.background)

    def set_hardmode(self):
        self.update_button_icons()

        self.hard = self.buttons['hard'].isChecked()
        sm.update_name(self.hard)
        self.set_priority()
        self.set_widgets()
        buff = [True, True, True, True]
        if self.hard:
            on = [False, True, False, False, False, False, False]
            self.set_buttons_active(on + buff)
            self.buttons['on0'].config['icon'] = Bot.APP_PTH['sel1_hard']
            self.hard_conf.show()
            self.hard_conf2.show()
            self.hard_conf3.show()
        else:
            on = [False, True, False, False, True, False, False]
            self.set_buttons_active(on + buff)
            self.buttons['on0'].config['icon'] = Bot.APP_PTH['sel1_extra']
            self.hard_conf.hide()
            self.hard_conf2.hide()
            self.hard_conf3.hide()
        self.activate_ego_gifts(sm.get_config(7))
        self.set_buttons_active(sm.get_config(8))
        self.set_card_buttons(sm.get_config(9))

    def set_lux(self):
        self.lux.show()
        self.lux.raise_()
        self.is_lux = True
        self.buttons['start'].raise_()
        self.update_sinners()
        self.sinner_selections[self.team] = self.sinners
        self.set_selected_buttons(self.sinner_selections[self.team_lux + 7])

    def lux_hide(self):
        self.is_lux = False
        self.update_sinners() 
        self.sinner_selections[self.team_lux + 7] = self.sinners
        self.set_selected_buttons(self.sinner_selections[self.team])
        self.lux.hide()

    def toggle_ego_panel(self):
        if self.ego_panel.isVisible():
            self.ego_panel.hide()
        else:
            self.ego_panel.raise_()
            self.ego_panel.show()

    def save(self):
        if self.is_lux:
            team = self.team_lux + 7
        else:
            team = self.team
        self.update_sinners()
        sm.save_team(team, self.sinners)
    
    def reset(self):
        self.selected_button_order.clear()
        for key, button in self.buttons.items():
            if key.startswith("sel"):
                button.setChecked(False)
                button.setIcon(QIcon())

        if self.is_lux:
            self.sinner_selections[self.team_lux + 7]
        else:
            self.sinner_selections[self.team]

    def save_config(self):
        if len(self.selected_card_order) < 5:
            frame = (10, 10, 43, 41)
            errors = list(filter(lambda i: not self.buttons[f'card{i}'].isChecked(), [i for i in range(1, 6)]))
            for i in errors:
                self.buttons[f'card{i}'].set_glow_image(Bot.APP_PTH["warn_support"], frame)
            CustomButton.glow_multiple([self.buttons[f'card{i}'] for i in errors])
            return
        
        sm.save_config(self.team, (self.priority, self.avoid))
        sm.save_config(7, {str(id): state for id, state in self.keywordless.items()})
        sm.save_config(8, self.get_config_buttons())
        sm.save_config(9, self.get_cards())
        self.ego_panel.hide()
        self.config.hide()

    def update_sinners(self):
        self.sinners = [button.config.get('id') for button in self.selected_button_order]

    def get_cards(self):
        return [button.config.get('id') for button in self.selected_card_order]

    def get_config_buttons(self):
        activated = []
        for i in range(7):
            activated.append(self.buttons[f'on{i}'].isChecked())
        for i in range(4):
            activated.append(self.buttons[f'buff{i}'].isChecked())
        return activated
    
    def ask_csv(self):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.NoIcon)
        msg.setWindowTitle("Get run stats")
        msg.setText("Do you want to export your run data from game.log to game.csv?")
        
        msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | 
            QMessageBox.StandardButton.No
        )
        
        response = msg.exec()
        
        if response == QMessageBox.StandardButton.Yes:
            self.get_csv()
    
    def get_csv(self):
        try:
            log_to_csv()
        except FileNotFoundError:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Error")
            msg.setText("File game.log is not found")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()

    
    def set_buttons_active(self, states):
        on_buttons = [self.buttons[f'on{i}'] for i in range(7)]
        buff_buttons = [self.buttons[f'buff{i}'] for i in range(4)]
        
        if len(states) == 5: # old version
            states += [False]*2 + [True]*4
        elif len(states) == 9: # less old version
            states = states[:5] + [False]*2 + states[-4:]
        elif len(states) != 11: # not default
            return

        buttons = on_buttons + buff_buttons

        for button, state in zip(buttons, states):
            button.setChecked(state)
            if state:
                icon_path = getattr(button, 'config', {}).get('icon', '')
                if icon_path:
                    button.setIcon(QIcon(icon_path))
            else:
                button.setIcon(QIcon())
            button.setIconSize(button.size())


    def activate_ego_gifts(self, data):
        if isinstance(data, list): # old format
            data = {}
        self.keywordless = {}
        print(data)
        for id in range(23):
            if str(id) in data.keys():
                state = data[str(id)]
                self.buttons[f'ego{id}'].config["state"] = state
                self.buttons[f'ego{id}'].setChecked(True)
                self.buttons[f'ego{id}'].setIcon(QIcon(Bot.APP_PTH[f'select_gift{state}']))
                self.keywordless[id] = state
            else:
                if self.buttons[f'ego{id}'].isChecked():
                    self.buttons[f'ego{id}'].config["state"] = 0
                    self.buttons[f'ego{id}'].setChecked(False)
                    self.buttons[f'ego{id}'].setIcon(QIcon())

    def activate_lux_teams(self):
        sender = self.sender()
        if not sender or not isinstance(sender, QPushButton):
            return
        
        id = None
        for i in range(10):
            if self.buttons[f"team_lux{i}"] == sender:
                id = i
                break
        else: return
        button_group = int(id > 2) # 0 for damage, 1 for sin
        ranges = [range(3), range(3, 10)]

        # print('before')
        # print(self.team_lux)
        # print(self.team_lux_buttons)
        # print([self.buttons[f"team_lux{i}"].isChecked() for i in range(10)])
        self.update_sinners()
        self.sinner_selections[self.team_lux + 7] = self.sinners
        if id == self.team_lux: # same item is clicked
            if all(item is not None for item in self.team_lux_buttons):
                self.buttons[f"team_lux{id}"].setIcon(QIcon())
                self.team_lux_buttons[button_group] = None

                self.team_lux = self.team_lux_buttons[1 - button_group]
                self.buttons[f"team_lux{self.team_lux}"].setIcon(QIcon(Bot.APP_PTH['affinity']))
            else:
                self.buttons[f"team_lux{id}"].setChecked(True)
        elif self.team_lux not in ranges[button_group]: # different group is clicked
            self.buttons[f"team_lux{self.team_lux}"].setIcon(QIcon(Bot.APP_PTH['affinity_support']))
            self.team_lux = id
            self.buttons[f"team_lux{id}"].setIcon(QIcon(Bot.APP_PTH['affinity']))
            if self.team_lux_buttons[button_group] is not None:
                if self.team_lux_buttons[button_group] == id:
                    self.buttons[f"team_lux{id}"].setChecked(True)
                else:
                    self.buttons[f"team_lux{self.team_lux_buttons[button_group]}"].setIcon(QIcon())
                    self.buttons[f"team_lux{self.team_lux_buttons[button_group]}"].setChecked(False)
            self.team_lux_buttons[button_group] = id
        else: # same group is clicked but different item
            self.buttons[f"team_lux{self.team_lux}"].setIcon(QIcon())
            self.buttons[f"team_lux{self.team_lux}"].setChecked(False)

            self.team_lux = id
            self.team_lux_buttons[button_group] = id
            self.buttons[f"team_lux{id}"].setIcon(QIcon(Bot.APP_PTH['affinity']))
        # print("after")
        # print(self.team_lux)
        # print(self.team_lux_buttons)
        # print([self.buttons[f"team_lux{i}"].isChecked() for i in range(10)])
        self.set_selected_buttons(self.sinner_selections[self.team_lux + 7])

    def activate_permanent_button(self):
        sender = self.sender()
        if not sender or not isinstance(sender, QPushButton):
            return

        self.update_sinners()
        self.sinner_selections[self.team] = self.sinners
        null_visual_state = sender.icon().isNull()

        if null_visual_state:
            sender.setIcon(QIcon(Bot.APP_PTH['affinity']))
            self.buttons[f"team{self.team}"].setIcon(QIcon(Bot.APP_PTH['affinity_support']))
            for i in range(7):
                if self.buttons[f"team{i}"] == sender:
                    self.team = i
                    break
        else:
            if sender != self.buttons[f"team{self.team}"]:
                sender.setIcon(QIcon())
            else:
                sender.setChecked(True)

        self.priority_team.setPixmap(QPixmap(Bot.APP_PTH[f'team{self.selected_affinity[self.team][0]}']))
        self.reset_to_defaults(self.team, default=False)
        self.set_selected_buttons(self.sinner_selections[self.team])
        self.set_affinity_buttons(self.selected_affinity[self.team])
    
    def activate_keyword_button(self):
        sender = self.sender()
        if not sender or not isinstance(sender, QPushButton):
            return

        button_key = next((k for k, v in self.buttons.items() if v == sender), None)
        if not button_key:
            return
        
        selected_affinity_buttons = [self.buttons[f'keyword{id}'] for id in self.selected_affinity[self.team]]

        main = selected_affinity_buttons[0]
        change_icon = False

        if sender.isChecked():
            if sender not in selected_affinity_buttons:
                selected_affinity_buttons.append(sender)
        else:
            if sender in selected_affinity_buttons and len(selected_affinity_buttons) > 1:
                selected_affinity_buttons.remove(sender)
                if sender is main:
                    change_icon = True

        if change_icon:
            self.change_icon(selected_affinity_buttons[0].config.get('id'))

        for index, button in enumerate(selected_affinity_buttons):
            if index == 0:
                icon_path = Bot.APP_PTH[f'affinity']
            else:
                icon_path = Bot.APP_PTH[f'aff{index}']
            button.setIcon(QIcon(icon_path))
            button.setIconSize(button.size())

        for key, button in self.buttons.items():
            if key.startswith("keyword") and button not in selected_affinity_buttons:
                button.setIcon(QIcon())

        self.selected_affinity[self.team] = [button.config.get('id') for button in selected_affinity_buttons]

    def change_icon(self, id):
        self.buttons[f'icon{self.team}'].setIcon(QIcon(Bot.APP_PTH[f"t{id}"]))
        self.priority_team.setPixmap(QPixmap(Bot.APP_PTH[f'team{id}']))

    def update_button_icons(self):
        sender = self.sender()
        if not sender or not isinstance(sender, QPushButton):
            return
        
        if sender.isChecked():
            icon_path = getattr(sender, 'config', {}).get('icon', '')
            if icon_path:
                sender.setIcon(QIcon(icon_path))
        else:
            sender.setIcon(QIcon())
        sender.setIconSize(sender.size())

    def update_ego_icons(self):
        sender = self.sender()
        if not sender or not isinstance(sender, QPushButton):
            return
        
        id = getattr(sender, 'config', {}).get('id', None)
        state = getattr(sender, 'config', {}).get('state', None)
        if id is None or state is None: 
            return
        
        states = [j for j in range(Bot.WORDLESS[id]['state'] + 1)]
        i = states.index(state)
        next_state = states[(i + 1) % len(states)]

        if next_state == 0:
            self.keywordless.pop(id, None)
            sender.setIcon(QIcon())
        else:
            self.keywordless[id] = next_state
            sender.setIcon(QIcon(Bot.APP_PTH[f'select_gift{next_state}']))
            if next_state != 1:
                sender.setChecked(True)
        sender.config["state"] = next_state

    def update_card_buttons(self):
        sender = self.sender()
        if not sender or not isinstance(sender, QPushButton):
            return

        button_key = next((k for k, v in self.buttons.items() if v == sender), None)
        if not button_key:
            return

        if sender.isChecked():
            if sender not in self.selected_card_order:
                self.selected_card_order.append(sender)
        else:
            if sender in self.selected_card_order:
                self.selected_card_order.remove(sender)

        for index, button in enumerate(self.selected_card_order):
            icon_path = Bot.APP_PTH[f'aff{index + 1}']
            button.setIcon(QIcon(icon_path))
            button.setIconSize(button.size())

        for key, button in self.buttons.items():
            if key.startswith("card") and button not in self.selected_card_order:
                button.setIcon(QIcon())

    def update_selected_buttons(self):
        sender = self.sender()
        if not sender or not isinstance(sender, QPushButton):
            return

        button_key = next((k for k, v in self.buttons.items() if v == sender), None)
        if not button_key:
            return

        if sender.isChecked():
            if sender not in self.selected_button_order:
                self.selected_button_order.append(sender)
        else:
            if sender in self.selected_button_order:
                self.selected_button_order.remove(sender)

        for index, button in enumerate(self.selected_button_order):
            icon_path = Bot.APP_PTH[f'sel{index + 1}']
            button.setIcon(QIcon(icon_path))
            button.setIconSize(button.size())

        for key, button in self.buttons.items():
            if key.startswith("sel") and button not in self.selected_button_order:
                button.setIcon(QIcon())

    def set_selected_buttons(self, button_keys: list):
        self.selected_button_order.clear()
        self.selected_button_order = [self.buttons[f'sel{key+1}'] for key in button_keys]

        # First uncheck all selectable buttons
        for key, button in self.buttons.items():
            if key.startswith("sel"):
                button.setChecked(False)
                button.setIcon(QIcon())

        for index, button in enumerate(self.selected_button_order):
            icon_path = Bot.APP_PTH[f'sel{index + 1}']
            button.setChecked(True)
            button.setIcon(QIcon(icon_path))
            button.setIconSize(button.size())

    def set_affinity_buttons(self, button_keys: list):
        selected_affinity_buttons = [self.buttons[f'keyword{id}'] for id in button_keys]

        # First uncheck all selectable buttons
        for key, button in self.buttons.items():
            if key.startswith("keyword"):
                button.setChecked(False)
                button.setIcon(QIcon())

        for index, button in enumerate(selected_affinity_buttons):
            if index == 0:
                icon_path = Bot.APP_PTH[f'affinity']
            else:
                icon_path = Bot.APP_PTH[f'aff{index}']
            button.setChecked(True)
            button.setIcon(QIcon(icon_path))
            button.setIconSize(button.size())

    def set_card_buttons(self, button_keys: list):
        self.selected_card_order.clear()
        if not button_keys: button_keys = [1, 0, 2, 3, 4]
        self.selected_card_order = [self.buttons[f'card{key+1}'] for key in button_keys]

        # First uncheck all selectable buttons
        for key, button in self.buttons.items():
            if key.startswith("card"):
                button.setChecked(False)
                button.setIcon(QIcon())

        for index, button in enumerate(self.selected_card_order):
            icon_path = Bot.APP_PTH[f'aff{index + 1}']
            button.setChecked(True)
            button.setIcon(QIcon(icon_path))
            button.setIconSize(button.size())
            
    def show_guide(self):
        self.guide.raise_()
        self.guide.show()

    def check_version(self):
        self.version_thread = VersionChecker()
        self.version_thread.versionFetched.connect(self.on_version_checked)
        self.version_thread.start()

    def on_version_checked(self, up_to_date):
        if not up_to_date:
            self.buttons['update'].show()
            self.buttons['update'].start_flickering()

    def check_inputs(self):
        # if len(self.selected_button_order) < 6: return False
        if not self.is_lux and self.count == 0: return False
        if self.is_lux and (self.count_exp + self.count_thd) < 1: return False
        return True
    
    def check_sinners(self):
        errors = []
        # print(self.teams)
        for team in self.teams.keys():
            if len(self.teams[team]["sinners"]) < 1:
                errors.append(team)
        
        if not errors: return True

        suffix = ''
        frame = (10, 10, 43, 41)
        if self.is_lux: 
            suffix = '_lux'

        # set up glows
        for i in errors:
            if not self.is_lux and i == self.team or self.is_lux and i == self.team_lux:
                self.buttons[f'team{suffix}{i}'].set_glow_image(Bot.APP_PTH[f"warn"], frame)
            else:
                self.buttons[f'team{suffix}{i}'].set_glow_image(Bot.APP_PTH[f"warn_support"], frame)

        # play it
        CustomButton.glow_multiple(
            [self.buttons[f'team{suffix}{i}'] for i in errors]
        )
        return False
    
    def get_params(self):
        # MD count
        text = self.inputField.text()
        if text: self.count = int(text)
        else: self.count = 0

        # Lux count
        text = self.exp.text()
        if text: self.count_exp = int(text)
        else: self.count_exp = 0
        text = self.thd.text()
        if text: self.count_thd = int(text)
        else: self.count_thd = 0

        # selected teams
        self.teams = dict()
        affinity_values = [self.selected_affinity[i][0] for i in range(7)]
        counts = [affinity_values[:i].count(x) for i, x in enumerate(affinity_values)]
        duplicates = {v for v in affinity_values if affinity_values.count(v) > 1}

        self.update_sinners()
        if self.is_lux:
            self.sinner_selections[self.team_lux + 7] = self.sinners
            for i in self.team_lux_buttons:
                if i is not None:
                    self.teams[i] = {"sinners": self.sinner_selections[i + 7]}
        else:
            self.sinner_selections[self.team] = self.sinners
            for index in range(7):
                i = (self.team + index) % 7
                affinity = self.selected_affinity[i][0]
                if self.buttons[f"team{i}"].isChecked():
                    priority, avoid = self.get_packs(i)
                    self.teams[i] = {
                        "duplicates": affinity in duplicates,
                        "affinity_idx": counts[i],
                        "affinity": self.selected_affinity[i],
                        "sinners": self.sinner_selections[i], 
                        "priority": priority,
                        "avoid": avoid
                    }

        self.settings = {
            'log'        : self.buttons['log'].isChecked(),
            'bonus'      : self.buttons['on0'].isChecked(),
            'restart'    : self.buttons['on1'].isChecked() if not self.is_lux else self.buttons['on7'].isChecked(),
            'altf4'      : self.buttons['on2'].isChecked() if not self.is_lux else self.buttons['on8'].isChecked(),
            'enkephalin' : self.buttons['on3'].isChecked() if not self.is_lux else self.buttons['on9'].isChecked(),
            'skip'       : self.buttons['on4'].isChecked(),
            'wishmaking' : self.buttons['on5'].isChecked(),
            'winrate'    : self.hard or self.buttons['on6'].isChecked(),
            'infinity'   : self.hard and self.buttons['on6'].isChecked(),
            'buff'       : [self.buttons[f'buff{i}'].isChecked() for i in range(4)],
            'card'       : self.get_cards(),
            'keywordless': {Bot.WORDLESS[id]['name']: state for id, state in self.keywordless.items()}
        }

    def start(self):
        self.get_params()
        if not self.check_inputs() or not self.check_sinners():
            self.buttons['guide_icon'].trigger_glow_once()
            return

        if self.buttons['update'].isVisible(): self.buttons['update'].pause_flickering()
        self.save_affinity()

        self.progress.raise_()
        self.progress.show()
        self.run.show()
        QApplication.processEvents()

        p.stop_event.clear()

        self.thread = QThread()
        self.worker = BotWorker(
            self.is_lux,
            self.count,
            self.count_exp,
            self.count_thd,
            self.teams,
            self.settings,
            self.hard,
            self
        )

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.error.connect(self.handle_bot_error)
        self.worker.warning.connect(self.handle_bot_warning)

        self.thread.start()

    @pyqtSlot()
    def to_pause(self):
        self.run.hide()
        self.rerun.hide()
        self.pause.raise_()
        self.pause.show()

    def proceed(self):
        self.pause.hide()
        self.warn.hide()
        self.rerun.raise_()
        self.rerun.show()
        p.pause_event.set()

    @pyqtSlot()
    def stop_execution(self):
        print("Stopping execution...")
        p.stop_event.set()
        p.pause_event.set()

        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        self.run.hide()
        self.rerun.hide()
        self.pause.hide()
        self.progress.hide()
        self.warn.hide()

        if self.buttons['update'].isVisible(): self.buttons['update'].resume_flickering()
        
    def handle_bot_error(self, message):
        self.run.hide()
        self.pause.hide()
        self.rerun.hide()
        self.warn.hide()

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Bot Error")
        msg.setText("An error occurred:")
        msg.setInformativeText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

        self.close()

    def handle_bot_warning(self, message):
        self.warn.raise_()
        self.warn_txt.setText(message)
        self.warn.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())