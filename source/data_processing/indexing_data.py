import os
import pickle
import logging
from dotenv import load_dotenv
from typing import List
from dataclasses import dataclass
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from elasticsearch import Elasticsearch
from ..model.loader import ModelLoader
from configs.config_system import LoadConfig

load_dotenv()

class DataIndexer:

    @staticmethod
    def restart_index_name(index_names = LoadConfig.INDEX_NAME):
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

    @staticmethod
    def _create_db( 
                   documents: List[Document], 
                   db_path: str = LoadConfig.VECTOR_DATABASE_STORAGE) -> None:
        db = Chroma.from_documents(
            documents=documents,
            embedding=ModelLoader().load_embed_openai_model(),
            persist_directory=db_path
        )
    @staticmethod
    def _load_data(data_path: str):
        with open(data_path, 'rb') as f:
            return pickle.load(f)

    def embedding_all_product(self, folder_path: str = LoadConfig.specific_txt_folder_path) -> None:
        try:
            for code in LoadConfig.MEMBER_CODE:
                folder_member_path = folder_path.format(member_code=code)
                db_member_path = db_path.format(member_code=code)
                os.makedirs(db_member_path, exist_ok=True)
                if len(os.listdir(db_member_path)) < LoadConfig.NUM_PRODUCT:
                    for file_name in os.listdir(folder_member_path):
                        file_path = os.path.join(folder_member_path, file_name)
                        documents = self._load_data(file_path)
                        db_path = os.path.join(db_member_path, file_name.replace(".pkl", ""))
                        self._create_db(documents, db_path)
                    logging.info(f"Successfully embedded all products for member {code}")
                else:
                    logging.info(f"Member {code} has already been embedded")
        except Exception as e:
            logging.error(f"Error when embedding all products: {e}")