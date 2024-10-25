import os
import pickle
import pandas as pd
import logging
from typing import List
from langchain_core.documents import Document
from configs.config_system import SYSTEM_CONFIG

class DataConverter:
    """
    Chuyển đổi dữ liệu sản phẩm từ CSV sang định dạng văn bản và lưu trữ.
    """
    
    def __init__(
        self,
        member_code: str,
        num_products: int = SYSTEM_CONFIG.NUM_PRODUCT,
        text_folder: str = SYSTEM_CONFIG.SPECIFIC_PRODUCT_FOLDER_TXT_STORAGE,
        csv_folder: str = SYSTEM_CONFIG.SPECIFIC_PRODUCT_FOLDER_CSV_STORAGE,
    ):
        self.num_products = num_products
        self.text_folder = text_folder
        self.csv_folder = csv_folder
        self.member_code = member_code

    def convert_faq_data(self, xlsx_path: str) -> List[Document]:
        """
        Chuyển đổi file Excel FAQ thành danh sách Document.
        """
        data = pd.read_excel(xlsx_path)
        data.columns = data.loc[1].values.tolist()
        data = data.loc[2:].reset_index(drop=True)
        data = data.drop(columns=['Title', 'Desire', 'Evaluate'])

        documents = []
        for _, row in data.iterrows():
            content = f"Question: {row['Question']}\n"
            documents.append(Document(content))
        
        return documents

    def convert_product_data(self) -> None:
        """
        Chuyển đổi dữ liệu sản phẩm từ CSV sang Document và lưu trữ.
        """
        csv_path = self.csv_folder.format(member_code=self.member_code)
        text_path = self.text_folder.format(member_code=self.member_code)
        try:
            for file_name in os.listdir(csv_path):
                csv_file_path = os.path.join(csv_path, file_name)
                df = pd.read_csv(csv_file_path)

                documents = []
                for _, row in df.iterrows():
                    content = (
                        f"Tên sản phẩm: '{row['product_name']}' - "
                        f"Mã sản phẩm: {row['product_info_id']} - "
                        f"Giá: {row['lifecare_price']}\n"
                        f"Thông số kỹ thuật:\n {row['specifications']}\n\n"
                    )
                    documents.append(Document(content))

                # Lưu documents
                output_path = os.path.join(text_path, file_name.replace(".csv", ".pkl"))
                with open(output_path, 'wb') as f:
                    pickle.dump(documents, f)

            # os.remove(csv_path)
            logging.info("Successfully converted product data.")
        except Exception as e:
            logging.error(f"Error when converting product data: {e}")

    def process_data(self) -> None:
        """
        Kiểm tra và xử lý dữ liệu nếu cần.
        """
        os.makedirs(self.text_folder.format(member_code=self.member_code), exist_ok=True)
        text_path = self.text_folder.format(member_code=self.member_code)
        if len(os.listdir(text_path)) < self.num_products:
            self.convert_product_data()