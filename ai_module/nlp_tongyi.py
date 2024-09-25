"""
@Author:     
@Time:      2024/9/21 18:07
@What:      通义千问的NLP模块
"""
import time

from dashscope import Generation
from core import content_db
from utils import util
from utils import config_util as cfg


def get_response(messages):
    response = Generation.call(
        model="qwen-plus",
        messages=messages,
        api_key=cfg.tongyi_api_key,
        result_format="message",
    )
    return response


def question(cont, uid=0):
    # 获取历史记录
    history = content_db.new_instance()
    if uid == 0:
        communication_history = history.get_list('all', 'desc', 11)
    else:
        communication_history = history.get_list('all', 'desc', 11, uid=uid)
    messages = [
        {"role": "system",
         "content": "你是数字人Fay。回答之前请一步一步想清楚。对于大部分问题，请直接回答并提供有用和准确的信息。"}
    ]
    i = len(communication_history) - 1

    if len(communication_history) > 1:
        while i >= 0:
            answer_info = dict()
            if communication_history[i][0] == "member":
                answer_info["role"] = "user"
                answer_info["content"] = communication_history[i][2]
            elif communication_history[i][0] == "fay":
                answer_info["role"] = "assistant"
                answer_info["content"] = communication_history[i][2]
            messages.append(answer_info)
            i -= 1
    else:
        answer_info = dict()
        answer_info["role"] = "user"
        answer_info["content"] = cont
        messages.append(answer_info)
    start_time = time.time()
    response = get_response(messages)
    end_time = time.time()
    response_text = response.output.choices[0].message.content
    if response.status_code != 200:
        print(f"请求错误：{response.message}")
        response_text = "抱歉，我现在太忙了，休息一会儿再试试吧。"
    util.log(1, "接口调用耗时 :" + str(end_time - start_time))
    return response_text
