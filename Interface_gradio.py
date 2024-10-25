import gradio as gr
from typing import Dict, Optional
import random
import time
import uuid
import logging
import datetime
from configs import SYSTEM_CONFIG
from api.handle_request import handle_request
from utils.utils_feedback import UserFeedback

# Configure logging
logging.basicConfig(
    filename='feedback.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

class ChatBot:
    def __init__(self):
        self.user_sessions = {}  # Dictionary to store user-specific data
        self.greetings = [
            "Chào mừng anh/chị đã tin tưởng mua sắm tại Viettel. Em là Phương Nhi, trợ lý tư vấn bán hàng tại VCC luôn ở đây để hỗ trợ và tư vấn mua sắm. Có phải anh chị đang có nhu cầu tìm hiểu, mua sắm phải không? Vậy hãy cho em biết mình cần tìm sản phẩm nào và với ngân sách bao nhiêu ạ! Chúc anh/chị một ngày rực rỡ và thành công! 🌈",
            "Xin chào! Em là Phương Nhi, trợ lý mua sắm tại VCC sẵn sàng tư vấn cho anh/chị về sản phẩm bên em. Có phải anh chị đang có nhu cầu mua sắm phải không ạ. Anh/chị có thể cho em biết gia đình đang cần mua sản phẩm gì không ạ?",
            "Chào anh/chị! Em là Phương Nhi - trợ lý mua sắm sẵn sàng hỗ trợ cho anh/chị ạ. Chúc anh/chị một ngày tốt lành và mua sắm vui vẻ ạ!"
        ]
        self.last_response = ""
        self.rated_responses = {}
        self.current_session_id = str(uuid.uuid4())
        self.pending_rating = False
        self.feedback_logger = UserFeedback()

    def get_user_session(self, phone_number):
        if phone_number not in self.user_sessions:
            self.user_sessions[phone_number] = {
                'chat_history': [],
                'last_response': "",
                'rated_responses': {},
                'session_id': str(uuid.uuid4()),
                'pending_rating': False
            }
        return self.user_sessions[phone_number]

    def validate_chat_preconditions(self, user_name, phone_number, address):
        if not user_name or not phone_number or not address:
            raise gr.Error("Vui lòng nhập đầy đủ thông tin (Tên, Số điện thoại, Địa chỉ) trước khi chat!")
        if not phone_number.isdigit() or len(phone_number) < 10:
            raise gr.Error("Số điện thoại không hợp lệ!")
        
        session = self.get_user_session(phone_number)
        if session['pending_rating']:
            raise gr.Error("Vui lòng đánh giá câu trả lời trước khi tiếp tục!")

    def log_feedback(self, rating, phone_number, feedback_text="", user_info=None):
        session = self.get_user_session(phone_number)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "session_id": session['session_id'],
            "rating": rating,
            "feedback": feedback_text,
            "last_response": session['last_response'],
            "user_info": user_info
        }
        logging.info(log_entry)

    def chat(self, message, history, id_request, phone_number, address, user_name, name_bot=None, image=None, voice=None):
        self.validate_chat_preconditions(user_name, phone_number, address)
        session = self.get_user_session(phone_number)

        if not message or message.strip() == "":
            bot_message = random.choice(self.greetings)
            session['last_response'] = bot_message
            session['chat_history'].append(("", bot_message))
            session['pending_rating'] = True
            return "", session['chat_history']

        input_text = message
        
        users = {
            "phone_number": phone_number,
            "name": user_name,
        }

        response = handle_request(
            InputText=input_text,
            IdRequest=id_request,
            NameBot=name_bot,
            UserName=user_name,
            Image=image,
            Voice=voice,
            MemberCode="NORMAL",
            PhoneNumber=phone_number,
            Address=address
        )

        bot_message = response.get("content", "")
        if response.get("terms"):
            bot_message += "\n\nTerms: " + ", ".join(response.get("terms"))
        
        session['last_response'] = bot_message
        session['chat_history'].append((message, bot_message))
        session['pending_rating'] = True
        
        return "", session['chat_history']

    def rate_response(self, rating, phone_number, feedback_text="", user_info=None):
        session = self.get_user_session(phone_number)
        if session['last_response']:
            session['rated_responses'][session['last_response']] = rating
            self.log_feedback(rating, phone_number, feedback_text, user_info)
            
            if user_info and 'phone' in user_info:
                self.feedback_logger.save_conversation(
                    phone_number=user_info['phone'],
                    id_request=session['session_id'],
                    query=session['chat_history'][-1][0] if session['chat_history'] else "",
                    response=session['last_response'],
                    rating=rating,
                    feedback=feedback_text
                )
            
            if session['chat_history']:
                last_exchange = session['chat_history'][-1]
                feedback_display = last_exchange[1].split('\n[Đánh giá:')[0]
                session['chat_history'][-1] = (last_exchange[0], feedback_display)
                session['pending_rating'] = False
        return session['chat_history']

    def clear_chat(self, phone_number):
        if phone_number in self.user_sessions:
            self.user_sessions[phone_number] = {
                'chat_history': [],
                'last_response': "",
                'rated_responses': {},
                'session_id': str(uuid.uuid4()),
                'pending_rating': False
            }
        return None

