import random
import time
from typing import Dict, Optional, Any
from source.generate.chat_seasion import Pipline
from utils.postgres_connecter.postgres_logger import PostgresHandler
from configs import SYSTEM_CONFIG

DB_LOGGER = PostgresHandler()


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
             response = Pipline().chat_session(input_text=InputText, id_request=IdRequest, user_name=UserName)
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
        results['message'] = f'An error occurred while processing your request. ERROR: {str(e)}'

    results['time_processing'] = f"{time.time() - start_time:.2f}s"

    DB_LOGGER.insert_data(
        user_name=UserName, 
        session_id=IdRequest, 
        total_token=results['total_token'],
        status=results['status'], 
        error_message=results['message'],
        human_chat=InputText, 
        bot_chat=results['content'],
        time_request=results['time_processing'],
        toal_cost=results['cost']
    )
    
    return results
