#ui.py
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect, QThread, Signal,
    QSize, QTime, QUrl, Qt, QPropertyAnimation, QEasingCurve)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform, QTextCursor)
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QListView, QMainWindow,
    QMenuBar, QPushButton, QScrollArea, QSizePolicy,
    QSpacerItem, QTextEdit, QVBoxLayout, QWidget, QTextBrowser, QListWidget, QSplitter)
from PySide6.QtGui import QMovie
from PySide6.QtCore import QTimer
import subprocess
import os
import time
import requests
from engine import EngineWindow
import sys
def resource_path(relative_path):
     if hasattr(sys, '_MEIPASS'):
         return os.path.join(sys._MEIPASS, relative_path)
     return os.path.join(os.path.abspath("."), relative_path)

a_p = '/usr/local/bin/asset/'
ubuntu = False
STYLE_SHEET = """
QWidget {
    background-color: transparent;
    color: white;
    font-family: Arial, sans-serif;
}

QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #000000, stop:1 #2E0619);
}

#side_panel {
    background-color: rgba(0, 0, 0, 0.5);
    border-right: 1px solid #243689;
}

#new_chat_btn, #sponsor_us_btn, #future_plan_btn, #log_in_btn {
    padding: 10px 20px;
    border: none;
    border-radius: 15px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #000000, stop:1 #2E0619);
    color: white;
    font-weight: bold;
    margin-bottom: 10px;
    text-align: left;
}

#new_chat_btn:hover, #sponsor_us_btn:hover, #future_plan_btn:hover, #log_in_btn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #1c1c1c, stop:1 #5a9aff);
}

#chat_list {
    background-color: transparent;
    color: white;
    border: none;
}

#chat_list::item {
    padding: 10px;
    border-radius: 15px;
}

#chat_list::item:selected {
    background-color: rgba(66, 135, 245, 0.3);
}


#main_content {
    background-color: transparent;
}

#send_btn, #engine_btn {
    padding: 10px 20px;
    border: 2px solid #243689; /* Add blue border */
    border-radius: 15px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #000000, stop:1 #2E0619);
    color: white;
    font-weight: bold;
    margin-bottom: 10px;
}

#send_btn:hover, #engine_btn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #1c1c1c, stop:1 #2E0619);
}

QLineEdit, QTextEdit, QDateEdit, QComboBox {
    padding: 10px;
    border: 2px solid #4287f5;
    border-radius: 15px;
    background-color: rgba(0, 0, 0, 0.7); /* Ensure background is dark */
    color: white;
    margin-bottom: 10px;
}

QComboBox::drop-down {
    border: none;
}

QComboBox::down-arrow {
    image: url(path_to_your_down_arrow_icon);
    width: 12px;
    height: 12px;
}

QPushButton {
    padding: 10px 20px;
    border: none;
    border-radius: 15px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #000000, stop:1 #2E0619);
    color: white;
    font-weight: bold;
    margin-bottom: 10px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #1c1c1c, stop:1 #026390);
}

QRadioButton, QCheckBox {
    color: white;
}
"""



class AnimatedSplitter(QSplitter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setHandleWidth(2)
        self.splitterMoved.connect(self.handle_splitter_moved)
        self.animation = QPropertyAnimation(self, b"sizes")
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.animation.setDuration(300)  # 300ms animation duration

    def handle_splitter_moved(self, pos, index):
        if not self.animation.state() == QPropertyAnimation.Running:
            self.animation.setStartValue(self.sizes())
            self.animation.setEndValue(self.sizes())
            self.animation.start()

class Ui_MainWindow(QMainWindow):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 800)
        MainWindow.setMinimumSize(800, 600)
        
        # Set up the central widget and main layout
        self.centralwidget = QWidget(MainWindow)
        self.main_layout = QHBoxLayout(self.centralwidget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create an AnimatedSplitter
        self.splitter = AnimatedSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)
        
        # Set up the side panel
        self.setup_side_panel()
        
        # Set up the main content area
        self.setup_main_content()
        
        # Set the initial sizes of the splitter
        self.splitter.setSizes([100, 1000])  # Set default width for side panel and remaining space for main content
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        # Set up the menu bar
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QRect(0, 0, 1200, 22))
        MainWindow.setMenuBar(self.menubar)
        
        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setStyleSheet(STYLE_SHEET)

    def setup_side_panel(self):
        self.side_panel = QWidget()
        self.side_panel.setObjectName("side_panel")
        self.side_panel.setMinimumWidth(50)
        self.side_panel.setMaximumWidth(1220)
        
        side_layout = QVBoxLayout(self.side_panel)
        side_layout.setSpacing(10)
        side_layout.setContentsMargins(10, 10, 10, 10)
        
        # 14 QPushButtons
        button_names = [
            "Button 1", "Button 2", "Button 3", "Button 4",
            "Button 5", "Button 6", "Button 7", "Button 8",
            "Button 9", "API", "AI training", "Popular Models",
            "(IL) Extension", "Engine Settings"
        ]
        
        for name in button_names:
            btn = QPushButton(name)
            btn.setObjectName(f"{name.lower().replace(' ', '_')}_btn")
            side_layout.addWidget(btn)
            if name == "Engine || Models Settings":
                btn.clicked.connect(self.show_engine_window)
        
        # Your Account button with user logo
        self.account_btn = QPushButton("Your Account")
        self.account_btn.setObjectName("account_btn")
        user_icon = QIcon(resource_path("./asset/user.png"))  # Make sure to have a user icon SVG in your asset folder
        self.account_btn.setIcon(user_icon)
        self.account_btn.setIconSize(QSize(24, 24))
        side_layout.addWidget(self.account_btn)
        
        # Add side panel to splitter
        self.splitter.addWidget(self.side_panel)
        
    def setup_main_content(self):
        self.main_content = QWidget()
        self.main_content.setObjectName("main_content")
        
        content_layout = QVBoxLayout(self.main_content)
        content_layout.setSpacing(10)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create a horizontal layout to center the text browser
        center_layout = QHBoxLayout()
        
        left_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        center_layout.addItem(left_spacer)
        
        # Chat display area
        self.text_browser = QTextBrowser()
        self.text_browser.setObjectName("chat_display")
        self.text_browser.setMaximumWidth(800)
        self.text_browser.setMinimumWidth(800)
        center_layout.addWidget(self.text_browser)
        
        right_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        center_layout.addItem(right_spacer)
        
        content_layout.addLayout(center_layout)
        
        # Input area
        input_layout = QHBoxLayout()
        
        left_input_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        input_layout.addItem(left_input_spacer)
        
        self.input_textEdit = QTextEdit()
        self.input_textEdit.setObjectName("input_textEdit")
        self.input_textEdit.setPlaceholderText("Say Something")
        self.input_textEdit.setMaximumHeight(100)
        self.input_textEdit.setMaximumWidth(750)
        self.input_textEdit.setMinimumWidth(750)
        input_layout.addWidget(self.input_textEdit)
        
        self.send_btn = QPushButton()
        self.send_btn.setObjectName("send_btn")
        self.send_btn.setIcon(QIcon(resource_path("asset/send.svg")))
        self.send_btn.setIconSize(QSize(24, 24))
        self.send_btn.setFixedSize(QSize(40, 40))
        input_layout.addWidget(self.send_btn)
        
        right_input_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        input_layout.addItem(right_input_spacer)
        
        content_layout.addLayout(input_layout)
        
        # Add main content to splitter
        self.splitter.addWidget(self.main_content)

    
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("QueenDahyun")
    
    def show_engine_window(self):
        self.engine_window = EngineWindow()
        self.engine_window.show()