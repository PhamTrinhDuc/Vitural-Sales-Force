import os
import pickle
import dotenv
from typing import List, Tuple, Optional
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_openai import OpenAIEmbeddings
from utils import timing_decorator
from ...model.loader import ModelLoader
from configs.config_system import LoadConfig

dotenv.load_dotenv()

class DocumentManager:
    """Manages document operations and storage"""
    
    def get_document_paths(self, 
                           member_code: str, 
                           product_name: str) -> Tuple[str, str]:
        """Get file and database paths for a product"""
        file_path = os.path.join(
            LoadConfig.SPECIFIC_PRODUCT_FOLDER_TXT_STORAGE.format(member_code=member_code), 
            f"{product_name}.pkl"
            )
        
        db_path = os.path.join(
            LoadConfig.VECTOR_DATABASE_STORAGE.format(member_code=member_code), 
            product_name
            )
        return file_path, db_path
    
    def load_document_chunked(self, file_path: str) -> Document:
        """Load a single document"""
        with open(file_path, "rb") as file:
            return pickle.load(file)

class VectorDBHandler:
    """Handles vector database operations"""
    
    def __init__(self, embedding_model: Optional[OpenAIEmbeddings] = None):
        self.embedding_model = embedding_model or ModelLoader().load_embed_openai_model()
    
    def create_or_load_db(self, documents: List[Document], db_path: str) -> Chroma:
        """Create new vector database or load existing one"""
        if not os.path.exists(db_path):
            return Chroma.from_documents(
                documents=documents,
                embedding=self.embedding_model,
                persist_directory=db_path
            )
        return Chroma(
            persist_directory=db_path,
            embedding_function=self.embedding_model
        )

class RetrieverBuilder:
    """Builds and configures retrievers"""
    
    def build_ensemble_retriever(self, vector_db: Chroma, documents: List[Document]) -> EnsembleRetriever:
        """Build ensemble retriever combining BM25 and vector similarity"""
        bm25_retriever = self._create_bm25_retriever(documents)
        vanilla_retriever = self._create_vanilla_retriever(vector_db)
        
        return EnsembleRetriever(
            retrievers=[vanilla_retriever, bm25_retriever],
            weights=[0.5, 0.5]
        )
    
    def _create_bm25_retriever(self, documents: List[Document]) -> BM25Retriever:
        """Create BM25 retriever"""
        retriever = BM25Retriever.from_documents(documents)
        retriever.k = self.config.top_k_products
        return retriever
    
    def _create_vanilla_retriever(self, vector_db: Chroma):
        """Create vanilla vector similarity retriever"""
        return vector_db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": self.config.top_k_products}
        )

class ChromaQueryEngine:
    """Main retriever class coordinating document retrieval operations"""
    
    def __init__(self, 
                 member_code: str,):
        self.member_code = member_code
        self.doc_manager = DocumentManager()
        self.vector_handler = VectorDBHandler()
        self.retriever_builder = RetrieverBuilder()

    def _load_product_data(self, product_name: str, member_code: str) -> Tuple[List[Document], Chroma]:
        """Load data for a specific product"""
        file_path, db_path = self.doc_manager.get_document_paths(product_name=product_name, member_code=member_code)
        documents = self.doc_manager.load_document_chunked(file_path=file_path)
        vector_db = self.vector_handler.create_or_load_db(documents=documents, db_path=db_path)
        return documents, vector_db
    
    @timing_decorator
    def get_context(self, query: str, product_name: str) -> str:
        """
        Get relevant context for a query about a specific product
        
        Args:
            query: User query after rewriting
            product_name: Name of the product to search in
            
        Returns:
            Relevant context for the query
        """
        documents, vector_db = self._load_product_data(product_name, self.member_code)
        retriever = self.retriever_builder.build_ensemble_retriever(vector_db, documents)
        contents = retriever.invoke(input=query)
        
        return "\n".join(doc.page_content for doc in contents)

if __name__ == "__main__":
    query = "Tôi muốn mua điều hòa có công suất 18000BTU"
    retriever = ChromaQueryEngine(code_member="test")
    response = retriever.get_context(query=query, product_name="air_conditioner")
    print(response)