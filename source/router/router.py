from langchain_core.prompts import PromptTemplate
from utils import SeachingDecision, ClassfifyProduct
from utils import timing_decorator
from source.model.loader import ModelLoader
from source.prompt.template import PROMPT_ROUTER, PROMPT_CLF_PRODUCT

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
    llm_with_output = ModelLoader().load_rag_model().with_structured_output(SeachingDecision)
    type = llm_with_output.invoke(PROMPT_ROUTER.format(query=query)).type
    return type

@timing_decorator
def classify_product(query: str) -> str:
    """
    Hàm này để phân loại sản phẩm dựa vào câu hỏi của người dùng.

    Args:
        - query: câu hỏi của người dùng
    Return:
        - trả về ID của sản phẩm
    """

    prompt_template = PromptTemplate(
        input_variables=['query'],
        template=PROMPT_CLF_PRODUCT
    ).format(query=query)

    llm_with_output = ModelLoader().load_rag_model().with_structured_output(ClassfifyProduct)
    product_id = llm_with_output.invoke(prompt_template).ID
    return product_id