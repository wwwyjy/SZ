import requests
import json
from utils import util
from utils import config_util as cfg
from core import content_db

def question(cont, uid=0):
    contentdb = content_db.new_instance()
    if uid == 0:
        communication_history = contentdb.get_list('all','desc', 11)
    else:
        communication_history = contentdb.get_list('all','desc', 11, uid)
    message = []
    i = len(communication_history) - 1

    if len(communication_history)>1:
        while i >= 0:
            answer_info = dict()
            if communication_history[i][0] == "member":
                answer_info["role"] = "user"
                answer_info["type"] = "query"
                answer_info["content"] = communication_history[i][2]
                answer_info["content_type"] = "text"
            elif communication_history[i][0] == "fay":
                answer_info["role"] = "assistant"
                answer_info["type"] = "answer"
                answer_info["content"] = communication_history[i][2]
                answer_info["content_type"] = "text"
            message.append(answer_info)
            i -= 1
    api_url = 'https://api.coze.cn/open_api/v2/chat'
    headers = {
        'Authorization': "Bearer "+cfg.coze_api_key,
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Host': 'api.coze.cn',
        'Connection': 'keep-alive'
    }
    data = {
        "bot_id": cfg.coze_bot_id,
        "user": "user",
        "query": cont,
        "stream": False,
        "chat_history": message
    }
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            response_json = response.json()
            if response_json.get('code', 0) == 0:
                for message in response_json.get('messages', []):
                    if message.get('type') == 'answer':
                        return message.get('content')
            else:
                util.log(1, f"调用失败，请检查配置错误 {response_json.get('msg', '')}")
                response_text = "抱歉，我现在太忙了，休息一会，请稍后再试。"
                return response_text
        else:
            util.log(1, f"调用失败，请检查配置")
            response_text = "抱歉，我现在太忙了，休息一会，请稍后再试。"
            return response_text
    except Exception as e:
        util.log(1, f"调用失败，请检查配置（错误：{e}）")
        response_text = "抱歉，我现在太忙了，休息一会，请稍后再试。"
        return response_text