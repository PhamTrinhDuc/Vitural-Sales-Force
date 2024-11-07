import os
from dataclasses import dataclass
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

@dataclass
class LoadConfig:
    # API CONFIG
    MEMBER_CODE = ['G-JLVIYR', 'G-XNAWVM', 'G-MIMWPJ', 'G-QAXOHL', "NORMAL"]
    TIMEOUT = 50
    # MEMBER_CODE = [index.replace("-", "").lower() for index in MEMBER_CODE]
    
    # SEVER CONFIG
    IP = "0.0.0.0"
    PORT = 7878

    # POSTGRES CONFIG
    POSTGRES_HOST = "127.0.0.1"
    POSTGRES_DB_NAME = "chatbot"
    POSTGRES_PASSWORD = "duc8504@@"
    POSTGRES_USER = "postgres"
    POSTGRES_PORT = 5432
    POSTGRE_TIMEOUT = 6


    # ELASTIC_SEACH_CONFIG
    INDEX_NAME_ELS = [index_name.replace("-", "").lower() for index_name in MEMBER_CODE]
    ELASTIC_URL =  'http://10.248.243.105:9200'
    NUM_SIZE_ELAS = 4
    QUANTITY_SPECIFICATIONS =  ['số lượng', 'bao nhiêu', 'mấy loại', 'số lượng sản phẩm', 'danh sách', 'tổng số', 'mấy', 'liệt kê số lượng', 'liệt kê', 'số lượng hiện còn', 'danh sách đang còn hàng']
    CHEAP_KEYWORDS =  ["rẻ", "giá rẻ", "giá thấp", "bình dân", "tiết kiệm", "khuyến mãi", "giảm giá", "hạ giá", "giá cả phải chăng", "ưu đãi", "rẻ nhất", "nhỏ nhất"]
    EXPENSIVE_KEYWORDS =  ["giá đắt", "giá cao", "xa xỉ", "sang trọng", "cao cấp", "đắt đỏ", "chất lượng cao", "hàng hiệu", "hàng cao cấp", "thượng hạng", "lớn nhất", "đắt nhất", "giá đắt nhất"]

    # QDRANT CONFIG
    # INDEX_NAME_QDRANT = "test_collection"
    INDEX_NAME_QDRANT = "test_hybrid"


    # DIRECTORIES
    VECTOR_DATABASE_STORAGE = 'data/vector_db/{member_code}'
    ALL_PRODUCT_FILE_NOT_MERGE_STORAGE = 'data/data_private/data_member/data_final_{member_code}.xlsx'
    ALL_PRODUCT_FILE_MERGED_STORAGE = 'data/data_private/data_member/data_final_{member_code}_merged.xlsx'
    SIMILAR_PRODUCT_STORAGE = 'data/data_dienmayxanh.csv'
    FEEDBACK_STORAGE = "security/feedback"
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
    
    NUM_PRODUCT = 22
    LIST_GROUP_NAME = pd.unique(pd.read_excel("data/data_private/data_member/data_final_NORMAL_merged.xlsx")['group_product_name'].tolist())
    TOP_CONVERSATION = 4
  
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