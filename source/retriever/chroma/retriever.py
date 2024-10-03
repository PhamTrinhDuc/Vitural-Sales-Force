import os
import dotenv
from typing import List, Tuple, Optional
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers import EnsembleRetriever
from utils import timing_decorator
from source.ingest_data.ingestion import IngestBuilder
from source.model.loader import ModelLoader
from configs import SYSTEM_CONFIG

dotenv.load_dotenv()

class Retriever:
    def __init__(self):
        os.makedirs(SYSTEM_CONFIG.VECTOR_DATABASE_DIRECTORY, exist_ok=True)
        os.makedirs(SYSTEM_CONFIG.SPECIFIC_PRODUCT_FOLDER_TXT_DIRECTORY, exist_ok=True)
        if len(os.listdir(SYSTEM_CONFIG.VECTOR_DATABASE_DIRECTORY)) == 0:
            self.embedding_all_document()

    def embedding_all_document(self,
                               data_specific_folder_txt_path: Optional[str] = SYSTEM_CONFIG.SPECIFIC_PRODUCT_FOLDER_TXT_DIRECTORY,
                               db_store_folder_path: Optional[str] = SYSTEM_CONFIG.VECTOR_DATABASE_DIRECTORY,
                               embedding_model: Optional[OpenAIEmbeddings] = ModelLoader().load_embed_openai_model()):
        
        os.makedirs(db_store_folder_path, exist_ok=True)
        for file_name in os.listdir(data_specific_folder_txt_path):
            product_name = file_name.split(".")[0]
            file_path = os.path.join(data_specific_folder_txt_path, product_name + ".pkl")
            db_path = os.path.join(db_store_folder_path, product_name)
            data_chunked = IngestBuilder().load_document_chunked(file_path)
            Chroma.from_documents(documents=data_chunked, 
                                  embedding=embedding_model,
                                  persist_directory=db_path)

    def initialize_database_embedding(self,
                                      product_name: str,
                                      data_specific_folder_txt_path: Optional[str] = SYSTEM_CONFIG.SPECIFIC_PRODUCT_FOLDER_TXT_DIRECTORY,
                                      db_store_folder_path: Optional[str] = SYSTEM_CONFIG.VECTOR_DATABASE_DIRECTORY,
                                      embedding_model: Optional[OpenAIEmbeddings] = ModelLoader().load_embed_openai_model()) -> Tuple[list, Chroma, int]:
        
        """
        Load data được chunk của từng sản phẩm, embedding các chunk và lưu vào Chroma
        
        Args:
            csv_prodquct: đường dẫn file csv chứa thông tin sản phẩm
            xlsx_fqa: đường dẫn file xlsx chứa câu hỏi thường gặp
            vecto_db_path: đường dẫn lưu vector embedding cho từng sản phẩm 
            embedding_model: model embedding
        
        Returns:
            data_chunked: data sau khi được chunk
            vectordb: database lưu các vector data 
        """

        file_path = os.path.join(data_specific_folder_txt_path, product_name + ".pkl")
        db_path = os.path.join(db_store_folder_path, product_name)
        data_chunked = IngestBuilder().load_document_chunked(file_path)


        if not db_path:
            vectordb = Chroma.from_documents(documents=data_chunked, 
                                                embedding=embedding_model,
                                                persist_directory=db_path)
        else:
            vectordb = Chroma(persist_directory=db_path, 
                                embedding_function=embedding_model)
        return data_chunked, vectordb

    def initialize_retriever(
        self,
        vector_db: Chroma,
        data_chunked: List[Document]) -> EnsembleRetriever:

        """
        Khởi tạo retriver để tìm kiếm context từ câu hỏi người dùng
        
        Arg: 
            vector db: vector db(Chroma) được khỏi tạo trong file create_db.py
            data_chunked: data được chunk (file từng sản phẩm hoặc file tất cả sản phẩm)
        
        Return:
            trả về  ensemble retriever kết hợp reranker 
        """

        # initialize the bm25 retriever
        retriever_BM25 = BM25Retriever.from_documents(data_chunked)
        retriever_BM25.k = SYSTEM_CONFIG.TOP_K_PRODUCT

        retriever_vanilla = vector_db.as_retriever(search_type="similarity", 
                                                    search_kwargs={"k": SYSTEM_CONFIG.TOP_K_PRODUCT})
        
        # initialize the ensemble retriever with 2 Retrievers
        ensemble_retriever = EnsembleRetriever(
            retrievers=[retriever_vanilla, retriever_BM25], 
            weights=[0.5, 0.5])
        # rerank with cohere
        # compressor = CohereRerank(top_n=top_k)
        # compression_retriever = ContextualCompressionRetriever(
        #     base_compressor=compressor, 
        #     base_retriever=ensemble_retriever
        # )
        return ensemble_retriever

    @timing_decorator
    def get_context(self, query: str, product_name: str) -> str:
        """
        Hàm này để lấy context từ câu hỏi của người dùng
        
        Arg:
            query: câu hỏi của người dùng sau khi được rewrite.
            db_name: loại db chứa data cần tìm kiếm
        
        Return:
            phần context liên quan đến query cho llm
        """

        data_chunked, vector_db = self.initialize_database_embedding(product_name=product_name)

        retriever = self.initialize_retriever(vector_db=vector_db, data_chunked=data_chunked)
        contents = retriever.invoke(input=query)

        final_contents = "\n".join(doc.page_content for doc in contents)
        return final_contents

if __name__ == "__main__":
    query = "Tôi muốn mua điều hòa có công suất 18000BTU"
    retriever = Retriever()
    response = retriever.get_context(query=query)
    print(response)