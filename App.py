import sys, os, datetime, json, hashlib
import source.utils.params as p
import Bot

from stats import log_to_csv

os.environ['QT_LOGGING_RULES'] = 'qt.qpa.*=false'

from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel, QGraphicsOpacityEffect, QMessageBox, QLayout, QHBoxLayout, QVBoxLayout, QScrollArea, QComboBox
from PyQt6.QtGui import QIcon, QFont, QPixmap, QPainter, QIntValidator, QFontDatabase
from PyQt6.QtCore import Qt, QTimer, QEvent, QPropertyAnimation, QObject, pyqtSignal, QThread, QSize, QRect, QPoint, pyqtSlot

import webbrowser
from urllib.request import urlopen


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

    def save_config(self, key, value_list):
        if self.config not in self.data:
            self.data[self.config] = {}

        self.data[self.config][str(key)] = value_list
        self.save_settings()

    def delete_config(self):
        if self.config in self.data:
            del self.data[self.config]
            self.save_settings()

    def config_exists(self, key):
        return str(key) in self.data.get(self.config, {})

sm = SettingsManager()


# Custom selectize like in shiny
class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        self._items = []
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index):
        return self._items.pop(index) if 0 <= index < len(self._items) else None

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), False)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, True)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margin = self.contentsMargins().left()
        return size + QSize(2 * margin, 2 * margin)

    def _do_layout(self, rect, move):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()
        
        for item in self._items:
            widget = item.widget()
            if widget.isHidden():
                continue
            space_x = spacing
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y += line_height + spacing
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0
            
            if move:
                widget.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
                
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
            
        return y + line_height - rect.y()

class SelectizeItem(QWidget):
    removed = pyqtSignal(str)

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text
        self.setStyleSheet('border: 1px solid #d3c19b;background: #000000;border-radius: 3px;padding: 2px 5px;')
        self.setup_ui()

    def setup_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 2, 5, 2)
        
        self.label = QLabel(self.text)
        self.btn_remove = QPushButton("×")
        self.btn_remove.setFixedSize(20, 20)
        
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.btn_remove)
        self.btn_remove.clicked.connect(self.on_remove)

    def sizeHint(self):
        return self.layout.sizeHint()
    
    def setFont(self, font):
        self.label.setFont(font)

    def on_remove(self):
        self.removed.emit(self.text)

class SelectizeWidget(QWidget):
    itemsChanged = pyqtSignal(list)
    itemRemoved = pyqtSignal(str)
    itemAdded = pyqtSignal(str)

    def __init__(self, parent=None, font=None):
        super().__init__(parent)
        self.font = font or QFont()
        self.setStyleSheet('color: #EDD1AC; background: transparent; border: none;')
        self.items = []
        self.setup_ui()
        # self.apply_style()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll Area with Flow Layout
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = FlowLayout(self.scroll_content, margin=5, spacing=5)
        self.scroll.setWidget(self.scroll_content)
        
        self.layout.addWidget(self.scroll)

    def addItems(self, items):
        for item in items:
            self.add_item(item)

    def getItems(self):
        return self.items

    def add_item(self, text):
        if text not in self.items:
            self.items.append(text)
            self._refresh_items()
            self.itemsChanged.emit(self.items)
            self.itemAdded.emit(text)

    def remove_item(self, text):
        if text in self.items:
            self.items.remove(text)
            self._refresh_items()
            self.itemsChanged.emit(self.items)
            self.itemRemoved.emit(text)

    def _refresh_items(self):
        # Clear existing items
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Add current items
        for item in self.items:
            item_widget = SelectizeItem(item)
            item_widget.setFont(self.font)
            item_widget.removed.connect(self.remove_item)
            self.scroll_layout.addWidget(item_widget)


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

    def __init__(self, is_lux, count, count_exp, count_thd, teams, avoid, log, bonus, restart, altf4, enkephalin, skip, hard, app):
        super().__init__()
        self.is_lux = is_lux
        self.count = count
        self.count_exp = count_exp
        self.count_thd = count_thd
        self.teams = teams
        self.avoid = avoid
        self.log = log
        self.bonus = bonus
        self.restart = restart
        self.altf4 = altf4
        self.enkephalin = enkephalin
        self.skip = skip
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
                self.avoid,
                self.log,
                self.bonus,
                self.restart,
                self.altf4,
                self.enkephalin,
                self.skip,
                self.hard,
                self.app,
                warning=self.warning.emit
            )
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()


