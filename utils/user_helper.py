import yaml
import os
import json
from typing import List, Dict, Optional, Union
from configs import SYSTEM_CONFIG

class UserHelper:
    def __init__(self):
        self.CONVERSATION_PATH  = SYSTEM_CONFIG.CONVERSATION_DIRECTORY
        os.makedirs(self.CONVERSATION_PATH, exist_ok=True)

    def save_conversation(self, user_name: str, id_request: str,
                          query: str, response: str) -> None:
        """
        Lưu cuộc hội thoại vào file json
        Args:
            user_name: str: tên người dùng
            id_request: str: id của phiên hội thoại
            query: str: câu hỏi của người dùng
            response: str: câu trả lời của chatbot
        """
        conversation_key = f"{id_request}.json"
        os.makedirs(os.path.join(self.CONVERSATION_PATH, user_name), exist_ok=True)
        user_specific_conversation = os.path.join(self.CONVERSATION_PATH, user_name, conversation_key)
        # try: 
        #     with open(user_specific_conversation, 'r', encoding='utf-8') as f:
        #         conversation = json.load(f)
        # except json.JSONDecodeError as e:
        #     print(e)
        conversation = {}

        if not conversation_key in conversation:
            conversation[conversation_key] = []
        conversation[conversation_key].append({"query": query, "response": response})

        with open(user_specific_conversation, 'a', encoding='utf-8') as f:
            json.dump(conversation, f, ensure_ascii=False, indent=2)


    def load_conversation(self, 
                          user_name: Optional[str] = None,
                          id_request: Optional[str] = None) -> Union[List, str]:
        """
        Lấy lịch sử cuộc hội thoại được lưu trữ trong file json. Lấy ra 3 cuộc hội thoại gần nhất.
        Args:
            user_name: str: tên người dùng
            seasion_id: str: id của phiên hội thoại
        Returns:
            history: List[Dict]: lịch sử cuộc hội thoại
        """
        if not user_name or not id_request:
            return ""
        else:
            conversation_key = f"{id_request}.json"
            user_specific_conversation = os.path.join(self.CONVERSATION_PATH, user_name, conversation_key)
            if os.path.exists(user_specific_conversation) and os.path.getsize(user_specific_conversation) > 0:
                try:
                    with open(user_specific_conversation, 'r', encoding='utf-8') as f:
                        conversation = json.load(f)
                        if user_name in conversation:
                            history = conversation[user_name][-3:]
                        else:
                            history = []
                except json.JSONDecodeError:
                    history = []
            else: 
                history = []

            return history