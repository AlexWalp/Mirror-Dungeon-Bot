import sys, os, json, hashlib, copy
from datetime import datetime, timezone, timedelta

if getattr(sys, "frozen", False):
    base = sys._MEIPASS
    os.add_dll_directory(base)
    os.environ["PATH"] = base + os.pathsep + os.environ.get("PATH", "")

import source.utils.params as p
from source.utils.log_config import *
import Bot

from stats import log_to_csv

# os.environ['QT_LOGGING_RULES'] = 'qt.qpa.*=false'

from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel, QGraphicsOpacityEffect, QMessageBox, QLayout, QHBoxLayout, QVBoxLayout, QScrollArea, QComboBox, QMainWindow, QFrame, QStyleFactory
from PyQt6.QtGui import QIcon, QFont, QPixmap, QPainter, QIntValidator, QFontDatabase, QRegularExpressionValidator
from PyQt6.QtCore import Qt, QTimer, QEvent, QPropertyAnimation, QObject, pyqtSignal, QThread, QSize, QRect, QPoint, QRegularExpression, pyqtSlot

import webbrowser
from urllib.request import urlopen