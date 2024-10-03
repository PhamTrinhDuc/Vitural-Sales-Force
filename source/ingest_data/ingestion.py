import os
import pickle
import pandas as pd
from typing import List
from configs.config_system import SYSTEM_CONFIG
from langchain_core.documents import Document


class IngestBuilder:
    def __init__(self):
        if len(os.listdir(SYSTEM_CONFIG.SPECIFIC_PRODUCT_FOLDER_TXT_DIRECTORY)) == 0:
            self.chunk_all_data()


    def chunk_FQA_data(self, xlsx_link: str = SYSTEM_CONFIG.CSV_FQA_DIRECTORY) -> List[Document]:

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


    def chunk_all_data(self, 
                       specific_product_folder_csv_path: str = SYSTEM_CONFIG.SPECIFIC_PRODUCT_FOLDER_CSV_DIRECTORY,
                       specific_product_folder_text_path: str = SYSTEM_CONFIG.SPECIFIC_PRODUCT_FOLDER_TXT_DIRECTORY) -> None:
        
        """
        Hàm này để chuyển đổi file CSV thành file văn bản TXT. 
        Với mỗi hàng trong file CSV sản phấm, chuyển thành đoạn 1 text.
        """

        CSV_DATA_PATH = specific_product_folder_csv_path
        TEXT_DATA_PATH = specific_product_folder_text_path


        for file_name in os.listdir(CSV_DATA_PATH):
            file_path_csv = os.path.join(CSV_DATA_PATH, file_name)
            dataframes = pd.read_csv(file_path_csv)

            stored_data = []
            for index, row in dataframes.iterrows():
                product_name = row['product_name'] 
                product_code = row['product_code'] 
                specification = row['specification']
                product_info = row['product_info']
                lifecare_price = row['lifecare_price']
                s1 = f"Product_name: {product_name} - ID: {product_code} - Price: {lifecare_price}\n"
                s2 = f"Specifications:\n {specification}\n"
                stored_data.append(Document(s1 + s2 + "\n"))

            file_text_data = os.path.join(TEXT_DATA_PATH, file_name.replace(".csv", ".pkl"))
            with open(file_text_data, 'wb') as f:
                pickle.dump(stored_data, f)    


    def load_document_chunked(self, specific_product_file_path: str) -> List[Document]:
        with open(specific_product_file_path, 'rb') as f:
            data = pickle.load(f)
            return data

