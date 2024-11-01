import os
import pickle
import logging
import pandas as pd
from dotenv import load_dotenv
from typing import List
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from elasticsearch import Elasticsearch
from ..model.loader import ModelLoader
from configs.config_system import LoadConfig

load_dotenv()

class DataIndexer:

    @staticmethod
    def restart_index_name(index_names = LoadConfig.INDEX_NAME_ELS):
        # client = Elasticsearch(hosts='http://10.248.243.105:9200')
        client = Elasticsearch(
            cloud_id=os.getenv("ELASTIC_CLOUD_ID"),
            api_key=os.getenv("ELASTIC_API_KEY"),
        )
        for index_name in index_names:
            try:
                if client.indices.exists(index=index_name):
                    client.indices.delete(index=index_name)
                    logging.info(f"Successfully deleted index {index_name}")
                else:
                    logging.info(f"Index {index_name} does not exist")
            except Exception as e:
                logging.error(f"Error when deleting index {index_name}: {e}")


    def _convert_product_data(self, member_code: str) -> None:
        """
        Chuyển đổi dữ liệu sản phẩm từ CSV sang Document và lưu trữ.
        """
        try:
            data_path = LoadConfig.ALL_PRODUCT_FILE_MERGED_STORAGE.format(member_code=member_code)
            df = pd.read_excel(data_path)

            documents = []
            for _, row in df.iterrows():
                content = (
                    f"Tên sản phẩm: '{row['product_name']}' - "
                    f"Mã sản phẩm: {row['product_info_id']} - "
                    f"Giá: {row['lifecare_price']}\n"
                    f"Thông số kỹ thuật:\n {row['specifications']}\n\n"
                )

                metadata = {
                    'product_info_id': row['product_info_id'],
                    "group_product_name": row['group_product_name'],
                    'product_name': row['product_name'],
                    'price': row['lifecare_price'],
                    'short_description': row['short_description'],
                    'specifications': row['specifications'],
                    'file_path': row['file_path'],
                    'power': row['power'],
                    'weight': row['weight'],
                    'volume': row['volume']
                }
                documents.append(Document(content, metadata=metadata))
            logging.info("Successfully converted product data.")
            return documents
        except Exception as e:
            logging.error(f"Error when converting product data: {e}")
            return None
        
    @staticmethod
    def _create_db( 
                   documents: List[Document], 
                   db_path: str) -> None:
        db = Chroma.from_documents(
            documents=documents,
            embedding=ModelLoader.load_embed_openai_model(),
            persist_directory=db_path
        )
    def embedding_data(self, members_code: list =  LoadConfig.MEMBER_CODE) -> None:
        try:
            for member_code in members_code:

                db_path = LoadConfig.VECTOR_DATABASE_STORAGE.format(member_code=member_code)
                #convert data
                documents = self._convert_product_data(member_code=member_code)
                #embedding data
                self._create_db(documents=documents, db_path=db_path)
                
                logging.info(f"Successfully embedded all products for member {member_code}")
        except Exception as e:
            logging.error(f"Error when embedding all products for member: {e}")