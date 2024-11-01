from fastembed import TextEmbedding
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from configs.config_system import LoadConfig

class ModelLoader:

    @staticmethod
    def load_embed_openai_model() -> OpenAIEmbeddings:
        embedding_model = OpenAIEmbeddings(model=LoadConfig.EMBEDDING_OPENAI, 
                                            timeout=LoadConfig.TIMEOUT)
        return embedding_model
    
    @staticmethod
    def load_embed_baai_model() -> TextEmbedding:
        embedding_model = TextEmbedding(model_name=LoadConfig.EMBEDDING_BAAI)
        return embedding_model
    
    @staticmethod
    def load_rag_model() -> ChatOpenAI:
        rag_model = ChatOpenAI(
            model=LoadConfig.GPT_MODEL,
            temperature=LoadConfig.TEMPERATURE_RAG,
            max_tokens=LoadConfig.MAX_TOKEN,
            timeout=LoadConfig.TIMEOUT
        )
        return rag_model
    @staticmethod
    def load_chatchit_model() -> ChatOpenAI:
        chatchit_model = ChatOpenAI(
            model=LoadConfig.GPT_MODEL,
            temperature=LoadConfig.TEMPERATURE_CHAT,
            max_tokens=LoadConfig.MAX_TOKEN,
            timeout=LoadConfig.TIMEOUT
        )
        return chatchit_model

    @staticmethod
    def testing():
        model = ModelLoader.load_chatchit_model()
        print(model)