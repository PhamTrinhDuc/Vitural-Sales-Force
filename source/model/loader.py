from fastembed import TextEmbedding
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from configs.config_system import LoadConfig

class ModelLoader:
    def __init__(self):
        self.EMBEDDING_OPENAI = LoadConfig.EMBEDDING_OPENAI
        self.EMBEDDING_BAAI = LoadConfig.EMBEDDING_BAAI
        self.GPT_MODEL = LoadConfig.GPT_MODEL
        self.TEMPERATURE_RAG = LoadConfig.TEMPERATURE_RAG
        self.TEMPERATURE_CHAT = LoadConfig.TEMPERATURE_CHAT
        self.MAX_TOKEN = LoadConfig.MAX_TOKEN
    
    def load_embed_openai_model(self) -> OpenAIEmbeddings:
            embedding_model = OpenAIEmbeddings(model = self.EMBEDDING_OPENAI)
            return embedding_model
        
    def load_embed_baai_model(self) -> TextEmbedding:
        embedding_model = TextEmbedding(model_name = self.EMBEDDING_BAAI)
        return embedding_model
    
    def load_rag_model(self) -> ChatOpenAI:
        rag_model = ChatOpenAI(
            model=self.GPT_MODEL,
            temperature=self.TEMPERATURE_RAG,
            max_tokens=self.MAX_TOKEN
        )
        return rag_model
    
    def load_chatchit_model(self) -> ChatOpenAI:
        chatchit_model = ChatOpenAI(
            model=self.GPT_MODEL,
            temperature=self.TEMPERATURE_CHAT,
            max_tokens=self.MAX_TOKEN
        )
        return chatchit_model
