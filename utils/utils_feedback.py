import os
import json
from configs.config_system import LoadConfig
class UserFeedback:
    def __init__(self):
        self.FEEDBACK_STORAGE  = LoadConfig.FEEDBACK_STORAGE
        os.makedirs(self.FEEDBACK_STORAGE, exist_ok=True)
    def save_conversation(self, phone_number: str, id_request: str,
                        query: str, response: str, rating: float = None, 
                        feedback: str = None) -> None:
        """
        Lưu cuộc hội thoại mới vào file json
        Args:
            user_name: str: tên người dùng
            season_id: str: id của phiên hội thoại
            query: str: câu hỏi của người dùng
            response: str: câu trả lời của chatbot
            rating: float: điểm đánh giá (tùy chọn)
            feedback: str: nội dung góp ý (tùy chọn)
        """
        conversation_key = f"{id_request}.json"
        os.makedirs(os.path.join(self.FEEDBACK_STORAGE, phone_number), exist_ok=True)
        user_specific_conversation = os.path.join(self.FEEDBACK_STORAGE, phone_number, conversation_key)
        
        # mở file đã lưu lịch sử trò chuyện
        if os.path.exists(user_specific_conversation) and os.path.getsize(user_specific_conversation) > 0:
            with open(user_specific_conversation, mode='r', encoding='utf-8') as f:
                conversation = json.load(f)
        else:
            conversation = {}

        # lưu lại cuộc trò chuyện mới vào file json
        if not id_request in conversation:
            conversation[id_request] = []
        
        conversation_data = {
            "human": query, 
            "ai": response,
            "rating": rating if rating is not None else "",
            "feedback": feedback if feedback else ""
        }
            
        conversation[id_request].append(conversation_data)

        with open(user_specific_conversation, mode='w', encoding='utf-8') as f:
            json.dump(conversation, f, ensure_ascii=False, indent=2)