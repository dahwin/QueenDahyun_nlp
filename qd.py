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
import subprocess
from engine import Widget
import httpx
import asyncio
global pre_model,pre_engine
pre_model = None
pre_engine=None
server_thread = None
from ui import resource_path,a_p,ubuntu
from server import text
def run_server():
    # # Define the command to run the script with nohup
    # run_command = ["dahwin/bin/python", "server.py"]
    # # run_command = ["dahwin/Scripts/python.exe", "server.py"]

    # # Run the script command
    # subprocess.run(run_command)
    python_3_11_path = "/usr/local/bin/dahwin/bin/python3.11"
    # Use subprocess to run the code
    process = subprocess.Popen([python_3_11_path, "-c", text])
    process.wait()


def start_server_thread():
    global server_thread
    server_thread = threading.Thread(target=run_server)
    server_thread.start()

start_server_thread()
def close_server():
        if server_thread is not None:
            server_thread.join()  # Join the server thread
class ChatThread(QThread):

    message_received = Signal(str)
    stream_finished = Signal()
    stream_started = Signal()  # New signal to indicate the start of the response

    def __init__(self, user_input):
        super().__init__()
        self.user_input = user_input

    def run(self):
        try:
            self.stream_responses(self.user_input)
        except Exception as e:
            print(f"Error in ChatThread: {e}")

    def stream_responses(self, prompt):
        global pre_model,pre_engine,server_thread,u

        u = "http://localhost:8000/"
        async def restart_server():
            url = f"{u}restart"  # Update the URL if your server runs on a different address
            async with httpx.AsyncClient() as client:
                response = await client.post(url)
                print("Server is restarting...")     

        
        w = Widget()
        engine_name,model_id,formate,max_new_token,temperature,top_p,top_k,do_sample,max_time,system_insturction = w.print_updated_parameters()
        print(engine_name,model_id,formate,max_new_token,temperature,top_p,top_k,do_sample,max_time,system_insturction)
        url = f"{u}{engine_name}"
        payload = {
            "model_id": model_id,
            "quantization": formate,
            "dtype": "float16",
            "prompt": prompt,
            "max_new_tokens": max_new_token,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "prompt_template": f"system\n{system_insturction}\n\nuser\n{prompt}\nassistant\n"
        
        }
        # if pre_model!=None and pre_model!=model_id
        if pre_engine != None and pre_engine != engine_name:
            if server_thread is not None:
                server_thread.join()
            asyncio.run(restart_server())
            time.sleep(3)
            start_server_thread()

        response = requests.post(url, json=payload, stream=True)
        pre_model=model_id
        pre_engine=engine_name
        buffer = ""
        self.stream_started.emit()  # Emit the start signal before beginning to stream
        for chunk in response.iter_content(chunk_size=512):
            if chunk:
                buffer += chunk.decode('utf-8')
                while " " in buffer:
                    word, buffer = buffer.split(" ", 1)
                    self.message_received.emit(word + " ")
        



        # Emit any remaining words in the buffer
        if buffer:
            self.message_received.emit(buffer)

        self.stream_finished.emit()



