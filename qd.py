## ==> SPLASH SCREEN
from ui_splash_screen import *

## ==> MAIN WINDOW
from ui import *
# from ui import again
import threading
import subprocess
import sys
import platform
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent, QThread, Signal, QMetaObject)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient)
from PySide6.QtWidgets import *
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QMessageBox
import re
import requests
import time
from setup_gui import QD_Setup
from desktop_singin import FuturisticAuthWindow  # Import FuturisticAuthWindow
from main import MyMainWindow
import subprocess
from engine import Widget
import httpx
import asyncio
global pre_model,pre_engine
pre_model = None
pre_engine=None
server_thread = None
counter = 0
from server import text



class SplashScreen(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_SplashScreen()
        self.ui.setupUi(self)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.ui.dropShadowFrame.setGraphicsEffect(self.shadow)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progress)
        self.timer.start(35)
        self.ui.label_description.setText("<strong>WELCOME</strong> TO Advanced AI Agent")
        QtCore.QTimer.singleShot(1500, lambda: self.ui.label_description.setText("<strong>LOADING</strong> Checking Ai Model"))
        QtCore.QTimer.singleShot(3000, lambda: self.ui.label_description.setText("<strong>LOADING</strong> UI"))
        self.show()

    def progress(self):
        global counter

        self.ui.progressBar.setValue(counter)

        if counter > 10:
            self.timer.stop()
            if self.is_user_logged_in():
                self.main = MyMainWindow()
                self.main.show()
            else:
                self.auth_window = FuturisticAuthWindow()
                self.auth_window.show()

            self.close()


        counter += 1

    def is_user_logged_in(self):
        # Implement your logic to check if the user is logged in
        # For example, check if a token exists in a file or in memory
        return os.path.exists('user_token.json')

    def on_login_successful(self):
        # Close the auth window
        self.auth_window.close()
        # Open the main window
        self.main = MyMainWindow()
        self.main.show()


def run_additional_code():
    app = QApplication(sys.argv)
    # Create and show the SplashScreen
    window = SplashScreen()

    sys.exit(app.exec())

additional_code_thread = threading.Thread(target=run_additional_code)

additional_code_thread.start()
additional_code_thread.join()

