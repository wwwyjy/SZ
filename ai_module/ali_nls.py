from threading import Thread

import websocket
import json
import time
import ssl
import _thread as thread
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

from core import wsa_server
from scheduler.thread_manager import MyThread
from utils import util
from utils import config_util as cfg
from core.authorize_tb import Authorize_Tb

__running = True
__my_thread = None
_token = ''


def __post_token():
    global _token
    __client = AcsClient(
        cfg.key_ali_nls_key_id,
        cfg.key_ali_nls_key_secret,
        "cn-shanghai"
    )

    __request = CommonRequest()
    __request.set_method('POST')
    __request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
    __request.set_version('2019-02-28')
    __request.set_action_name('CreateToken')
    info = json.loads(__client.do_action_with_exception(__request))
    _token = info['Token']['Id']
    authorize = Authorize_Tb()
    authorize_info = authorize.find_by_userid(cfg.key_ali_nls_key_id)
    if authorize_info is not None:
       authorize.update_by_userid(cfg.key_ali_nls_key_id, _token, info['Token']['ExpireTime']*1000)
    else:
       authorize.add(cfg.key_ali_nls_key_id, _token, info['Token']['ExpireTime']*1000) 

def __runnable():
    while __running:
        __post_token()
        time.sleep(60 * 60 * 12)


def start():
    MyThread(target=__runnable).start()


class ALiNls:
    # 初始化
    def __init__(self, username):
        self.__URL = 'wss://nls-gateway-cn-shenzhen.aliyuncs.com/ws/v1'
        self.__ws = None
        self.__connected = False
        self.__frames = []
        self.__state = 0
        self.__closing = False
        self.__task_id = ''
        self.done = False
        self.finalResults = ""
        self.username = username

    def __create_header(self, name):
        if name == 'StartTranscription':
            self.__task_id = util.random_hex(32)
        header = {
            "appkey": cfg.key_ali_nls_app_key,
            "message_id": util.random_hex(32),
            "task_id": self.__task_id,
            "namespace": "SpeechTranscriber",
            "name": name
        }
        return header

    # 收到websocket消息的处理
    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            header = data['header']
            name = header['name']
            if name == 'SentenceEnd':
                self.done = True
                self.finalResults = data['payload']['result']
                wsa_server.get_web_instance().add_cmd({"panelMsg": self.finalResults, "Username" : self.username})
                if not cfg.config["interact"]["playSound"]: # 非展板播放
                    content = {'Topic': 'Unreal', 'Data': {'Key': 'log', 'Value': self.finalResults}, 'Username' : self.username}
                    wsa_server.get_instance().add_cmd(content)
                ws.close()#TODO
            elif name == 'TranscriptionResultChanged':
                self.finalResults = data['payload']['result']
                wsa_server.get_web_instance().add_cmd({"panelMsg": self.finalResults, "Username" : self.username})
                if not cfg.config["interact"]["playSound"]: # 非展板播放
                    content = {'Topic': 'Unreal', 'Data': {'Key': 'log', 'Value': self.finalResults}, 'Username' : self.username}
                    wsa_server.get_instance().add_cmd(content)

        except Exception as e:
            print(e)
        # print("### message:", message)
        if self.__closing:
            try:
                self.__ws.close()
            except Exception as e:
                print(e)

    # 收到websocket的关闭要求
    def on_close(self, ws, code, msg):
        self.__connected = False
        # print("### CLOSE:", msg)

    # 收到websocket错误的处理
    def on_error(self, ws, error):
        print("### error:", error)

    # 收到websocket连接建立的处理
    def on_open(self, ws):
        self.__connected = True
        #为了兼容多路asr，关闭过程数据
        def run(*args):
            while self.__connected:
                try:
                    if len(self.__frames) > 0:
                        frame = self.__frames[0]

                        self.__frames.pop(0)
                        if type(frame) == dict:
                            ws.send(json.dumps(frame))
                        elif type(frame) == bytes:
                            ws.send(frame, websocket.ABNF.OPCODE_BINARY)
                        #print('发送 ------> ' + str(type(frame)))
                except Exception as e:
                    print(e)
                time.sleep(0.0001)

        thread.start_new_thread(run, ())

    def __connect(self):
        self.finalResults = ""
        self.done = False
        self.__frames.clear()
        self.__ws = websocket.WebSocketApp(self.__URL + '?token=' + _token, on_message=self.on_message)
        self.__ws.on_open = self.on_open
        self.__ws.on_error = self.on_error
        self.__ws.on_close = self.on_close
        self.__ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    def send(self, buf):
        self.__frames.append(buf)

    def start(self):
        Thread(target=self.__connect, args=[]).start()
        data = {
            'header': self.__create_header('StartTranscription'),
            "payload": {
                "format": "pcm",
                "sample_rate": 16000,
                "enable_intermediate_result": True,
                "enable_punctuation_prediction": False,
                "enable_inverse_text_normalization": True,
                "speech_noise_threshold": -1
            }
        }
        self.send(data)

    def end(self):
        if self.__connected:
            try:
                for frame in self.__frames:
                    self.__frames.pop(0)
                    if type(frame) == dict:
                        self.__ws.send(json.dumps(frame))
                    elif type(frame) == bytes:
                        self.__ws.send(frame, websocket.ABNF.OPCODE_BINARY)
                    time.sleep(0.0001)
                self.__frames.clear()
                frame = {"header": self.__create_header('StopTranscription')}
                self.__ws.send(json.dumps(frame))
            except Exception as e:
                print(e)
        self.__closing = True
        self.__connected = False
