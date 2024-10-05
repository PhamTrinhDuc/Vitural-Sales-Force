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
    query_rewriten = rewrite_query(query=query, history=history_conversation)
    print("Question: ",query_rewriten)

    results_type = decision_search_type(query_rewriten) # sử dụng function calling để gọi các hàm custom.
    type_search = results_type['content']
    print("Type: ", results_type['content'])

    llm_rag = ModelLoader().load_rag_model()
    llm_chat_chit = ModelLoader().load_chatchit_model()
    user_info = {
        'name': 'Phương Ly',
        'phone_number': '0987654321',
        'address': 'Hà Nội'
    }


    PROMPT_HEADER_TEMPLATE = PromptTemplate(
        input_variables=['context', 'question', 'user_info'],
        template=PROMPT_HEADER)
    rag_chain = PROMPT_HEADER_TEMPLATE | llm_rag | StrOutputParser()

    if "SIMILARITY" in type_search: # sản phẩm tương tự
        product_name = type_search.split("|")[1].strip()
        engine = SimilarProductSearchEngine(product_name)
        out_text = engine.invoke(query=query_rewriten)
    
    elif "ORDER" in type_search:
        PROMPT_TEMPLATE = PromptTemplate(
            input_variables=['question', 'user_info'],
            template=PROMPT_ORDER
        )
        chain = PROMPT_TEMPLATE | llm_rag | StrOutputParser()
        out_text = chain.invoke({"question": query_rewriten, "user_info": user_info})


    elif "TEXT" in type_search: # chroma db search
        results_cls = classify_product(query=query_rewriten)

        product_id = results_cls['content']
        print(product_id)

        if product_id == -1: # không phân loại được sản phẩm
            template = PromptTemplate(
                input_variables=['question', 'user_info'],
                template=PROMPT_CHATCHIT
            ).format(question=query_rewriten)
            response = llm_chat_chit.invoke(template).content
        else:
            db_name = SYSTEM_CONFIG.ID_2_NAME_PRODUCT[product_id]
            context = Retriever().get_context(query=query_rewriten, product_name=db_name) # thông tin điều hòa liên quan tới câu query
            response = rag_chain.invoke({'context': context, 
                                        'question': query_rewriten,
                                        'user_info': user_info})
        out_text = response 

    else: # elastic search
        demands = classify_intent(query_rewriten)
        print("= = = = result few short = = = =:", demands)
        response_elastic, products_info = search_db(demands)
        # print(response_elastic)
        out_text = rag_chain.invoke({'context': response_elastic, 
                                     'question': query_rewriten,
                                     'user_info': user_info})
    
    memory.chat_memory.add_user_message(query_rewriten)
    memory.chat_memory.add_ai_message(out_text)
    if isinstance(history, list):
        history.append((query, out_text))

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

    history_conversation = get_history()
    query_rewriten = rewrite_query(query=query, history=history_conversation)
    print("Question: ",query_rewriten)

    results_type = decision_search_type(query_rewriten) # sử dụng function calling để gọi các hàm custom.
    type_search = results_type['content']
    print("Type: ", results_type['content'])

    llm_rag = ModelLoader().load_rag_model()
    llm_chat_chit = ModelLoader().load_chatchit_model()
    user_info = {
        'name': 'Phương Ly',
        'phone_number': '0987654321',
        'address': 'Hà Nội'
    }


    PROMPT_HEADER_TEMPLATE = PromptTemplate(
        input_variables=['context', 'question', 'user_info'],
        template=PROMPT_HEADER)
    rag_chain = PROMPT_HEADER_TEMPLATE | llm_rag | StrOutputParser()

    if "SIMILARITY" in type_search: # sản phẩm tương tự
        product_name = type_search.split("|")[1].strip()
        engine = SimilarProductSearchEngine(product_name)
        out_text = engine.invoke(query=query_rewriten)
    
    elif "ORDER" in type_search:
        PROMPT_TEMPLATE = PromptTemplate(
            input_variables=['question', 'user_info'],
            template=PROMPT_ORDER
        )
        chain = PROMPT_TEMPLATE | llm_rag | StrOutputParser()
        out_text = chain.invoke({"question": query_rewriten, "user_info": user_info})


    elif "TEXT" in type_search: # chroma db search
        results_cls = classify_product(query=query_rewriten)

        product_id = results_cls['content']
        print(product_id)

        if product_id == -1: # không phân loại được sản phẩm
            template = PromptTemplate(
                input_variables=['question', 'user_info'],
                template=PROMPT_CHATCHIT
            ).format(question=query_rewriten)
            response = llm_chat_chit.invoke(template).content
        else:
            db_name = SYSTEM_CONFIG.ID_2_NAME_PRODUCT[product_id]
            context = Retriever().get_context(query=query_rewriten, product_name=db_name) # thông tin điều hòa liên quan tới câu query
            response = rag_chain.invoke({'context': context, 
                                        'question': query_rewriten,
                                        'user_info': user_info})
        out_text = response 

    else: # elastic search
        demands = classify_intent(query_rewriten)
        print("= = = = result few short = = = =:", demands)
        response_elastic, products_info = search_db(demands)
        # print(response_elastic)
        out_text = rag_chain.invoke({'context': response_elastic, 
                                     'question': query_rewriten,
                                     'user_info': user_info})
    
    memory.chat_memory.add_user_message(query_rewriten)
    memory.chat_memory.add_ai_message(out_text)
    
    return out_text