class CustomButton(QPushButton):
    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.config = config or {}
        self._glow_cache = {}
        self.glowImage = None
        self.animation = None

        self.flickering = False
        self.flicker_paused = False
        self.event_filter = True
        self._setup_button()

    def _setup_button(self):
        if 'geometry' in self.config:
            x, y, w, h = self.config['geometry']
            self.setGeometry(x, y, w, h)

        self.setText(self.config.get('text', ''))
        self.setCheckable(self.config.get('checkable', False))
        self.setChecked(self.config.get('checked', False))

        style = self.config.get('style', '')
        self.setStyleSheet(style if style else 'background: transparent; border: none;')

        if 'click_handler' in self.config:
            self.clicked.connect(self.config['click_handler'])

        if 'icon' in self.config:
            self.setIcon(QIcon(self.config['icon']))
            self.setIconSize(self.size())
        
        if not self.isChecked():
            self.setIcon(QIcon())

        if 'glow' in self.config:
            if 'glow_geometry' in self.config:
                self._setup_glow_effect(self.config['glow_geometry'])
            else:
                self._setup_glow_effect(self.config['geometry'])
        
        if 'filter' in self.config:
            self.event_filter = bool(self.config['filter'])

    def _setup_glow_effect(self, geometry: tuple, enable_hover=True):
        if hasattr(self, 'glowImage') and self.glowImage:
            self.glowImage.deleteLater()
        
        self.glowImage = QLabel(self.parentWidget())
        
        if self.config['glow'] not in self._glow_cache:
            self._glow_cache[self.config['glow']] = QPixmap(self.config['glow'])
        
        pixmap = self._glow_cache[self.config['glow']].scaled(
            geometry[2], geometry[3],
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.glowImage.setPixmap(pixmap)
        
        self.glowImage.setGeometry(*geometry)
        self.glowImage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.glowImage.setVisible(False)
        self.glowImage.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        self.glowImage.raise_()
        
        self.opacityEffect = QGraphicsOpacityEffect(self.glowImage)
        self.opacityEffect.setOpacity(0.0)
        self.glowImage.setGraphicsEffect(self.opacityEffect)

        self.animation = QPropertyAnimation(self.opacityEffect, b"opacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)

        if enable_hover:
            self.installEventFilter(self)
        elif hasattr(self, 'event_filter'):
            self.removeEventFilter(self)

    def eventFilter(self, obj, event):
        if not self.event_filter:
            return super().eventFilter(obj, event)
    
        if obj == self and self.glowImage:
            if event.type() == QEvent.Type.Enter:
                self._start_glow()
            elif event.type() == QEvent.Type.Leave:
                self._end_glow()
        
        return super().eventFilter(obj, event)

    def _start_glow(self):
        if not self.glowImage.isVisible():
            self.glowImage.setVisible(True)
        
        self.animation.stop()
        self.animation.setDirection(QPropertyAnimation.Direction.Forward)
        self.animation.start()

    def _end_glow(self):
        self.animation.stop()
        self.animation.setDirection(QPropertyAnimation.Direction.Backward)
        self.animation.start()
        
        QTimer.singleShot(self.animation.duration(), 
                         lambda: self.glowImage.setVisible(False) 
                         if self.opacityEffect.opacity() == 0.0 
                         else None)
        
    def trigger_glow_once(self):
        if self.glowImage and self.animation:
            self.glowImage.setVisible(True)
            self.animation.stop()
            self.animation.setDirection(QPropertyAnimation.Direction.Forward)
            self.animation.start()

            QTimer.singleShot(self.animation.duration(), lambda: self._end_glow())

    def start_flickering(self):
        self.animation.setDuration(1000)
        if not self.flickering:
            self.flickering = True
            self.flicker_paused = False
            self._flicker_cycle()

    def _flicker_cycle(self):
        if not self.flickering or self.flicker_paused:
            return
        
        self.trigger_glow_once()
        QTimer.singleShot(1900, self._flicker_cycle)

    def pause_flickering(self):
        if self.flickering:
            self.flicker_paused = True
            self.animation.stop()

    def resume_flickering(self):
        if self.flickering and self.flicker_paused:
            self.flicker_paused = False
            self._flicker_cycle()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.glowImage and 'glow_geometry' not in self.config:
            self.glowImage.setGeometry(self.geometry())

    def set_glow_image(self, image_path, geometry=None):
        if hasattr(self, 'glowImage') and self.glowImage:
            self.glowImage.deleteLater()
        
        self.config['glow'] = image_path
        
        if geometry:
            x, y, _, _ = self.config['geometry']
            self.config['glow_geometry'] = (geometry[0] + x, geometry[1] + y, geometry[2], geometry[3])
        elif 'glow_geometry' in self.config:
            del self.config['glow_geometry']
        
        if 'glow_geometry' in self.config:
            self._setup_glow_effect(self.config['glow_geometry'], enable_hover=False)
        else:
            self._setup_glow_effect(self.config['geometry'], enable_hover=False)
    
    @staticmethod
    def glow_multiple(buttons):
        for button in buttons:
            if isinstance(button, CustomButton):
                button.trigger_glow_once()
    
class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        # params
        self.count = 0
        self.affinity = 0
        self.log = True
        self.sinners = []
        self.bonus = False
        self.restart = True
        self.altf4 = False
        self.hard = False

        self.enkephalin = False
        self.skip = True
        self.is_lux = False
        self.count_exp = 1
        self.count_thd = 3

        self.sinner_selections = {i: sm.get_team(i) for i in range(10)}
        self.affinity_lux = self._day()

        self._init_ui()
        self._create_buttons()
    
    #     self.debug_timer = QTimer()
    #     self.debug_timer.timeout.connect(self.print_state)
    #     self.debug_timer.start(2000)  # 2000 ms = 2 sec

    # def print_state(self):
    #     print(f"Current state - Affinity: {self.affinity}, Priority: {self.priority}")
          
    def _init_ui(self):
        """Initialize main window settings"""
        self.setWindowTitle("app")
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
        self.config_widgets = []

        self.config = QLabel(self)
        self.config.setPixmap(QPixmap(Bot.APP_PTH["config"]))
        self.config.setGeometry(0, 93, 700, 693)
        self.config.hide()

        self.priority_team = QLabel(self.config)
        self.priority_team.setPixmap(QPixmap(Bot.APP_PTH[f'team{self.affinity}']))
        self.priority_team.setGeometry(38, 121, 301, 247)
        self.priority_team.show()

        self.combo_boxes = []
        self.selectize_widgets = []

        self.hard_conf = QLabel(self.config)
        self.hard_conf.setPixmap(QPixmap(Bot.APP_PTH["hard_conf"]))
        self.hard_conf.setGeometry(228, 421, 169, 26)
        self.hard_conf.hide()
        self.hard_conf2 = QLabel(self.config)
        self.hard_conf2.setPixmap(QPixmap(Bot.APP_PTH["hard_conf2"]))
        self.hard_conf2.setGeometry(87, 31, 149, 27)
        self.hard_conf2.hide()

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
        self.thd.setGeometry(108, 72, 90, 50)
        self.thd.setValidator(QIntValidator(0, 1000))
        self.thd.setText(str(self.count_thd))
        self.thd.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thd.setStyleSheet('color: #EDD1AC; background: transparent; border: none;')

        # self.test = QPushButton(self)
        # self.test.setText("Test")
        # self.test.setGeometry(228, 514, 169, 26)
        # self.test.show()

    def set_priority(self):
        if sm.config_exists(self.affinity):
            self.priority = sm.get_config(self.affinity)
        else: 
            self.priority = self.get_priority(self.affinity)
        
        if sm.config_exists(7):
            self.avoid = sm.get_config(7)
        else:
            self.avoid = self.get_avoid()

        self.all = self.get_all()

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
            if self.hard:
                self.set_buttons_active([False, True, False, False, False])
            else:
                self.set_buttons_active([False, True, False, False, True])
            sm.delete_config()
        elif sm.config_exists(team):
            self.priority = sm.get_config(team)
        else:
            self.priority = self.get_priority(team)
        self.all = self.get_all()
        
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

    def _day(self):
        day_number = datetime.datetime.today().weekday()
        return (day_number > 1) + (day_number > 3) - (day_number == 6)
    
    def get_priority(self, affinity):
        if self.hard:
            team_data = Bot.TEAMS[list(Bot.TEAMS.keys())[affinity]]
        else:
            team_data = Bot.HARD[list(Bot.HARD.keys())[affinity]]
        seen = set()
        unique_floors = []

        for i in range(1, 6):
            for floor in team_data.get(f"floor{i}", []):
                if floor not in seen:
                    seen.add(floor)
                    unique_floors.append(floor)
        return unique_floors
    
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

    def _get_button_damage(self):
        return [
            (f'affinity_lux{i-2}', {
                'geometry': (45 + 89*i, 188, 74, 88),
                'checkable': True,
                'checked': i == self._day() + 2,
                'click_handler': self.activate_permanent_button,
                'icon': Bot.APP_PTH['affinity']
            }) for i in range(2, 5)
        ]

    def _get_button_affinity(self):
        return [
            (f'affinity{i}', {
                'geometry': (45 + 89*i, 280, 74, 88),
                'checkable': True,
                'checked': i == 0,
                'click_handler': self.activate_permanent_button,
                'icon': Bot.APP_PTH['affinity'],
            }) for i in range(7)
        ]
    
    def _get_button_on(self):
        return [
            (f'on{i}', {
                'geometry': (461, 411 + 54*i + (i > 1), 144, 45),
                'checkable': True,
                'checked': i == 1 or i == 4,
                'click_handler': self.update_button_icons,
                'icon': Bot.APP_PTH['On']
            }) for i in range(5)
        ] + [
            (f'on{i+5}', {
                'geometry': (30 + 496*i, 235, 144, 45),
                'checkable': True,
                'checked': i == 1,
                'click_handler': self.update_button_icons,
                'icon': Bot.APP_PTH['On']
            }) for i in range(2)
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
                'geometry': (209, 160, 217, 55),
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
                'click_handler': lambda: self.reset_to_defaults(self.affinity),
                'glow': Bot.APP_PTH['del']
            }),

            'hard': CustomButton(self, {
                'geometry': (24, 161, 178, 59),
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
        all_buttons = self._get_button_affinity() + self._get_button_selected()
        for name, settings in all_buttons:
            self.buttons[name] = CustomButton(self, settings)

        for name, settings in self._get_button_on()[:5]:
            self.buttons[name] = CustomButton(self.config, settings)
        for name, settings in self._get_button_on()[5:]:
            self.buttons[name] = CustomButton(self.lux, settings)

        for name, settings in self._get_button_damage():
            self.buttons[name] = CustomButton(self.lux, settings)

        self.buttons['update'].hide()
        self.check_version()

        self.set_affinity()
        self.priority_team.setPixmap(QPixmap(Bot.APP_PTH[f'team{self.affinity}']))
        self.set_priority()
        self.set_widgets()
        self.set_selected_buttons(self.sinner_selections[self.affinity])
        self.set_buttons_active(sm.get_config(8))
        self.overlay.raise_()

    def set_affinity(self):
        # first 7 values - whether button is activated, last - aff index
        state = sm.get_aff()
        if state:
            self.affinity = state["7"]
            for i in range(7):
                if state[str(i)]:
                    self.buttons[f"affinity{i}"].setChecked(True)
                    if i == self.affinity:
                        self.buttons[f"affinity{i}"].setIcon(QIcon(Bot.APP_PTH["affinity"]))
                    else:
                        self.buttons[f"affinity{i}"].setIcon(QIcon(Bot.APP_PTH["affinity_support"]))
                else:
                    self.buttons[f"affinity{i}"].setChecked(False)
                    self.buttons[f"affinity{i}"].setIcon(QIcon())
    
    def save_affinity(self):
        state = dict()
        for i in range(7):
            state[str(i)] = self.buttons[f"affinity{i}"].isChecked()
        state[str(7)] = self.affinity
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
        if self.hard:
            self.set_buttons_active([False, True, False, False, False])
            self.hard_conf.show()
            self.hard_conf2.show()
        else:
            self.set_buttons_active([False, True, False, False, True])
            self.hard_conf.hide()
            self.hard_conf2.hide()
        self.set_buttons_active(sm.get_config(8))

    def set_lux(self):
        self.lux.show()
        self.lux.raise_()
        self.is_lux = True
        self.buttons['start'].raise_()
        self.update_sinners()
        self.sinner_selections[self.affinity] = self.sinners
        self.set_selected_buttons(self.sinner_selections[self.affinity_lux + 7])

    def lux_hide(self):
        self.is_lux = False
        self.update_sinners() 
        print(self.sinners)
        print(self.sinner_selections)
        print(self.affinity_lux)
        print(self.affinity)
        self.sinner_selections[self.affinity_lux + 7] = self.sinners
        self.set_selected_buttons(self.sinner_selections[self.affinity])
        self.lux.hide()

    def save(self):
        if self.is_lux:
            team = self.affinity_lux + 7
        else:
            team = self.affinity
        self.update_sinners()
        sm.save_team(team, self.sinners)
    
    def reset(self):
        self.selected_button_order.clear()
        for key, button in self.buttons.items():
            if key.startswith("sel"):
                button.setChecked(False)
                button.setIcon(QIcon())

        if self.is_lux:
            self.sinner_selections[self.affinity_lux + 7]
        else:
            self.sinner_selections[self.affinity]

    def save_config(self):
        sm.save_config(self.affinity, self.priority)
        sm.save_config(7, self.avoid)
        sm.save_config(8, self.get_config_buttons())
        self.config.hide()

    def update_sinners(self):
        self.sinners = [button.config.get('id') for button in self.selected_button_order]

    def get_config_buttons(self):
        activated = []
        for i in range(5):
            activated.append(self.buttons[f'on{i}'].isChecked())
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
        on_buttons = [self.buttons[f'on{i}'] for i in range(5)]
        
        for button, state in zip(on_buttons, states):
            button.setChecked(state)
            if state:
                icon_path = getattr(button, 'config', {}).get('icon', '')
                if icon_path:
                    button.setIcon(QIcon(icon_path))
            else:
                button.setIcon(QIcon())
            button.setIconSize(button.size())


    def activate_permanent_button(self):
        sender = self.sender()
        if not sender or not isinstance(sender, QPushButton):
            return

        self.update_sinners()
        if self.is_lux:
            self.sinner_selections[self.affinity_lux + 7] = self.sinners
            if sender != self.buttons[f"affinity{self.affinity_lux}"]:
                self.buttons[f"affinity_lux{self.affinity_lux}"].setChecked(False)
                self.buttons[f"affinity_lux{self.affinity_lux}"].setIcon(QIcon())
                sender.setIcon(QIcon(Bot.APP_PTH['affinity']))
            else:
                sender.setChecked(True)
            for i in range(3):
                if self.buttons[f"affinity_lux{i}"] == sender:
                    self.affinity_lux = i
                    break
        else:
            self.sinner_selections[self.affinity] = self.sinners
            null_visual_state = sender.icon().isNull()

            if null_visual_state:
                sender.setIcon(QIcon(Bot.APP_PTH['affinity']))
                self.buttons[f"affinity{self.affinity}"].setIcon(QIcon(Bot.APP_PTH['affinity_support']))
                for i in range(7):
                    if self.buttons[f"affinity{i}"] == sender:
                        self.affinity = i
                        break
            else:
                if sender != self.buttons[f"affinity{self.affinity}"]:
                    sender.setIcon(QIcon())
                else:
                    sender.setChecked(True)
        if self.is_lux:
            self.set_selected_buttons(self.sinner_selections[self.affinity_lux + 7])
        else:
            self.priority_team.setPixmap(QPixmap(Bot.APP_PTH[f'team{self.affinity}']))
            self.reset_to_defaults(self.affinity, default=False)
            self.set_selected_buttons(self.sinner_selections[self.affinity])

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
            if len(self.teams[team]["sinners"]) < 6:
                errors.append(team)
        
        if not errors: return True

        # set up glows
        frame = (9, 7, 55, 52)
        for i in errors:
            if i == self.affinity:
                self.buttons[f'affinity{i}'].set_glow_image(Bot.APP_PTH["warn"], frame)
            else:
                self.buttons[f'affinity{i}'].set_glow_image(Bot.APP_PTH["warn_support"], frame)

        # play it
        CustomButton.glow_multiple(
            [self.buttons[f'affinity{i}'] for i in errors]
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
        self.update_sinners()
        if self.is_lux:
            self.teams[self.affinity_lux] = {"sinners": self.sinners}
        else:
            self.sinner_selections[self.affinity] = self.sinners
            for index in range(7):
                i = (self.affinity + index) % 7
                if self.buttons[f"affinity{i}"].isChecked():
                    self.teams[i] = {
                        "sinners": self.sinner_selections[i], 
                        "priority": sm.get_config(str(i))
                    }

        self.log = self.buttons['log'].isChecked()
        self.bonus, self.restart, self.altf4, self.enkephalin, self.skip = self.get_config_buttons()
        if self.is_lux:
            self.enkephalin = self.buttons['on5'].isChecked()
            self.restart = self.buttons['on6'].isChecked()

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
            self.avoid,
            self.log,
            self.bonus,
            self.restart,
            self.altf4,
            self.enkephalin,
            self.skip,
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