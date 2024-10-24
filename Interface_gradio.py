import gradio as gr
from configs import SYSTEM_CONFIG
from api.handle_request import handle_request
from source.generate.chat_seasion import Pipeline

class ChatBot:
    def __init__(self):
        self.pipeline = Pipeline(code_member="NORMAL")
        self.chat_history = []

    def chat(self, message, history, id_request, name_bot, user_name, image, voice, phone_number, address):
        input_text = message if message else "first_text"
        
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
            PhoneNumber=phone_number,
            Address=address
        )

        bot_message = response.get("content", "")
        if response.get("terms"):
            bot_message += "\n\nTerms: " + ", ".join(response.get("terms"))
        
        self.chat_history.append((message, bot_message))
        return "", self.chat_history

chatbot = ChatBot()

with gr.Blocks(css="#chatbot {height: 400px; overflow: auto;}") as demo:
    gr.Markdown(
        """
        # 🤖 Chat with Bot
        Welcome to our AI chatbot! Enter your message below and interact with our intelligent assistant.
        """
    )
    
    with gr.Row():
        with gr.Column(scale=3):
            chatbot_interface = gr.Chatbot(elem_id="chatbot")
            with gr.Row():
                msg = gr.Textbox(
                    label="Type your message here",
                    placeholder="Enter your message...",
                    show_label=False
                )
                submit_btn = gr.Button("Send", variant="primary")
            clear = gr.Button("Clear Chat")
        
        with gr.Column(scale=1):
            user_name = gr.Textbox(label="User Name", placeholder="Enter your name", value="Phạm Đức")
            phone_number = gr.Textbox(label="Phone Number", placeholder="Enter your phone number", value="0987654321")
            address = gr.Textbox(label="Address", placeholder="Enter your address", value="Hà Nội")
            id_request = gr.Textbox(label="ID Request", placeholder="Enter your ID Request", value="1436909309")
            name_bot = gr.Textbox(label="Bot Name", placeholder="Enter your bot name", value="SuperApp")
            image = gr.Textbox(label="Image")
            voice = gr.Textbox(label="Voice")

    submit_btn.click(chatbot.chat, [msg, chatbot_interface, id_request, name_bot, user_name, image, voice, phone_number, address], [msg, chatbot_interface])
    msg.submit(chatbot.chat, [msg, chatbot_interface, id_request, name_bot, user_name, image, voice, phone_number, address], [msg, chatbot_interface])
    clear.click(lambda: None, None, chatbot_interface, queue=False)

demo.launch()