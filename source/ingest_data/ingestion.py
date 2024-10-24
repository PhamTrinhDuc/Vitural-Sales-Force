import os
import pickle
import pandas as pd
from typing import List
from configs.config_system import SYSTEM_CONFIG
from langchain_core.documents import Document


class IngestBuilder:

    """Lớp IngestBuilder chịu trách nhiệm chuyển đổi dữ liệu sản phẩm từ định dạng CSV sang định dạng văn bản TXT và lưu trữ chúng.
    Methods:
    - __init__(self, num_product: int, folder_data_text: str, folder_data_csv: str, code_members: List[str]):
        Khởi tạo đối tượng IngestBuilder với các tham số cấu hình hệ thống và kiểm tra số lượng sản phẩm trong thư mục dữ liệu văn bản.
    - chunk_FQA_data(self, xlsx_link: str) -> List[Document]:
        Chuyển đổi file Excel chứa câu hỏi thường gặp (FAQ) thành danh sách các đối tượng Document.
    - chunk_all_data(self, code_member: str, specific_product_folder_csv_path: str, specific_product_folder_text_path: str) -> None:
        Chuyển đổi file CSV chứa thông tin sản phẩm thành danh sách các đối tượng Document và lưu trữ chúng dưới dạng file văn bản.
    - load_document_chunked(self, specific_product_file_path: str) -> List[Document]:
        Tải dữ liệu văn bản đã được chuyển đổi từ file lưu trữ.
    """

    def __init__(self, 
                 num_product: int = SYSTEM_CONFIG.NUM_PRODUCT,  
                 folder_data_text: str = SYSTEM_CONFIG.SPECIFIC_PRODUCT_FOLDER_TXT_STORAGE,
                 folder_data_csv: str = SYSTEM_CONFIG.SPECIFIC_PRODUCT_FOLDER_CSV_STORAGE,
                 code_members: List[str] = SYSTEM_CONFIG.MEMBER_CODE):
        self.code_members = code_members

        for code_member in code_members:
            if len(os.listdir(folder_data_text.format(code_member=code_member))) < num_product:
                self.chunk_all_data(code_member = code_member,
                                    specific_product_folder_csv_path = folder_data_csv,
                                    specific_product_folder_text_path = folder_data_text)

    @staticmethod
    def chunk_FQA_data(xlsx_link: str) -> List[Document]:

        """
        Hàm này để chuyển đổi file CSV thành file văn bản TXT. 
        Với mỗi hàng trong file CSV về câu hỏi thường gặp, chuyển thành đoạn 1 text.
        """
        
        data_text = []
        data = pd.read_excel(xlsx_link)
        data.columns = data.loc[1].values.tolist()
        data = data.loc[2:].reset_index(drop=True)
        data = data.drop(columns=['Title', 'Desire', 'Evaluate'])
        for index, row in data.iterrows():
            question = row['Question']
            answer = row['Answer Bot']
            s = f"Question: {question}\n"
            data_text.append(Document(s))
        
        return data_text

    @staticmethod
    def chunk_all_data(
        code_member: str,
        specific_product_folder_csv_path: str,
        specific_product_folder_text_path: str) -> None:
        
        """
        Hàm này để chuyển đổi file CSV thành file văn bản TXT. 
        Với mỗi hàng trong file CSV sản phấm, chuyển thành đoạn 1 text.
        """

        CSV_DATA_PATH = specific_product_folder_csv_path.format(code_member = code_member)
        TEXT_DATA_PATH = specific_product_folder_text_path.format(code_member = code_member)


        for file_name in os.listdir(CSV_DATA_PATH):
            file_path_csv = os.path.join(CSV_DATA_PATH, file_name)
            dataframes = pd.read_csv(file_path_csv)

            stored_data = []
            for index, row in dataframes.iterrows():
                product_name = row['product_name'] 
                product_info_id = row['product_info_id'] 
                specification = row['specification']
                lifecare_price = row['lifecare_price']
                s1 = f"Tên sản phẩm: '{product_name}' - Mã sản phẩm : {product_info_id} - Giá: {lifecare_price}\n"
                s2 = f"Thông số kỹ thuật:\n {specification}\n"
                stored_data.append(Document(s1 + s2 + "\n"))

            file_text_data = os.path.join(TEXT_DATA_PATH, file_name.replace(".csv", ".pkl"))
            with open(file_text_data, 'wb') as f:
                pickle.dump(stored_data, f)    
        
        os.remove(CSV_DATA_PATH)

    @staticmethod
    def load_document_chunked(specific_product_file_path: str) -> List[Document]:
        with open(specific_product_file_path, 'rb') as f:
            data = pickle.load(f)
            return data