import yaml
import os
import json
from typing import List, Dict, Optional, Union
from configs import SYSTEM_CONFIG

class UserHelper:
    def __init__(self):
        self.CONVERSATION_PATH  = SYSTEM_CONFIG.CONVERSATION_STORAGE
        self.INFO_USER_PATH = SYSTEM_CONFIG.INFO_USER_STORAGE
        os.makedirs(self.CONVERSATION_PATH, exist_ok=True)
        os.makedirs(self.INFO_USER_PATH, exist_ok=True)

    def get_user_info(self, phone_number: str) -> Dict:
        """
        Hàm để load thông tin người dùng từ file yaml
        """
        user_info_specific = os.path.join(self.INFO_USER_PATH, f"{phone_number}.json")
        if os.path.exists(user_info_specific) and os.path.getsize(user_info_specific) > 0:
            with open(user_info_specific, "r") as f:
                user_data = yaml.safe_load(f)
        else:
            user_data = {}
        return user_data


    def save_users(self, users: Dict[str, str]) -> None:
        """
        Hàm để lưu thông tin người dùng vào file yaml
        """
        user_info_specific = os.path.join(self.INFO_USER_PATH, f"{users['phone_number']}.json")
        with open(user_info_specific, "w") as f:
            yaml.dump(users, f)


    def save_conversation(self, phone_number: str, id_request: str,
                          query: str, response: str) -> None:
        """
        Lưu cuộc hội thoại vào file json
        Args:
            user_name: str: tên người dùng
            season_id: str: id của phiên hội thoại
            query: str: câu hỏi của người dùng
            response: str: câu trả lời của chatbot
        """
        conversation_key = f"{id_request}.json"
        os.makedirs(os.path.join(self.CONVERSATION_PATH, phone_number), exist_ok=True)
        user_specific_conversation = os.path.join(self.CONVERSATION_PATH, phone_number, conversation_key)
        # try: 
        #     with open(user_specific_conversation, 'r', encoding='utf-8') as f:
        #         conversation = json.load(f)
        # except json.JSONDecodeError as e:
        #     print(e)
        conversation = {}

        if not id_request in conversation:
            conversation[id_request] = []
        conversation[id_request].append({"query": query, "response": response})

        with open(user_specific_conversation, 'a', encoding='utf-8') as f:
            json.dump(conversation, f, ensure_ascii=False, indent=2)


    def load_conversation(self, phone_number: str, id_request: str) -> Union[List, str]:
        """
        Lấy lịch sử cuộc hội thoại được lưu trữ trong file json. Lấy ra 3 cuộc hội thoại gần nhất.
        Args:
            user_name: str: tên người dùng
            seasion_id: str: id của phiên hội thoại
        Returns:
            history: List[Dict]: lịch sử cuộc hội thoại
        """
        if not phone_number:
            return ""
        else:
            conversation_key = f"{id_request}.json"
            os.makedirs(os.path.join(self.CONVERSATION_PATH, phone_number), exist_ok=True)
            user_specific_conversation = os.path.join(self.CONVERSATION_PATH, phone_number, conversation_key)
            if os.path.exists(user_specific_conversation) and os.path.getsize(user_specific_conversation) > 0:
                try:
                    with open(user_specific_conversation, 'r', encoding='utf-8') as f:
                        conversation = json.load(f)
                        if id_request in conversation:
                            history = conversation[id_request][-3:]
                        else:
                            history = []
                except json.JSONDecodeError:
                    history = []
            else: 
                history = []

            return history
