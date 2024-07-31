import importlib
import json
import time

import pyaudio
from flask import Flask, render_template, request
from flask_cors import CORS

import fay_booter

from core import tts_voice
from gevent import pywsgi
from scheduler.thread_manager import MyThread
from utils import config_util, util
from core import wsa_server
from core import fay_core
from core import content_db
from ai_module import yolov8


__app = Flask(__name__)
CORS(__app, supports_credentials=True)


def __get_template():
    return render_template('index.html')


def __get_device_list():
    audio = pyaudio.PyAudio()
    device_list = []
    for i in range(audio.get_device_count()):
        devInfo = audio.get_device_info_by_index(i)
        if devInfo['hostApi'] == 0:
            device_list.append(devInfo["name"])
    
    return list(set(device_list))


@__app.route('/api/submit', methods=['post'])
def api_submit():
    data = request.values.get('data')
    config_data = json.loads(data)
    if(config_data['config']['source']['record']['enabled']):
        config_data['config']['source']['record']['channels'] = 0
        audio = pyaudio.PyAudio()
        for i in range(audio.get_device_count()):
            devInfo = audio.get_device_info_by_index(i)
            if devInfo['name'].find(config_data['config']['source']['record']['device']) >= 0 and devInfo['hostApi'] == 0:
                 config_data['config']['source']['record']['channels'] = devInfo['maxInputChannels']

    config_util.save_config(config_data['config'])

    return '{"result":"successful"}'

@__app.route('/api/control-eyes', methods=['post'])
def control_eyes():
    eyes = yolov8.new_instance()
    if(not eyes.get_status()):
       eyes.start()
       util.log(1, "YOLO v8正在启动...")
    else:
       eyes.stop()
       util.log(1, "YOLO v8正在关闭...")
    return '{"result":"successful"}'


@__app.route('/api/get-data', methods=['post'])
def api_get_data():
    config_data = config_util.config
    if  wsa_server.new_instance().isConnect:
        config_data['interact']['playSound'] = False
    else:
        config_data['interact']['playSound'] = True
    config_util.save_config(config_data)
    voice_list = tts_voice.get_voice_list()
    send_voice_list = []
    if config_util.tts_module == 'ali':
        wsa_server.get_web_instance().add_cmd({
        "voiceList": [
            {"id": "abin", "name": "阿斌"},
            {"id": "zhixiaobai", "name": "知小白"},
            {"id": "zhixiaoxia", "name": "知小夏"},
            {"id": "zhixiaomei", "name": "知小妹"},
            {"id": "zhigui", "name": "知柜"},
            {"id": "zhishuo", "name": "知硕"},
            {"id": "aixia", "name": "艾夏"},
            {"id": "zhifeng_emo", "name": "知锋_多情感"},
            {"id": "zhibing_emo", "name": "知冰_多情感"},
            {"id": "zhimiao_emo", "name": "知妙_多情感"},
            {"id": "zhimi_emo", "name": "知米_多情感"},
            {"id": "zhiyan_emo", "name": "知燕_多情感"},
            {"id": "zhibei_emo", "name": "知贝_多情感"},
            {"id": "zhitian_emo", "name": "知甜_多情感"},
            {"id": "xiaoyun", "name": "小云"},
            {"id": "xiaogang", "name": "小刚"},
            {"id": "ruoxi", "name": "若兮"},
            {"id": "siqi", "name": "思琪"},
            {"id": "sijia", "name": "思佳"},
            {"id": "sicheng", "name": "思诚"},
            {"id": "aiqi", "name": "艾琪"},
            {"id": "aijia", "name": "艾佳"},
            {"id": "aicheng", "name": "艾诚"},
            {"id": "aida", "name": "艾达"},
            {"id": "ninger", "name": "宁儿"},
            {"id": "ruilin", "name": "瑞琳"},
            {"id": "siyue", "name": "思悦"},
            {"id": "aiya", "name": "艾雅"},
            {"id": "aimei", "name": "艾美"},
            {"id": "aiyu", "name": "艾雨"},
            {"id": "aiyue", "name": "艾悦"},
            {"id": "aijing", "name": "艾婧"},
            {"id": "xiaomei", "name": "小美"},
            {"id": "aina", "name": "艾娜"},
            {"id": "yina", "name": "伊娜"},
            {"id": "sijing", "name": "思婧"},
            {"id": "sitong", "name": "思彤"},
            {"id": "xiaobei", "name": "小北"},
            {"id": "aitong", "name": "艾彤"},
            {"id": "aiwei", "name": "艾薇"},
            {"id": "aibao", "name": "艾宝"},
            {"id": "shanshan", "name": "姗姗"},
            {"id": "chuangirl", "name": "小玥"},
            {"id": "lydia", "name": "Lydia"},
            {"id": "aishuo", "name": "艾硕"},
            {"id": "qingqing", "name": "青青"},
            {"id": "cuijie", "name": "翠姐"},
            {"id": "xiaoze", "name": "小泽"},
            {"id": "zhimao", "name": "知猫"},
            {"id": "zhiyuan", "name": "知媛"},
            {"id": "zhiya", "name": "知雅"},
            {"id": "zhiyue", "name": "知悦"},
            {"id": "zhida", "name": "知达"},
            {"id": "zhistella", "name": "知莎"},
            {"id": "kelly", "name": "Kelly"},
            {"id": "jiajia", "name": "佳佳"},
            {"id": "taozi", "name": "桃子"},
            {"id": "guijie", "name": "柜姐"},
            {"id": "stella", "name": "Stella"},
            {"id": "stanley", "name": "Stanley"},
            {"id": "kenny", "name": "Kenny"},
            {"id": "rosa", "name": "Rosa"},
            {"id": "mashu", "name": "马树"},
            {"id": "xiaoxian", "name": "小仙"},
            {"id": "yuer", "name": "悦儿"},
            {"id": "maoxiaomei", "name": "猫小美"},
            {"id": "aifei", "name": "艾飞"},
            {"id": "yaqun", "name": "亚群"},
            {"id": "qiaowei", "name": "巧薇"},
            {"id": "dahu", "name": "大虎"},
            {"id": "ailun", "name": "艾伦"},
            {"id": "jielidou", "name": "杰力豆"},
            {"id": "laotie", "name": "老铁"},
            {"id": "laomei", "name": "老妹"},
            {"id": "aikan", "name": "艾侃"}
        ]
    })
    else:
        voice_list = tts_voice.get_voice_list()
        send_voice_list = []
        for voice in voice_list: 
            voice_data = voice.value 
            send_voice_list.append({"id": voice_data['name'], "name": voice_data['name']})
        wsa_server.get_web_instance().add_cmd({
            "voiceList": send_voice_list
        })
    wsa_server.get_web_instance().add_cmd({"deviceList": __get_device_list()})
    return json.dumps({'config': config_util.config})


