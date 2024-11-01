from langchain_community.callbacks.manager import get_openai_callback
from utils import timing_decorator, SeachingDecision
from source.model.loader import ModelLoader
from source.prompt.template import PROMPT_ROUTER
from configs.config_system import LoadConfig



@timing_decorator
def decision_search_type(query: str) -> str: 
    """
    Hàm này để phân loại loại câu hỏi của người dùng.
    Arg:
        query: câu hỏi của người dùng
        history: lịch sử của người dùng
        Sử dụng LLM để  phân loại câu hỏi của người dùng thành 1 trong 3 loại: TEXT, ELS, SIMILARITY
    Return:
        trả về loại câu hỏi
    """
    with get_openai_callback() as cb:
        llm_with_output = ModelLoader.load_rag_model().with_structured_output(SeachingDecision)
        type = llm_with_output.invoke(PROMPT_ROUTER.format(query=query, 
                                                           list_products = LoadConfig.LIST_GROUP_NAME)).type
    return {
        'content': type,
        'total_token': cb.total_tokens,
        'total_cost': cb.total_cost
    }
