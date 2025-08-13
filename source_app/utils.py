import sys, os, json, hashlib
from datetime import datetime, timezone, timedelta
import source.utils.params as p
import Bot

from stats import log_to_csv

os.environ['QT_LOGGING_RULES'] = 'qt.qpa.*=false'

from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel, QGraphicsOpacityEffect, QMessageBox, QLayout, QHBoxLayout, QVBoxLayout, QScrollArea, QComboBox
from PyQt6.QtGui import QIcon, QFont, QPixmap, QPainter, QIntValidator, QFontDatabase
from PyQt6.QtCore import Qt, QTimer, QEvent, QPropertyAnimation, QObject, pyqtSignal, QThread, QSize, QRect, QPoint, pyqtSlot

import webbrowser
from urllib.request import urlopen