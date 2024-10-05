import random
import time
from typing import Dict, Optional
from source.generate.chat_seasion import Pipeline
from configs import SYSTEM_CONFIG


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
        "products": [], "terms": [], "content": "",
        "status": 200, "message": "", "time_processing": "",
    }
    Users = {
        "phone_number": PhoneNumber,
        "address": Address,
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
        results['message'] = 'An error occurred while processing your request.'
        print(e)

    results['time_processing'] = f"{time.time() - start_time:.2f}s"
    return results