import gradio as gr
from source.generate.gradio_chat import chat_with_history
from PIL import Image
import requests
from io import BytesIO
import random

# Hàm reset lại cuộc trò chuyện
def reset_conversation():
    return [("", "Chào mừng anh/chị đến với VCC! Em là Phương Nhi, luôn ở đây để hỗ trợ và tư vấn mua sắm. Có phải anh chị đang có nhu cầu tìm hiểu và mua sắm phải không? Vậy hãy cho em biết mình cần tìm loại nào và với ngân sách bao nhiêu ạ! Chúc anh/chị một ngày rực rỡ và thành công! 🌈")], []

# Hàm tải hình ảnh từ URL
def load_image(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        return img
    except requests.exceptions.RequestException as e:
        print(f"Error loading image: {e}")
        return None

# Danh sách các URL ảnh sản phẩm
image_urls = [
    "https://bizweb.dktcdn.net/thumb/1024x1024/100/431/725/products/1-a3117c0b-55ff-4efd-b2bd-ec4ef2e86b56-99738266-1a91-458d-81c7-de7ea010b0d6.jpg?v=1686110787373", 
    "https://tragopacs.com/www/thumbs/thumb_6553de64e7f23_resize_700_700.jpg",
    "https://dienmaybaominh.vn/wp-content/uploads/2024/04/dieu-hoa-mdv-mdvg-10crdn8.jpg",
    "https://dienmayhungthinh.vn/wp-content/uploads/2023/06/auto-draft-86-444x296.jpg",
    "https://mdvvn.com/thumbs/400x300x1/upload/product/270x270-xtremeheat-8253.png",
    "https://bizweb.dktcdn.net/thumb/1024x1024/100/255/442/products/mdv-mdvf-10crn8.jpg?v=1689067021920",
    "https://bizweb.dktcdn.net/thumb/1024x1024/100/255/442/products/vsica-12civ.png?v=1622694889237",
]

# Hình ảnh mặc định nếu không tải được hình từ URL
default_image = Image.new('RGB', (300, 300), color = (255, 255, 255))

# Hàm lấy ảnh ngẫu nhiên
def get_random_images():
    selected_urls = random.sample(image_urls, min(len(image_urls), 4))
    images = [load_image(url) for url in selected_urls]
    
    # Đảm bảo luôn có đủ 4 ảnh, nếu thiếu ảnh thì dùng ảnh mặc định
    while len(images) < 4:
        images.append(default_image)
    
    return images[:4]  # Trả về đúng 4 ảnh

# Giao diện Gradio
with gr.Blocks(css="""
    #chatbot { 
        height: 100%; 
        overflow-y: auto; 
        border: 1px solid #ddd; 
        border-radius: 15px; 
        padding: 20px;
        background-color: #f7f7f7;
    }
    #chatbot .user, #chatbot .bot { 
        padding: 10px 15px; 
        border-radius: 20px; 
        display: inline-block;
    }
    #chatbot .user { 
        background-color: #FF6347; 
        color: black;
        float: right;
    }
    #chatbot .bot { 
        background-color: #F0F8FF; 
        color: black;
        float: left;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    #chat-header {
        text-align: center;
        padding: 20px;
        background-color: #FF6347;
        color: white;
        border-radius: 15px 15px 0 0;
        margin-bottom: 20px;
    }
    #msg-box {
        border-radius: 20px;
        border: 1px solid #ddd;
    }
    #send-btn, #reset-btn, #clear-btn {
        border-radius: 20px;
    }
    .button-row {
        display: flex;
        justify-content: space-between;
        margin-top: 10px;
    }
""") as demo:
    gr.HTML("""
    <div id="chat-header">
        <h1 style="color: #000000">💬 Chat với AI Assistant</h1>
        <p style="color: #000000">Hãy đặt câu hỏi, tôi sẽ cố gắng trả lời bạn!</p>
    </div>
    """)

    # Giao diện chatbot
    chatbot = gr.Chatbot(
        [("", "Chào mừng anh/chị đã tin tưởng mua sắm tại Viettel. Em là Phương Nhi, trợ lý tư vấn bán hàng tại VCC luôn ở đây để hỗ trợ và tư vấn mua sắm. Có phải anh chị đang có nhu cầu tìm hiểu, mua sắm phải không? Vậy hãy cho em biết mình cần tìm sản phẩm nào và với ngân sách bao nhiêu ạ! Chúc anh/chị một ngày rực rỡ và thành công! 🌈")],
        elem_id="chatbot",
        bubble_full_width=False,
        avatar_images=("static/avt_user.png", "static/avt_bot.png"),
    )

    # Khu vực nhập tin nhắn và nút gửi
    with gr.Row():
        txt = gr.Textbox(
            show_label=False,
            placeholder="Nhập tin nhắn của bạn ở đây...",
            elem_id="msg-box"
        )
        submit_btn = gr.Button("Gửi", elem_id="send-btn")

    # Xử lý khi gửi tin nhắn
    txt.submit(chat_with_history, [txt, chatbot], [txt, chatbot])
    submit_btn.click(chat_with_history, [txt, chatbot], [txt, chatbot])

    # Nút xóa và reset cuộc trò chuyện
    with gr.Row(elem_classes="button-row"):
        clear = gr.Button("Xóa tin nhắn", elem_id="clear-btn")
        reset = gr.Button("Reset cuộc trò chuyện", elem_id="reset-btn")

    clear.click(lambda: None, None, chatbot, queue=False)
    reset.click(reset_conversation, outputs=[chatbot, txt])

    # Khu vực hiển thị ảnh sản phẩm
    with gr.Row():
        show_images_btn = gr.Button("Xem ảnh sản phẩm", elem_id="view-images-btn")
    
    with gr.Row():
        image1 = gr.Image(type="pil", label="Hình ảnh sản phẩm 1", width=300, height=300)
        image2 = gr.Image(type="pil", label="Hình ảnh sản phẩm 2", width=300, height=300)
        image3 = gr.Image(type="pil", label="Hình ảnh sản phẩm 3", width=300, height=300)
        image4 = gr.Image(type="pil", label="Hình ảnh sản phẩm 4", width=300, height=300)

    # Hàm cập nhật hình ảnh
    def update_images():
        return get_random_images()

    # Xử lý khi nhấn nút xem ảnh
    show_images_btn.click(update_images, outputs=[image1, image2, image3, image4])

# Chạy ứng dụng Gradio
demo.launch(share=True)
