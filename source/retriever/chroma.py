import os
import dotenv
import pandas as pd
from typing import List, Tuple, Optional
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_openai import OpenAIEmbeddings
from utils import timing_decorator, RetrieveHelper
from ..model.loader import ModelLoader
from configs.config_system import LoadConfig

dotenv.load_dotenv()

class DocumentManager:
    """Manages document operations and storage"""
    @staticmethod
    def ingest_data(member_code: str) -> List[Document]:
        csv_file_path = LoadConfig.ALL_PRODUCT_FILE_MERGED_STORAGE.format(member_code=member_code)
        df = pd.read_excel(csv_file_path)

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
        return documents
    
class VectorDBHandler:
    """Handles vector database operations"""
    
    def __init__(self, embedding_model: Optional[OpenAIEmbeddings] = None):
        self.embedding_model = embedding_model or ModelLoader.load_embed_openai_model()
    
    def create_or_load_db(self, documents: List[Document], db_path: str) -> Chroma:
        """Create new vector database or load existing one"""
        if not os.path.exists(db_path):
            return Chroma.from_documents(
                documents=documents,
                embedding=self.embedding_model,
                persist_directory=db_path,
            )
        return Chroma(
            persist_directory=db_path,
            embedding_function=self.embedding_model
        )

class RetrieverBuilder:
    """Builds and configures retrievers"""
    
    def build_ensemble_retriever(self, vector_db: Chroma, documents: List[Document], demands: dict[str, any]) -> EnsembleRetriever:
        """Build ensemble retriever combining BM25 and vector similarity"""
        bm25_retriever = self._create_bm25_retriever(documents=documents)
        vanilla_retriever = self._create_vanilla_retriever(vector_db=vector_db, demands=demands)
        
        return EnsembleRetriever(
            retrievers=[vanilla_retriever, bm25_retriever],
            weights=[0.5, 0.5]
        )
    
    def _create_bm25_retriever(self, documents: List[Document]) -> BM25Retriever:
        """Create BM25 retriever"""
        retriever = BM25Retriever.from_documents(documents)
        retriever.k = LoadConfig.TOP_K_PRODUCT
        return retriever
    
    def _create_vanilla_retriever(self, vector_db: Chroma, demands: dict[str, any]) -> Chroma:
        """Create vanilla vector similarity retriever"""

        filter = {"price": {"$gte": 0}, "price": {"$lte": 1000000000}}
        for key, value in demands.items():

            if value and key in ["price", "power", "weight", "volume"]:
                min_val, max_val = RetrieveHelper().parse_specification_range(specification=value)
                filter =  [{key: {"$gte": min_val}, key: {"$lte": max_val}}]
                if key == 'price': break

        return vector_db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": LoadConfig.TOP_K_PRODUCT, 
                           "filter": {"group_product_name": demands.get('group', '')}}
            )

class ChromaQueryEngine:
    """Main retriever class coordinating document retrieval operations"""
    
    def __init__(self, 
                 member_code: str,):
        self.member_code = member_code
        self.doc_manager = DocumentManager()
        self.vector_handler = VectorDBHandler()
        self.retriever_builder = RetrieverBuilder()

    def _load_product_data(self) -> Tuple[List[Document], Chroma]:
        """Load data for a specific product"""
        db_path = LoadConfig.VECTOR_DATABASE_STORAGE.format(member_code=self.member_code)
        documents = self.doc_manager.ingest_data(member_code=self.member_code)
        vector_db = self.vector_handler.create_or_load_db(documents=documents, db_path=db_path)
        return documents, vector_db
    
    @timing_decorator
    def get_context(self, query: str, demands: str) -> str:
        """
        Get relevant context for a query about a specific product
        
        Args:
            query: User query after rewriting
            product_name: Name of the product to search in
            
        Returns:
            Relevant context for the query
        """
        documents, vector_db = self._load_product_data()
        retriever = self.retriever_builder.build_ensemble_retriever(vector_db=vector_db, 
                                                                    documents=documents, 
                                                                    demands=demands)
        contents = retriever.invoke(input=query)
        return "\n".join(doc.page_content for doc in contents) if contents else None

    def testing(self, query: str):
        response = self.get_context(query=query)
        print(response)

if __name__ == "__main__":
    query = "Tôi muốn mua điều hòa có công suất 18000BTU"
    retriever = ChromaQueryEngine(code_member="NORMAL")
    retriever.testing(query=query)