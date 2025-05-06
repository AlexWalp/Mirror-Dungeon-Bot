import sys, os
import source.utils.params as p
import Bot

os.environ['QT_LOGGING_RULES'] = 'qt.qpa.*=false'

from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel, QGraphicsOpacityEffect, QMessageBox
from PyQt6.QtGui import QIcon, QFont, QPixmap, QPainter, QIntValidator
from PyQt6.QtCore import Qt, QTimer, QEvent, QPropertyAnimation, QObject, pyqtSignal, QThread, pyqtSlot
import webbrowser


class BotWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, count, affinity, sinners, log, bonus, restart, altf4, app):
        super().__init__()
        self.count = count
        self.affinity = affinity
        self.sinners = sinners
        self.log = log
        self.bonus = bonus
        self.restart = restart
        self.altf4 = altf4
        self.app = app

    def run(self):
        try:
            Bot.execute_me(
                self.count,
                self.affinity,
                self.sinners,
                self.log,
                self.bonus,
                self.restart,
                self.altf4,
                self.app
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

    def _setup_glow_effect(self, geometry: tuple):
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

        self.installEventFilter(self)

    def eventFilter(self, obj, event):
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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.glowImage and 'glow_geometry' not in self.config:
            self.glowImage.setGeometry(self.geometry())
    
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

        self._init_ui()
        self._create_buttons()
        
    def _init_ui(self):
        """Initialize main window settings"""
        self.setWindowTitle("ChargeGrinder")
        self.setWindowIcon(QIcon(Bot.ICON))
        self.setFixedSize(700, 892)
        self.background = QPixmap(Bot.APP_PTH["UI"])
        
        self.inputField = QLineEdit(self)
        self.inputField.setFont(QFont("Excelsior Sans", 30))
        self.inputField.setGeometry(108, 100, 90, 50)
        self.inputField.setValidator(QIntValidator(0, 1000))
        self.inputField.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.inputField.setStyleSheet('color: #EDD1AC; background: transparent; border: none;')

        self.overlay = QLabel(self)
        overlay_pixmap = QPixmap(Bot.APP_PTH['frames'])
        self.overlay.setPixmap(overlay_pixmap)
        self.overlay.setGeometry(48, 374, 601, 296)
        self.overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.guide = QLabel(self)
        self.guide.setPixmap(QPixmap(Bot.APP_PTH['guide']))
        self.guide.setGeometry(0, 0, 700, 892)
        self.guide.hide()
        self.guide_close_btn = QPushButton(self.guide)
        self.guide_close_btn.setGeometry(214, 769, 241, 74)
        self.guide_close_btn.clicked.connect(self.guide.hide)
        self.guide_close_btn.setStyleSheet('background: transparent; border: none;')

        self.progress = QLabel(self)
        self.progress.setPixmap(QPixmap(Bot.APP_PTH['progress']))
        self.progress.setGeometry(0, 0, 700, 892)
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
        self.stop.setGeometry(358, 443, 73, 69)
        self.stop.clicked.connect(self.stop_execution)
        self.stop.setStyleSheet('background: transparent; border: none;')
        self.play = QPushButton(self.pause)
        self.play.setGeometry(268, 443, 73, 69)
        self.play.clicked.connect(self.proceed)
        self.play.setStyleSheet('background: transparent; border: none;')
        

        self.selected_button_order = []

    def _get_button_affinity(self):
        return [
            (f'affinity{i}', {
                'geometry': (45 + 89*i, 214, 74, 88),
                'checkable': True,
                'checked': i == 0,
                'click_handler': self.activate_permanent_button,
                'icon': Bot.APP_PTH['affinity']
            }) for i in range(7)
        ]
    
    def _get_button_on(self):
        return [
            (f'on{i}', {
                'geometry': (456, 710 + 60*i + 2*(i == 2), 144, 45),
                'checkable': True,
                'checked': i == 1,
                'click_handler': self.update_button_icons,
                'icon': Bot.APP_PTH['On']
            }) for i in range(3)
        ]
    
    def _get_button_selected(self):
        return [
            (f'sel{i+1}', {
                'geometry': (51 + 99*(i - 6*(i > 5)), 373 + 149*(i > 5), 103, 147),
                'checkable': True,
                'checked': False,
                'id': i,
                'click_handler': self.update_selected_buttons,
            }) for i in range(12)
        ]

    def _create_buttons(self):
        """Create and configure all buttons using the CustomButton class"""
        self.buttons = {
            'log': CustomButton(self, {
                'geometry': (563, 29, 43, 40),
                'checkable': True,
                'checked': True,
                'click_handler': self.update_button_icons,
                'icon': Bot.APP_PTH['log_on']
            }),

            'guide_icon': CustomButton(self, {
                'geometry': (45, 25, 135, 49),
                'click_handler': self.show_guide,
                'glow': Bot.APP_PTH['guide_icon'],
            }),

            'start': CustomButton(self, {
                'geometry': (453, 97, 216, 65),
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
        all_buttons = self._get_button_on() + self._get_button_affinity() + self._get_button_selected()
        for name, settings in all_buttons:
            self.buttons[name] = CustomButton(self, settings)
        self.overlay.raise_()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.background)

    def activate_permanent_button(self):
        sender = self.sender()
        if not sender or not isinstance(sender, QPushButton):
            return

        for i in range(7):
            if self.buttons[f"affinity{i}"] != sender:
                self.buttons[f"affinity{i}"].setChecked(False)
                self.buttons[f"affinity{i}"].setIcon(QIcon())
            else:
                self.affinity = i

        if sender.isChecked():
            sender.setChecked(True)
            sender.setIcon(QIcon(Bot.APP_PTH['affinity']))
            sender.setIconSize(sender.size())

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
        
    def show_guide(self):
        self.guide.raise_()
        self.guide.show()

    def check_inputs(self):
        if len(self.selected_button_order) < 6: return False
        if self.count == 0: return False
        return True
    
    def get_params(self):
        # MD count
        text = self.inputField.text()
        if text: self.count = int(text)
        else: self.count = 0

        # selected sinners
        self.sinners = [button.config.get('id') for button in self.selected_button_order]

        # other
        self.log = self.buttons['log'].isChecked()
        self.bonus = self.buttons['on0'].isChecked()
        self.restart = self.buttons['on1'].isChecked()
        self.altf4 = self.buttons['on2'].isChecked()

    def start(self):
        self.get_params()
        if not self.check_inputs():
            self.buttons['guide_icon'].trigger_glow_once()
            return
        self.progress.raise_()
        self.progress.show()
        self.run.show()
        QApplication.processEvents()

        p.stop_event.clear()

        self.thread = QThread()
        self.worker = BotWorker(
            self.count,
            self.affinity,
            self.sinners,
            self.log,
            self.bonus,
            self.restart,
            self.altf4,
            self
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.error.connect(self.handle_bot_error)

        self.thread.start()

    @pyqtSlot()
    def to_pause(self):
        self.run.hide()
        self.rerun.hide()
        self.pause.raise_()
        self.pause.show()

    def proceed(self):
        self.pause.hide()
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
        
    def handle_bot_error(self, message):
        self.run.hide()
        self.pause.hide()
        self.rerun.hide()

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Bot Error")
        msg.setText("An error occurred:")
        msg.setInformativeText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())