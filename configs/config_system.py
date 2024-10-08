import os
from dotenv import load_dotenv

load_dotenv()
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
os.environ['LANGCHAIN_API_KEY'] = os.getenv("LANGCHAIN_API_KEY")
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
os.environ['TAVILY_API_KEY'] = os.getenv("TAVILY_API_KEY")

class LoadConfig:
    # SEVER CONFIG
    IP = "0.0.0.0"
    PORT = 8089
    LINK_SEVER = "https://allinonemobile.congtrinhviettel.com.vn/static"

    # POSTGRES CONFIG
    POSTGRES_HOST = "10.248.243.162"
    POSTGRES_DB_NAME = "ai_services"
    POSTGRES_PASSWORD = "Vcc#2024#"
    POSTGRES_USER = "ai_chatbot_admin"
    POSTGRES_PORT = 5432
    POSTGRE_TIMEOUT = 6

    # POSTGRES CONFIG
    # POSTGRES_HOST = "127.0.0.1"
    # POSTGRES_DB_NAME = "chatbot"
    # POSTGRES_PASSWORD = "duc8504@@"
    # POSTGRES_USER = "postgres"
    # POSTGRES_PORT = 5432
    # POSTGRE_TIMEOUT = 6

    # PARAMETER URL CONFIG
    IMAGE_URL = "http://10.248.243.105:8000/process_image/"
    VOICE_URL = "http://10.248.243.105:8005/voice"

    # ELASTIC_SEACH_CONFIG
    INDEX_NAME = "chatbot"
    ELASTIC_URL =  'http://10.248.243.105:9200'
    NUM_SIZE_ELAS =  10
    QUANTITY_SPECIFICATIONS =  ['số lượng', 'bao nhiêu', 'mấy loại', 'số lượng sản phẩm', 'danh sách', 'tổng số', 'mấy', 'liệt kê số lượng', 'liệt kê', 'số lượng hiện còn', 'danh sách đang còn hàng']
    CHEAP_KEYWORDS =  ["rẻ", "giá rẻ", "giá thấp", "bình dân", "tiết kiệm", "khuyến mãi", "giảm giá", "hạ giá", "giá cả phải chăng", "ưu đãi", "rẻ nhất", "nhỏ nhất"]
    EXPENSIVE_KEYWORDS =  ["giá đắt", "giá cao", "xa xỉ", "sang trọng", "cao cấp", "đắt đỏ", "chất lượng cao", "hàng hiệu", "hàng cao cấp", "thượng hạng", "lớn nhất", "đắt nhất"]

    # DIRECTORIES
    VECTOR_DATABASE_STORAGE = 'data/vector_db'
    ALL_PRODUCT_FILE_CSV_STORAGE = 'data/data_private/product_final_300_extract.xlsx'
    SPECIFIC_PRODUCT_FOLDER_CSV_STORAGE = 'data/data_private/data_csv'
    SPECIFIC_PRODUCT_FOLDER_TXT_STORAGE = 'data/data_private/data_text'
    SIMILAR_PRODUCT_STORAGE = 'data/data_private/data_dienmayxanh.csv'
    CONVERSATION_STORAGE = 'security/conv_storage'
    INFO_USER_STORAGE = 'security/info_user_storage'

    # LLM_CONFIG
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
    
    # CONFIG PRODUCT
    NUM_PRODUCT = 23
    ID_2_NAME_PRODUCT = {
        1: "ban_la",
        2: "bep_tu",
        3: "binh_dun_nuoc",
        4: "binh_nuoc_nong",
        5: "cong_tac",
        6: "dieu_hoa",
        7: "dnlmt",
        8: "ghe_massage",
        9: "lo_vi_song",
        10: "may_giat",
        11: "may_loc_kk",
        12: "may_loc_nuoc",
        13: "may_say_quan_ao",
        14: "may_say_toc",
        15: "may_xay",
        16: "noi_ap_suat",
        17: "noi_chien_kh_dau",
        18: "noi_com_dien",
        19: "robot_hut_bui",
        20: "thiet_bi_camera",
        21: "thiet_bi_giadung",
        22: "thiet_bi_webcam",
        23: "thiet_bi_wifi",
    }

    MESSAGE = [
        "Xin chào! Em là Phương Nhi, trợ lý AI của bạn tại VCC. Em đang phát triển nên không phải lúc nào cũng đúng. Anh/chị có thể phản hồi để giúp em cải thiện tốt hơn. Em xin chân thành cảm ơn!",
        "Em rất vui khi được hỗ trợ anh/chị! Em là Phương Nhi, trợ lý AI tư vấn bán hàng của VCC. Do đang trong quá trình hoàn thiện nên em có thể mắc lỗi. Mọi góp ý của anh/chị đều giúp em ngày càng hoàn thiện. Em có thể giúp gì cho bạn về các vấn đề chính sách hoặc tìm kiếm thông tin sản phẩm hôm nay?",
        "Xin chào! Em là Phương Nhi,trợ lý AI tư vấn bán hàng của VCC. Em vẫn đang trong giai đoạn phát triển và có thể không hoàn hảo. Hãy giúp em cải thiện bằng cách phản hồi về trải nghiệm của anh/chị. Em có thể hỗ trợ bạn gì về chính sách hoặc thông tin sản phẩm hôm nay?",
        "Xin chào anh/chị! Em rất hân hạnh được hỗ trợ anh chị trong việc tìm kiếm sản phẩm và chính sách.",
        "Rất vui khi được hỗ trợ anh/chị trong việc tìm kiếm sản phẩm. Do đang trong quá trình hoàn thiện nên em có thể mắc lỗi. Mong anh/chị thông cảm!"
        ]
    BUTTON = [
        "Anh/chị muốn biết VCC bán những gì?",
        "Anh/chị muốn tìm sản phẩm Đèn năng mặt trời cao cấp?",
        "Với ngân sách tầm dưới 10 triệu anh/chị có thể mua điều hòa nào?",
        "Anh/chị cần tìm đèn năng lượng mặt trời giá 500k",
        "Anh/chị có như cầu tìm bình nước nóng có dung tích 30 lít",
        "Đèn năng lượng mặt trời có câm nặng tầm 3kg",
    ]
    
SYSTEM_CONFIG = LoadConfig()