chatbot = ChatBot()

with gr.Blocks(css="""
    #chatbot { 
        height: 400px; 
        overflow-y: auto; 
        border: 1px solid #ddd; 
        border-radius: 15px; 
        padding: 20px;
        background-color: #f7f7f7;
    }
    .user, .bot { 
        padding: 10px 15px; 
        border-radius: 20px; 
        margin: 5px;
    }
    .user { 
        background-color: #FF6347; 
        color: black;
    }
    .bot { 
        background-color: #F0F8FF; 
        color: black;
    }
    .rating-buttons {
        display: flex;
        gap: 10px;
        margin-top: 10px;
    }
    .rating-feedback-section {
        margin-top: 10px;
        padding: 15px;
        border: 1px solid #ddd;
        border-radius: 5px;
        background-color: #f9f9f9;
    }
    .rating-group {
        margin-bottom: 10px;
    }
    .error-message {
        color: red;
        font-size: 0.9em;
        margin-top: 5px;
    }
    .alert {
        color: red;
        font-weight: bold;
        padding: 10px;
        margin: 10px 0;
        border: 1px solid red;
        border-radius: 5px;
        background-color: #ffe6e6;
    }
    .rating-submit-btn {
        background-color: #FF8C00 !important;
        color: black !important;
        border: none !important;
        padding: 10px 20px !important;
        margin-left: 5px !important;
        margin-right: 5px !important;
        border-radius: 5px !important;
        font-weight: bold !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
        transition: all 0.3s ease !important;
    }
    .rating-submit-btn:hover {
        background-color: #FF6347 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }
""") as demo:
    gr.Markdown(
        """
        # 💬 Chatbot Vitural Sales Force
        Hãy điền thông tin trước khi đặt câu hỏi và đánh giá sau khi có câu trả lời để giúp Chatbot cải thiện hơn nhé!
        """
    )
    
    with gr.Row():
        with gr.Column(scale=3):
            chatbot_interface = gr.Chatbot(elem_id="chatbot",
                                         avatar_images=("static/avt_user.png", "static/avt_bot.png"))
            
            with gr.Row():
                msg = gr.Textbox(
                    show_label=False,
                    placeholder="Nhập tin nhắn của bạn ở đây...",
                )
                submit_btn = gr.Button("Gửi", variant="primary")

            with gr.Row():
                recommend_1 = gr.Button("Cho tôi xem điều hòa có giá khoảng 16 triệu")
                recommend_2 = gr.Button("Điều hòa nào công suất nhỏ nhất")
            
            with gr.Row():
                recommend_3 = gr.Button("Cho tôi xem vài mẫu điều hòa sử dụng Gas R32")
                recommend_4 = gr.Button("So sánh điều hòa DaiKin và Carrier")

            clear = gr.Button("Xóa tin nhắn")
        
        with gr.Column(scale=1):
            user_name = gr.Textbox(label="User Name", placeholder="Nhập tên của bạn")
            phone_number = gr.Textbox(label="Phone Number", placeholder="Nhập số điện thoại")
            address = gr.Textbox(label="Address", placeholder="Nhập địa chỉ")
            id_request = gr.Textbox(label="Request ID", value=str(uuid.uuid4()), visible=False)
            
            with gr.Group(elem_classes="rating-feedback-section"):
                gr.Markdown("### Đánh giá và góp ý")
                
                rating = gr.Radio(
                    choices=["Kém (0)", "Trung bình (5)", "Khá (7.5)", "Tốt (10)"],
                    label="Đánh giá (bắt buộc)",
                    value=None
                )
                
                feedback_text = gr.Textbox(
                    label="Góp ý (không bắt buộc)",
                    placeholder="Nhập góp ý của bạn ở đây...",
                    lines=3
                )
                
                submit_rating_feedback = gr.Button(
                    "Gửi đánh giá và góp ý", 
                    size="sm",
                    elem_classes="rating-submit-btn"
                )
                status_message = gr.Text(label="Thông báo", visible=True)

    def submit_rating_and_feedback(rating_value, feedback, name, phone, addr):
        if not rating_value:
            return "Vui lòng chọn đánh giá trước khi gửi!"
        
        rating_map = {
            "Kém (0)": 0,
            "Trung bình (5)": 5,
            "Khá (7.5)": 7.5,
            "Tốt (10)": 10
        }
        numeric_rating = rating_map.get(rating_value)
        
        history = chatbot.rate_response(
            numeric_rating,
            phone,
            feedback,
            {"name": name, "phone": phone, "address": addr}
        )
        
        return "Cảm ơn bạn đã gửi đánh giá và góp ý!"

    def clear_handler(phone):
        if phone:
            return chatbot.clear_chat(phone)
        return None

    # Update the clear button click event
    clear.click(clear_handler, inputs=[phone_number], outputs=chatbot_interface, queue=False)

    submit_rating_feedback.click(
        submit_rating_and_feedback,
        inputs=[rating, feedback_text, user_name, phone_number, address],
        outputs=[status_message]
    )

    def recommend_handler(text):
        return text

    recommend_1.click(
        lambda: recommend_handler("Cho tôi xem điều hòa có giá khoảng 16 triệu"),
        outputs=msg
    ).then(
        chatbot.chat,
        inputs=[msg, chatbot_interface, id_request, phone_number, address, user_name],
        outputs=[msg, chatbot_interface]
    )
    
    recommend_2.click(
        lambda: recommend_handler("Điều hòa nào công suất nhỏ nhất"),
        outputs=msg
    ).then(
        chatbot.chat,
        inputs=[msg, chatbot_interface, id_request, phone_number, address, user_name],
        outputs=[msg, chatbot_interface]
    )
    
    recommend_3.click(
        lambda: recommend_handler("Cho tôi xem vài mẫu điều hòa sử dụng Gas R32"),
        outputs=msg
    ).then(
        chatbot.chat,
        inputs=[msg, chatbot_interface, id_request, phone_number, address, user_name],
        outputs=[msg, chatbot_interface]
    )
    
    recommend_4.click(
        lambda: recommend_handler("So sánh điều hòa DaiKin và Carrier"),
        outputs=msg
    ).then(
        chatbot.chat,
        inputs=[msg, chatbot_interface, id_request, phone_number, address, user_name],
        outputs=[msg, chatbot_interface]
    )

    submit_btn.click(
        chatbot.chat,
        inputs=[msg, chatbot_interface, id_request, phone_number, address, user_name],
        outputs=[msg, chatbot_interface]
    )
    
    msg.submit(
        chatbot.chat,
        inputs=[msg, chatbot_interface, id_request, phone_number, address, user_name],
        outputs=[msg, chatbot_interface]
    )

    def clear_handler():
        chatbot.pending_rating = False
        return None

    clear.click(clear_handler, None, chatbot_interface, queue=False)

demo.launch(share=True)