## ==> GLOBALS
counter = 0
class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Connect the send button click event to a custom method
        self.ui.send_btn.clicked.connect(self.send_user_message)
        self.ui.send_btn.clicked.connect(self.hide_download_completion_widgets)

        # Initialize the ChatThread but do not start it yet
        self.chat_thread = None

        # Connect the Enter key press event to the send_user_message method
        self.ui.input_textEdit.setAcceptRichText(True)
        self.ui.input_textEdit.installEventFilter(self)

        self.closeEvent = self.custom_close_event

        # Initialize variable to store AI response as it is streamed
        self.accumulated_ai_response = ""

    def custom_close_event(self, event):
        
        # Call the original closeEvent to handle the standard closing behavior
        super().closeEvent(event)


    def hide_download_completion_widgets(self):
        try:
            self.ui.download_compelete.setParent(None)
            self.ui.additional_label_3.setParent(None)
            self.ui.downloading.setParent(None)
            self.ui.must_download_button.setParent(None)
        except:
            pass

    def eventFilter(self, obj, event):
        if obj is self.ui.input_textEdit and event.type() == QEvent.KeyPress and event.key() == Qt.Key_Return:
            self.send_user_message()
            return True
        return super().eventFilter(obj, event)

    def send_user_message(self):
        # Get user input from the text edit
        user_input = self.ui.input_textEdit.toPlainText()

        # Display the user message immediately
        self.display_user_message(user_input)

        # Clear the accumulated AI response
        self.accumulated_ai_response = ""

        # Create a new ChatThread instance for each message
        self.chat_thread = ChatThread(user_input)
        
        # Connect the message_received signal to the display_ai_response method
        self.chat_thread.message_received.connect(self.display_ai_response)

        # Connect the stream_finished signal to finalize_ai_response method
        self.chat_thread.stream_finished.connect(self.finalize_ai_response)

        # Connect the stream_started signal to handle AI response initiation
        self.chat_thread.stream_started.connect(self.start_ai_response)

        self.hide_download_completion_widgets()

        # Start the ChatThread
        self.chat_thread.start()
    

    
    def display_user_message(self, user_input):
        # Access the QTextBrowser widget directly from the UI
        text_browser = self.ui.text_browser
        # Use resource_path to load images
        if ubuntu==True:
            user_image_path = f"{a_p}/user.png"
        else:
            user_image_path =f"./asset/user.png"

        if text_browser:
            # Insert the user's message with logo into the QTextBrowser
            user_message = f"""<img src='{user_image_path}' width='40' height='40' style='border-radius: 20px;'> <b>user:</b><br><span style='font-size: 14pt;'>{user_input}</span><br><br>"""

            text_browser.append(user_message)

            # Set the scroll bar to the maximum value
            text_browser.verticalScrollBar().setValue(text_browser.verticalScrollBar().maximum())

    def start_ai_response(self):
        # Access the QTextBrowser widget directly from the UI
        text_browser = self.ui.text_browser
        if ubuntu==True:
            queendahyun_image_path = f"{a_p}/queendahyun.png"
        else:
            queendahyun_image_path = f"./asset/queendahyun.png"


        if text_browser:

            ai_message_header = f"""<img src='{queendahyun_image_path}' width='80' height='80'  style='border-radius: 10px;'> <b>QueenDahyun:</b><br><span style='font-size: 14pt;'>"""
            text_browser.append(ai_message_header)

            # Set the scroll bar to the maximum value
            text_browser.verticalScrollBar().setValue(text_browser.verticalScrollBar().maximum())

    def display_ai_response(self, ai_response_chunk):
        # Access the QTextBrowser widget directly from the UI
        text_browser = self.ui.text_browser

        if text_browser:
            # Append each word to the QTextBrowser
            text_browser.insertPlainText(ai_response_chunk)

            # Set the scroll bar to the maximum value
            text_browser.verticalScrollBar().setValue(text_browser.verticalScrollBar().maximum())

    def finalize_ai_response(self):
        # Final update or cleanup after the streaming is finished can be handled here
        pass



# SPLASH SCREEN
class SplashScreen(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_SplashScreen()
        self.ui.setupUi(self)

        ## UI ==> INTERFACE CODES
        ########################################################################

        ## REMOVE TITLE BAR
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)


        ## DROP SHADOW EFFECT
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.ui.dropShadowFrame.setGraphicsEffect(self.shadow)

        ## QTIMER ==> START
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progress)
        # TIMER IN MILLISECONDS
        self.timer.start(35)

        # CHANGE DESCRIPTION

        # Initial Text
        self.ui.label_description.setText("<strong>WELCOME</strong> TO Advanced AI Agent")

        # Change Texts
        QtCore.QTimer.singleShot(1500, lambda: self.ui.label_description.setText("<strong>LOADING</strong> Checking Ai Model"))
        QtCore.QTimer.singleShot(3000, lambda: self.ui.label_description.setText("<strong>LOADING</strong> UI"))


        ## SHOW ==> MAIN WINDOW
        ########################################################################
        self.show()
        ## ==> END ##


    ## ==> APP FUNCTIONS
    ########################################################################
    def progress(self):
        global counter

        # SET VALUE TO PROGRESS BAR
        self.ui.progressBar.setValue(counter)

        # CLOSE SPLASH SCREE AND OPEN APP
        if counter > 10:
            # STOP TIMER
            self.timer.stop()

            # SHOW MAIN WINDOW
            self.main = MyMainWindow()
            self.main.show()

            # CLOSE SPLASH SCREEN
            self.close()

        # INCREASE COUNTER
        counter += 1


def run_additional_code():
    app = QApplication(sys.argv)
    # Create and show the SplashScreen
    window = SplashScreen()

    sys.exit(app.exec())
    


additional_code_thread = threading.Thread(target=run_additional_code)

additional_code_thread.start()
additional_code_thread.join()

