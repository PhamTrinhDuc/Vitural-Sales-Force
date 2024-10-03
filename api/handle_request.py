import random
import time
from typing import Dict, Optional, Any
from source.generate.chat_seasion import QuestionHandler
from configs import SYSTEM_CONFIG


def handle_request(
    InputText: str,
    IdRequest: str,
    UserName: str,
    NameBot:  Optional[str] = None,
    Voice: Optional[Any] = None,
    Image: Optional[Any] = None) -> Dict[str, Any]:
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
        "products": [], "terms": [], "content": "", "total_token": 0,
        "status": 200, "message": "", "time_processing": "",
    }
    try:
        if InputText not in('first_text', None, 'terms'):
             response = QuestionHandler().chat_session(input_text=InputText, id_request=IdRequest, user_name=UserName)
             results.update(**response)
            
        elif InputText == 'first_text' or InputText == None:
                results["terms"] = random.choice(SYSTEM_CONFIG.BUTTON)
                messages = SYSTEM_CONFIG.MESSAGE
                results["content"] = random.choice(messages)

        else:
            results['message'] = 'Invalid input or missing data.'
            results['status'] = 400

    except Exception as e:
        results['status'] = 500
        results['message'] = 'An error occurred while processing your request.'
        print(e)

    results['time_processing'] = f"{time.time() - start_time:.2f}s"
    return results
