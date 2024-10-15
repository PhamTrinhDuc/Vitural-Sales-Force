import random
import time
import json
import os
from typing import Dict, Optional
from source.generate.chat_seasion import Pipeline
from utils.utils_pipeline import HelperPiline
from configs import SYSTEM_CONFIG

HELPER = HelperPiline()


def handle_request(
    InputText: None,
    IdRequest: None,
    NameBot: None,
    UserName: None,
    Image: None,
    Voice: None,
    PhoneNumber: None,
    Address: None,):
    """

    Hàm chính để tương tác với người dùng, dựa vào query, user_name, seasion_id của người dùng, đưa qua pipeline và trả về câu trả lời.
    Args:
        - query: câu hỏi của người dùng
        - user_name: tên người dùng
        - seasion_id: id cuộc hội thoại của người dùng.
    Returns:
        - trả về câu trả lời cho người dùng.
    """
    
    start_time = time.time()
    results = {
        "products": [], 'product_confirms': [], "terms": [], "content": "",
        "status": 200, "message": "", "time_processing": "",
    }
    Users = {
        "phone_number": PhoneNumber,
        "name": UserName,
    }
    try:
        if InputText not in("terms", 'first_text', None):
            response = Pipeline().chat_session(InputText=InputText, IdRequest=IdRequest, NameBot=NameBot, Voice=Voice, Image=Image, UserInfor=Users)
            results.update(**response)
            
        elif InputText == 'first_text' or InputText == None:
            results["terms"] = SYSTEM_CONFIG.BUTTON
            results["content"] = random.choice(SYSTEM_CONFIG.MESSAGE)
        else:
            results['message'] = 'Invalid input or missing data.'
            results['status'] = 400

    except Exception as e:
        results['status'] = 500
        results['content'] = 'Hệ thống hiện đang bảo trì, anh chị vui lòng quay lại sau.'
        results['message'] = str(e)

    results['time_processing'] = f"{time.time() - start_time:.2f}s"
    return results


def handle_title_conversation(phone_number: None) -> dict:
    data = {"data": [], "status": 200, "message": None}
    try:
        user_specific_conversation = os.path.join(SYSTEM_CONFIG.CONVERSATION_STORAGE, phone_number)
        for session_path in os.listdir(user_specific_conversation):
            session_conv_path = os.path.join(user_specific_conversation, session_path)
            with open(session_conv_path, mode='r', encoding='utf-8') as f:
                conversation = json.load(f)
            session_id = list(conversation.keys())[0]
            title = conversation[session_id][0]['human']
            data['data'].append({"session_id": session_id, "title": title})
        data['message'] = "Get conversation title successfull!"
    except Exception as e:
        data['status'] = 500
        data['message'] = "Error - HANDLE TITLE CONVERSATION: " + str(e)
        
    return data


def handle_conversation(phone_number: None, session_id: None) -> dict:
    data = {"data": None, "status": 200, "message": None}
    try:
        session_conv_path = os.path.join(SYSTEM_CONFIG.CONVERSATION_STORAGE, phone_number, session_id + '.json')
        with open(session_conv_path, mode='r', encoding='utf-8') as f:
                conversation = json.load(f)
        
        data['data'] = conversation[session_id]
        data['message'] = "Get conversation successfull!"
    except Exception as e:
        data['status'] = 500
        data['message'] = "Error - HANDLE CONVERSATION: " + str(e)
    return data

if __name__ == "__main__":
    data = handle_title_conversation("088695868")
    print(data)
            
    
    
    