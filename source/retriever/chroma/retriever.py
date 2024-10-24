import os
import dotenv
from typing import List, Tuple, Optional
from dataclasses import dataclass
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_openai import OpenAIEmbeddings
from utils import timing_decorator
from ...ingest_data.ingestion import IngestBuilder
from ...model.loader import ModelLoader
from configs import SYSTEM_CONFIG

dotenv.load_dotenv()

@dataclass
class RetrieverConfig:
    """Configuration for Retriever"""
    text_data_path: str = SYSTEM_CONFIG.SPECIFIC_PRODUCT_FOLDER_TXT_STORAGE
    vector_db_path: str = SYSTEM_CONFIG.VECTOR_DATABASE_STORAGE
    top_k_products: int = SYSTEM_CONFIG.TOP_K_PRODUCT
    num_products: int = SYSTEM_CONFIG.NUM_PRODUCT

class DocumentManager:
    """Manages document operations and storage"""
    
    def __init__(self, config: RetrieverConfig):
        self.config = config
    
    def ensure_directories(self, code_member: str) -> None:
        """Ensure necessary directories exist"""
        os.makedirs(self.config.vector_db_path.format(code_member=code_member), exist_ok=True)
        os.makedirs(self.config.text_data_path.format(code_member=code_member), exist_ok=True)
    
    def needs_embedding(self, code_member: str) -> bool:
        """Check if documents need to be embedded"""
        return len(os.listdir(self.config.vector_db_path.format(code_member=code_member))) < self.config.num_products

    def get_document_paths(self, product_name: str) -> Tuple[str, str]:
        """Get file and database paths for a product"""
        file_path = os.path.join(self.config.text_data_path, f"{product_name}.pkl")
        db_path = os.path.join(self.config.vector_db_path, product_name)
        return file_path, db_path

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
    
    def __init__(self, config: RetrieverConfig):
        self.config = config
    
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

class Retriever:
    """Main retriever class coordinating document retrieval operations"""
    
    def __init__(self, 
                 code_member: str, 
                 config: Optional[RetrieverConfig] = None):
        
        self.config = config or RetrieverConfig()
        self.doc_manager = DocumentManager(self.config)
        self.vector_handler = VectorDBHandler()
        self.retriever_builder = RetrieverBuilder(self.config)
        
        # Initialize system
        self._initialize_system(code_member)
    
    def _initialize_system(self, code_member: str) -> None:
        """Initialize the retrieval system"""
        self.doc_manager.ensure_directories(code_member)
        if self.doc_manager.needs_embedding(code_member):
            self._embed_all_documents()
    
    def _embed_all_documents(self) -> None:
        """Embed all documents in the data directory"""
        for filename in os.listdir(self.config.text_data_path):
            product_name = filename.split(".")[0]
            file_path, db_path = self.doc_manager.get_document_paths(product_name)
            
            documents = IngestBuilder().load_document_chunked(file_path)
            self.vector_handler.create_or_load_db(documents, db_path)
    
    def _load_product_data(self, product_name: str) -> Tuple[List[Document], Chroma]:
        """Load data for a specific product"""
        file_path, db_path = self.doc_manager.get_document_paths(product_name)
        documents = IngestBuilder().load_document_chunked(file_path)
        vector_db = self.vector_handler.create_or_load_db(documents, db_path)
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
        documents, vector_db = self._load_product_data(product_name)
        retriever = self.retriever_builder.build_ensemble_retriever(vector_db, documents)
        contents = retriever.invoke(input=query)
        
        return "\n".join(doc.page_content for doc in contents)

if __name__ == "__main__":
    query = "Tôi muốn mua điều hòa có công suất 18000BTU"
    retriever = Retriever(code_member="test")
    response = retriever.get_context(query=query, product_name="air_conditioner")
    print(response)