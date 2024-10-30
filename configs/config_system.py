import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()
# os.environ['LANGCHAIN_TRACING_V2'] = 'true'
# os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
# os.environ['LANGCHAIN_API_KEY'] = os.getenv("LANGCHAIN_API_KEY")
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
# os.environ['TAVILY_API_KEY'] = os.getenv("TAVILY_API_KEY")


@dataclass
class LoadConfig:
    # API CONFIG
    MEMBER_CODE = ['G-JLVIYR', 'G-XNAWVM', 'G-MIMWPJ', 'G-QAXOHL', "NORMAL"]
    # MEMBER_CODE = [index.replace("-", "").lower() for index in MEMBER_CODE]
    
    # SEVER CONFIG
    IP = "0.0.0.0"
    PORT = 7878
    LINK_SEVER = "https://allinonemobile.congtrinhviettel.com.vn/static"

    # POSTGRES CONFIG
    # POSTGRES_HOST = "10.248.243.162"
    # POSTGRES_DB_NAME = "ai_services"
    # POSTGRES_PASSWORD = "Vcc#2024#"
    # POSTGRES_USER = "ai_chatbot_admin"
    # POSTGRES_PORT = 5432
    # POSTGRE_TIMEOUT = 6

    # POSTGRES CONFIG
    POSTGRES_HOST = "127.0.0.1"
    POSTGRES_DB_NAME = "chatbot"
    POSTGRES_PASSWORD = "duc8504@@"
    POSTGRES_USER = "postgres"
    POSTGRES_PORT = 5432
    POSTGRE_TIMEOUT = 6


    # PARAMETER URL CONFIG
    IMAGE_URL = "http://10.248.243.105:8000/process_image/"
    VOICE_URL = "http://10.248.243.105:8005/voice"

    # ELASTIC_SEACH_CONFIG
    INDEX_NAME = [index_name.replace("-", "").lower() for index_name in MEMBER_CODE]
    ELASTIC_URL =  'http://10.248.243.105:9200'
    NUM_SIZE_ELAS =  10
    QUANTITY_SPECIFICATIONS =  ['số lượng', 'bao nhiêu', 'mấy loại', 'số lượng sản phẩm', 'danh sách', 'tổng số', 'mấy', 'liệt kê số lượng', 'liệt kê', 'số lượng hiện còn', 'danh sách đang còn hàng']
    CHEAP_KEYWORDS =  ["rẻ", "giá rẻ", "giá thấp", "bình dân", "tiết kiệm", "khuyến mãi", "giảm giá", "hạ giá", "giá cả phải chăng", "ưu đãi", "rẻ nhất", "nhỏ nhất"]
    EXPENSIVE_KEYWORDS =  ["giá đắt", "giá cao", "xa xỉ", "sang trọng", "cao cấp", "đắt đỏ", "chất lượng cao", "hàng hiệu", "hàng cao cấp", "thượng hạng", "lớn nhất", "đắt nhất", "giá đắt nhất"]

    # DIRECTORIES
    VECTOR_DATABASE_STORAGE = 'data/vector_db/{member_code}'
    ALL_PRODUCT_FILE_NOT_MERGE_STORAGE = 'data/data_private/data_member/data_final_{member_code}.xlsx'
    ALL_PRODUCT_FILE_MERGED_STORAGE = 'data/data_private/data_member/data_final_{member_code}_merged.xlsx'
    SPECIFIC_PRODUCT_FOLDER_CSV_STORAGE = 'data/data_private/data_detail_superapp/{member_code}'
    SPECIFIC_PRODUCT_FOLDER_TXT_STORAGE = 'data/data_private/data_text/{member_code}'
    SIMILAR_PRODUCT_STORAGE = 'data/data_dienmayxanh.csv'
    FEEDBACK_STORAGE = "security/feedback"
    CONVERSATION_STORAGE = 'security/conv_storage'
    INFO_USER_STORAGE = 'security/info_user_storage' 

    # LLM_CONFIG
    TIMEOUT = 50
    GPT_MODEL = 'gpt-4o-mini-2024-07-18'
    TEMPERATURE_RAG = 0.2
    TEMPERATURE_CHAT = 0.5
    MAX_TOKEN = 1024

    # RETRIEVER_CONFIG
    EMBEDDING_BAAI = 'BAAI/bge-small-en-v1.5'
    VECTOR_EMBED_BAAI = 384
    EMBEDDING_OPENAI = 'text-embedding-ada-002'
    VECTOR_EMBED_OPENAI = 1536
    TOP_K_PRODUCT = 3
    TOP_K_QUESTION = 3
    TOP_P = 0.9
    
    NUM_PRODUCT = 22
    TOP_CONVERSATION = 4
    ID_2_NAME_PRODUCT = {
        1: "ban_la",
        2: "bep_tu",
        3: "binh_dun_nuoc",
        4: "binh_nuoc_nong",
        5: "cong_tac_o_cam_thong_minh",
        6: "dieu_hoa",
        7: "dnlmt",
        8: "ghe_massage_daikiosan",
        9: "lo_vi_song__lo_nuong",
        10: "may_giat",
        11: "may_loc_khong_khi_may_hut_bui",
        12: "may_loc_nuoc",
        13: "may_say",
        14: "may_xay",
        15: "noi_ap_suat",
        16: "noi_chien_khong_dau",
        17: "noi_com_dien",
        18: "robot_hut_bui",
        29: "thiet_bi_camera",
        20: "thiet_bi_gia_dung",
        21: "thiet_bi_webcam",
        22: "thiet_bi_wifi",
    }

    MESSAGE = [
        "Chào anh/chị, Viettel Construction cảm ơn anh/chị đã quan tâm đến sản phẩm và dịch vụ của Tổng Công ty. Em có thể hỗ trợ anh/chị thông tin gì không ạ?",
        "Chào mừng anh/chị đã đến với Viettel Construction. Anh/chị cần tìm hiểu sản phẩm nào ạ ?",
        "Em rất vui khi được hỗ trợ anh/chị! Em có thể giúp gì cho anh/chị về các vấn đề chính sách hoặc tìm kiếm thông tin sản phẩm hôm nay?",
        "Xin chào anh/chị! Hôm nay anh chị muốn tìm kiếm sản phẩm nào cho gia đình ạ ?",
        "Chào mừng anh/chị đến với gian hàng tại Viettel Construction. Hôm nay em có thể tư vấn cho anh chị sản phẩm nào ạ ?"
    ]
    
    BUTTON = [
        "Bán cho tôi điều hòa giá rẻ nhất",
        "Bán cho tôi đèn năng lượng mặt trời giá khoảng 1 triệu",
        "Điều hòa nào tốt cho người già và trẻ em ?",
        "Nồi cơm điện cho gia đình 4 người",
        "Ghế massage nào có giá hợp lý và phù hợp cho người lớn tuổi?",
    ]
    
    SYSTEM_MESSAGE = {"error_system": "Đã có vấn đề xảy ra, anh/ chị vui lòng đặt lại câu hỏi để được hỗ trợ ạ!",
                      "end_message": f"""Cảm ơn anh/chị đã quan tâm đến sản phẩm và dịch vụ của Viettel Construction. Nếu có bất kì thắc mắc hay câu hỏi xin vui lòng liên hệ đến tổng đài: <a href="tel:18009377">18009377</a>.""",
                      "question_other": "Hiện tại, bên em chưa có thông tin về câu hỏi này. Anh/ chị có thể liên hệ đến tổng đài: 18009377 để được tư vấn thêm & hỗ trợ. Em xin chân thành cảm ơn!"} # lỗi