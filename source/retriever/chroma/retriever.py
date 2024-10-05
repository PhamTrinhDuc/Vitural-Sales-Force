import os
from typing import List, Optional
from dataclasses import dataclass
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_openai import OpenAIEmbeddings
from source.ingest_data.ingestion import IngestBuilder
from source.model.loader import ModelLoader
from utils import timing_decorator
from configs import SYSTEM_CONFIG

@dataclass
class RetrieverConfig:
    vector_db_path: str = SYSTEM_CONFIG.VECTOR_DATABASE_STORAGE
    data_folder_path: str = SYSTEM_CONFIG.SPECIFIC_PRODUCT_FOLDER_TXT_STORAGE
    top_k: int = SYSTEM_CONFIG.TOP_K_PRODUCT

class Retriever:
    def __init__(self, config: RetrieverConfig = RetrieverConfig()):
        self.config = config
        self.model_loader = ModelLoader()
        self.ingest_builder = IngestBuilder()
        self._ensure_directories()
        self._initialize_embedding()

    def _ensure_directories(self):
        os.makedirs(self.config.vector_db_path, exist_ok=True)
        os.makedirs(self.config.data_folder_path, exist_ok=True)

    def _initialize_embedding(self):
        if len(os.listdir(self.config.vector_db_path)) < 23:
            self._embed_all_documents()

    def _embed_all_documents(self):
        embedding_model = self.model_loader.load_embed_openai_model()
        for file_name in os.listdir(self.config.data_folder_path):
            product_name = file_name.split(".")[0]
            self._embed_document(product_name, embedding_model)

    def _embed_document(self, product_name: str, embedding_model: OpenAIEmbeddings):
        file_path = os.path.join(self.config.data_folder_path, f"{product_name}.pkl")
        db_path = os.path.join(self.config.vector_db_path, product_name)
        data_chunked = self.ingest_builder.load_document_chunked(file_path)
        Chroma.from_documents(documents=data_chunked, 
                              embedding=embedding_model,
                              persist_directory=db_path)

    def initialize_database_embedding(self, product_name: str) -> tuple[List[Document], Chroma]:
        file_path = os.path.join(self.config.data_folder_path, f"{product_name}.pkl")
        db_path = os.path.join(self.config.vector_db_path, product_name)
        data_chunked = self.ingest_builder.load_document_chunked(file_path)
        embedding_model = self.model_loader.load_embed_openai_model()
        
        vectordb = (Chroma(persist_directory=db_path, embedding_function=embedding_model) 
                    if os.path.exists(db_path) 
                    else Chroma.from_documents(documents=data_chunked, 
                                               embedding=embedding_model,
                                               persist_directory=db_path))
        return data_chunked, vectordb

    def initialize_retriever(self, vector_db: Chroma, data_chunked: List[Document]) -> EnsembleRetriever:
        retriever_BM25 = BM25Retriever.from_documents(data_chunked)
        retriever_BM25.k = self.config.top_k

        retriever_vanilla = vector_db.as_retriever(search_type="similarity", 
                                                   search_kwargs={"k": self.config.top_k})
        
        return EnsembleRetriever(retrievers=[retriever_vanilla, retriever_BM25], 
                                 weights=[0.5, 0.5])

    @timing_decorator
    def get_context(self, query: str, product_name: str) -> str:
        data_chunked, vector_db = self.initialize_database_embedding(product_name)
        retriever = self.initialize_retriever(vector_db, data_chunked)
        contents = retriever.invoke(input=query)
        return "\n".join(doc.page_content for doc in contents)

if __name__ == "__main__":
    query = "Tôi muốn mua điều hòa có công suất 18000BTU"
    retriever = Retriever()
    response = retriever.get_context(query=query, product_name="air_conditioner")
    print(response)
