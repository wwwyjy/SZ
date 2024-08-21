import os
import sys
from io import BytesIO
from utils import config_util
config_util.load_config()
if config_util.start_mode == 'common':
    from PyQt5 import QtGui
    from PyQt5.QtWidgets import QApplication

from ai_module import ali_nls

if config_util.key_chat_module == 'langchain':
    from ai_module import nlp_langchain
if config_util.key_chat_module == 'privategpt':    
    from ai_module import nlp_privategpt
from core import wsa_server
from gui import flask_server
from gui.window import MainWindow

from scheduler.thread_manager import MyThread
from core import content_db
import sys
sys.setrecursionlimit(sys.getrecursionlimit() * 5)
import hashlib
import os
import time


def __clear_samples():
    if not os.path.exists("./samples"):
        os.mkdir("./samples")
    for file_name in os.listdir('./samples'):
        if file_name.startswith('sample-'):
            os.remove('./samples/' + file_name)


def __clear_songs():
    if not os.path.exists("./songs"):
        os.mkdir("./songs")
    for file_name in os.listdir('./songs'):
        if file_name.endswith('.mp3'):
            os.remove('./songs/' + file_name)

def __clear_logs():
    if not os.path.exists("./logs"):
        os.mkdir("./logs")
    for file_name in os.listdir('./logs'):
        if file_name.endswith('.log'):
            os.remove('./logs/' + file_name)
           


if __name__ == '__main__':
    __clear_samples()
    __clear_songs()
    __clear_logs()
    config_util.load_config()
    contentdb = content_db.new_instance()
    contentdb.init_db()     
    ws_server = wsa_server.new_instance(port=10002)
    ws_server.start_server()
    web_ws_server = wsa_server.new_web_instance(port=10003)
    web_ws_server.start_server()
    #Edit by xszyou in 20230516:增加本地asr后，aliyun调成可选配置
    if config_util.ASR_mode == "ali":
        ali_nls.start()
    flask_server.start() 
    if config_util.key_chat_module == 'langchain':
        nlp_langchain.save_all()
    if config_util.key_chat_module == 'privategpt':
        nlp_privategpt.save_all()
    if config_util.start_mode == 'common':    
        app = QApplication(sys.argv)
        app.setWindowIcon(QtGui.QIcon('icon.png'))
        win = MainWindow()
        time.sleep(1)
        win.show()
        app.exit(app.exec_())
    else:
        while True:
            time.sleep(1) 

    

    
