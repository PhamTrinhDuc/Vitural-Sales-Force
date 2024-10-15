import yaml
import re
import logging
import os
import json
from typing import List, Dict, Union
from configs import SYSTEM_CONFIG


class UserHelper:
    def __init__(self):
        self.CONVERSATION_PATH  = SYSTEM_CONFIG.CONVERSATION_STORAGE
        self.INFO_USER_PATH = SYSTEM_CONFIG.INFO_USER_STORAGE
        os.makedirs(self.CONVERSATION_PATH, exist_ok=True)
        os.makedirs(self.INFO_USER_PATH, exist_ok=True)
        
    def _clean_html(self, html_text: str) -> str:
        """
        Xóa các thẻ html từ phần output của chatbot
        Args:
            html_text: str: phần trả lời của bot sau khi đã format sang html
        Returns:
            clean_text: str: phần trả lời của bot sau khi đã xóa các thẻ html
        """
        clean_text = re.sub(r'<[^>]+>', '', html_text)
        clean_text = re.sub(r'\n+', '\n', clean_text)
        clean_text = clean_text.strip()
        return clean_text
    
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
            json.dump(users, f, ensure_ascii=False, indent=2)
    
    def save_conversation(self, phone_number: str, id_request: str,
                          query: str, response: str) -> None:
        """
        Lưu cuộc hội thoại mới vào file json
        Args:
            user_name: str: tên người dùng
            season_id: str: id của phiên hội thoại
            query: str: câu hỏi của người dùng
            response: str: câu trả lời của chatbot
        """
        conversation_key = f"{id_request}.json"
        os.makedirs(os.path.join(self.CONVERSATION_PATH, phone_number), exist_ok=True)
        user_specific_conversation = os.path.join(self.CONVERSATION_PATH, phone_number, conversation_key)
        
        # mở file đã lưu lịch sử trò chuyện
        if os.path.exists(user_specific_conversation) and os.path.getsize(user_specific_conversation) > 0:
            with open(user_specific_conversation, mode='r', encoding='utf-8') as f:
                conversation = json.load(f)
        else:
            conversation = {}

        # lưu lại cuộc trò chuyện mới vào file json
        if not id_request in conversation:
            conversation[id_request] = []
        conversation[id_request].append({"human": query, "ai": response})

        with open(user_specific_conversation, mode='w', encoding='utf-8') as f:
            json.dump(conversation, f, ensure_ascii=False, indent=2)


    def load_conversation(self, conv_user: str, id_request: str) -> str:
        """
        Lấy lịch sử cuộc hội thoại được lưu trữ trong file json. Lấy ra 3 cuộc hội thoại gần nhất.
        Args:
            user_name: str: tên người dùng
            seasion_id: str: id của phiên hội thoại
        Returns:
            history: List[Dict]: lịch sử cuộc hội thoại
        """
        if not conv_user or not id_request:
            return []
        else:
            history = []
            conversation_key = f"{id_request}.json"
            os.makedirs(os.path.join(self.CONVERSATION_PATH, conv_user), exist_ok=True)
            user_specific_conversation = os.path.join(self.CONVERSATION_PATH, conv_user, conversation_key)
            if os.path.exists(user_specific_conversation) and os.path.getsize(user_specific_conversation) > 0:
                try:
                    with open(user_specific_conversation, 'r') as f:
                        conversation = json.load(f)
                        if id_request in conversation:
                            conversation =  conversation[id_request][-SYSTEM_CONFIG.TOP_CONVERSATION:]
                            for conv in conversation:
                                conv['human'] = self._clean_html(conv['human'])
                                conv['ai'] = self._clean_html(conv['ai'])
                            return conversation
                        else:
                            return []
                except json.JSONDecodeError as e :
                    logging.ERROR("LOAD CONVERSATION ERROR: ", e)
                    return []
            else: 
                return []