@__app.route('/api/start-live', methods=['post'])
def api_start_live():
    # time.sleep(5)
    fay_booter.start()
    time.sleep(1)
    wsa_server.get_web_instance().add_cmd({"liveState": 1})
    return '{"result":"successful"}'


@__app.route('/api/stop-live', methods=['post'])
def api_stop_live():
    # time.sleep(1)
    fay_booter.stop()
    time.sleep(1)
    wsa_server.get_web_instance().add_cmd({"liveState": 0})
    return '{"result":"successful"}'

@__app.route('/api/send', methods=['post'])
def api_send():
    data = request.values.get('data')
    info = json.loads(data)
    fay_core.send_for_answer(info['msg'])
    return '{"result":"successful"}'

@__app.route('/api/get-msg', methods=['post'])
def api_get_Msg():
    contentdb = content_db.new_instance()
    list = contentdb.get_list('all','desc',1000)
    relist = []
    i = len(list)-1
    while i >= 0:
        relist.append(dict(type=list[i][0], way=list[i][1], content=list[i][2], createtime=list[i][3], timetext=list[i][4]))
        i -= 1

    return json.dumps({'list': relist})

@__app.route('/v1/chat/completions', methods=['post'])
@__app.route('/api/send/v1/chat/completions', methods=['post'])
def api_send_v1_chat_completions():
    data = request.json  # 解析JSON数据
    last_content = ""
    if 'messages' in data and data['messages']:
        last_message = data['messages'][-1]  # 获取最后一条消息
        last_content = last_message.get('content', 'No content provided')  # 获取'content'字段
    else:
        last_content = 'No messages found'
    text = fay_core.send_for_answer(last_content)
    return {
  "id": "chatcmpl-8jqorq6Fw1Vi5XoH7pddGGpQeuPe0",
  "object": "chat.completion",
  "created": 1705938489,
  "model": "fay-agent",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": text
      },
      "logprobs": "",
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": len(last_content),
    "completion_tokens": len(text),
    "total_tokens": len(last_content) + len(text)
  },
  "system_fingerprint": "fp_04de91a479"
}

@__app.route('/', methods=['get'])
def home_get():
    return __get_template()


@__app.route('/', methods=['post'])
def home_post():
    return __get_template()

def run():
    server = pywsgi.WSGIServer(('0.0.0.0',5000), __app)
    server.serve_forever()

def start():
    MyThread(target=run).start()
