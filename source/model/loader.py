from typing import Optional
from fastembed import TextEmbedding
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from configs.config_system import SYSTEM_CONFIG

class ModelLoader:
    def __init__(self):
        self.EMBEDDING_OPENAI = SYSTEM_CONFIG.EMBEDDING_OPENAI
        self.EMBEDDING_BAAI = SYSTEM_CONFIG.EMBEDDING_BAAI
        self.GPT_MODEL = SYSTEM_CONFIG.GPT_MODEL
        self.TEMPERATURE_RAG = SYSTEM_CONFIG.TEMPERATURE_RAG
        self.TEMPERATURE_CHAT = SYSTEM_CONFIG.TEMPERATURE_CHAT
        self.MAX_TOKEN = SYSTEM_CONFIG.MAX_TOKEN
    
    def load_embed_openai_model(self) -> OpenAIEmbeddings:
            embedding_model = OpenAIEmbeddings(model = self.EMBEDDING_OPENAI)
            return embedding_model
        
    def load_embed_baai_model(self) -> TextEmbedding:
        embedding_model = TextEmbedding(model_name = self.EMBEDDING_BAAI)
        return embedding_model
    
    def load_rag_model(self) -> ChatOpenAI:
        rag_model = ChatOpenAI(
            model=self.GPT_MODEL,
            streaming=True,
            temperature=self.TEMPERATURE_RAG,
            max_tokens=self.MAX_TOKEN,
            verbose=True,
        )
        return rag_model
    
    def load_chatchit_model(self) -> ChatOpenAI:
        chatchit_model = ChatOpenAI(
            model=self.GPT_MODEL,
            temperature=self.TEMPERATURE_CHAT,
            max_tokens=self.MAX_TOKEN,
            verbose=True,
        )
        return chatchit_model
