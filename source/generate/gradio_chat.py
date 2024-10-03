import time
from typing import Dict, Tuple
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from source.retriever.chroma.retriever import Retriever
from source.router.router import decision_search_type, classify_product
from source.retriever.elastic_search import  search_db, classify_intent
from source.similar_product.searcher import SimilarProductSearchEngine
from source.model.loader import ModelLoader
from source.prompt.template import PROMPT_HISTORY, PROMPT_HEADER, PROMPT_CHATCHIT, PROMPT_ORDER
from utils import GradeReWrite, timing_decorator
from configs.config_system  import SYSTEM_CONFIG


memory = ConversationBufferWindowMemory(memory_key="chat_history", k=3)
def get_history() -> str:
    """Retrieve chat history."""
    history = memory.load_memory_variables({})
    return history['chat_history']


@timing_decorator
def rewrite_query(query: str, history: str) -> str: 
    
    """
    Sử dụng LLM để viết lại câu hỏi của người dùng thành 1 câu mới dựa vào lịch sử trước đó và câu hỏi hiện tại.

    Arg:
        - query: câu hỏi của người dùng
        - history: lịch sử của người dùng
    Return:
        - trả về câu hỏi được viết lại.
    """

    llm_with_output = ModelLoader().load_rag_model().with_structured_output(GradeReWrite)
    query_rewrite = llm_with_output.invoke(PROMPT_HISTORY.format(question=query, chat_history=history)).rewrite
    
    return query_rewrite

@timing_decorator
def chat_with_history(query: str, history) -> Tuple[str, str]:
    """
    Hàm này để trả lời câu hỏi của người dùng theo flow: get_history + query-> rewrite_query -> router -> get_context OR search_db OR out_text -> LLM -> response

    Args: 
        - query: câu hỏi của người dùng
    Return:
        Dictionary chứa các thông tin sau:
            - type: loại câu hỏi
            - out_text: câu trả lời của chatbot
            - extract_similarity: trả về True nếu câu hỏi là extract_similarity
            - extract_inventory: trả về True nếu câu hỏi là extract
    """

    history_conversation = get_history()
    query_rewrited = rewrite_query(query=query, history=history_conversation)
    type = decision_search_type(query_rewrited) # sử dụng function calling để gọi các hàm custom.
    results = {"type": type, "out_text": None, "extract_similarity": False}

    PROMPT_HEADER_TEMPLATE = PromptTemplate(
        input_variables=['context', 'question'],
        template=PROMPT_HEADER)
    rag_chain = PROMPT_HEADER_TEMPLATE | ModelLoader().load_rag_model() | StrOutputParser()

    if type == "SIMILARITY": # sản phẩm tương tự
        product_name = type.split("|")[1].strip()
        engine = SimilarProductSearchEngine()
        response = engine.invoke(query=query_rewrited, product_name=product_name)
        results['out_text'] = response
    
    elif type == "ORDER":
        PROMPT_TEMPLATE = PromptTemplate(
            input_variables=['question'],
            template=PROMPT_ORDER
        )

        chain = PROMPT_TEMPLATE | ModelLoader().load_rag_model() | StrOutputParser()
        response = chain.invoke({"question": query_rewrited})
        results['out_text'] = response


    elif type == "TEXT": # chroma db search
        product_id = classify_product(query=query_rewrited)

        if product_id == -1: # không phân loại được sản phẩm
            template = PromptTemplate(
                input_variables=['question'],
                template=PROMPT_CHATCHIT
            ).format(question=query_rewrited)
            response = ModelLoader().load_chatchit_model().invoke(template).content
        else:
            db_name = SYSTEM_CONFIG.ID_2_NAME_PRODUCT[product_id]
            context = Retriever().get_context(query=query_rewrited, product_name=db_name) # thông tin điều hòa liên quan tới câu query
            response = rag_chain.invoke({'context': context, 
                                        'question': query_rewrited})
        results['out_text'] = response 

    else: # elastic search
        demands = classify_intent(query_rewrited)
        print("= = = = result few short = = = =:", demands)
        response_elastic, products_info = search_db(demands)
        # print(response_elastic)
        response = rag_chain.invoke({'context': response_elastic, 
                                     'question': query_rewrited})
        results['out_text'] = response
    
    memory.chat_memory.add_user_message(query_rewrited)
    memory.chat_memory.add_ai_message(results['content'])
    if isinstance(history, list):
        history.append((query, results['out_text']))

    return "", history



@timing_decorator
def chat_with_history_copy(query: str) -> str:
    """
    Hàm này để trả lời câu hỏi của người dùng theo flow: get_history + query-> rewrite_query -> router -> get_context OR search_db OR out_text -> LLM -> response

    Args: 
        - query: câu hỏi của người dùng
    Return:
        Dictionary chứa các thông tin sau:
            - type: loại câu hỏi
            - out_text: câu trả lời của chatbot
            - extract_similarity: trả về True nếu câu hỏi là extract_similarity
            - extract_inventory: trả về True nếu câu hỏi là extract
    """

    results = {
        "products": [], "terms": [], "content": "",
        "status": 200, "message": "", "time_processing": "",
    }

    history_conversation = get_history()
    query_rewrited = rewrite_query(query=query, history=history_conversation)
    type = decision_search_type(query_rewrited) # sử dụng function calling để gọi các hàm custom.
    results = {"type": type, "out_text": None, "extract_similarity": False}

    PROMPT_HEADER_TEMPLATE = PromptTemplate(
        input_variables=['context', 'question'],
        template=PROMPT_HEADER)
    rag_chain = PROMPT_HEADER_TEMPLATE | ModelLoader().load_rag_model() | StrOutputParser()

    if type == "SIMILARITY": # sản phẩm tương tự
        product_name = type.split("|")[1].strip()
        engine = SimilarProductSearchEngine()
        response = engine.invoke(query=query_rewrited, product_name=product_name)
        results['out_text'] = response
    
    elif type == "ORDER":
        PROMPT_TEMPLATE = PromptTemplate(
            input_variables=['question'],
            template=PROMPT_ORDER
        )

        chain = PROMPT_TEMPLATE | ModelLoader().load_rag_model() | StrOutputParser()
        response = chain.invoke({"question": query_rewrited})
        results['out_text'] = response


    elif type == "TEXT": # chroma db search
        product_id = classify_product(query=query_rewrited)

        if product_id == -1: # không phân loại được sản phẩm
            template = PromptTemplate(
                input_variables=['question'],
                template=PROMPT_CHATCHIT
            ).format(question=query_rewrited)
            response = ModelLoader().load_chatchit_model().invoke(template).content
        else:
            db_name = SYSTEM_CONFIG.ID_2_NAME_PRODUCT[product_id]
            context = Retriever().get_context(query=query_rewrited, product_name=db_name) # thông tin điều hòa liên quan tới câu query
            response = rag_chain.invoke({'context': context, 
                                        'question': query_rewrited})
        results['out_text'] = response 

    else: # elastic search
        demands = classify_intent(query_rewrited)
        print("= = = = result few short = = = =:", demands)
        response_elastic, products_info = search_db(demands)
        # print(response_elastic)
        response = rag_chain.invoke({'context': response_elastic, 
                                     'question': query_rewrited})
        results['out_text'] = response
    
    memory.chat_memory.add_user_message(query_rewrited)
    memory.chat_memory.add_ai_message(results['content'])


    return results['out_text']