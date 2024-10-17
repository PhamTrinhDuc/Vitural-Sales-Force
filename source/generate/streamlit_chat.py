import os
import streamlit as st
from typing import Optional
from icecream import ic
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from source.retriever.chroma.retriever import Retriever
from source.router.router import decision_search_type, classify_product
from source.retriever.elastic_search import search_db, classify_intent
from source.similar_product.searcher import SimilarProductSearchEngine
from source.model.loader import ModelLoader
from source.prompt.template import PROMPT_HEADER, PROMPT_HISTORY, PROMPT_ORDER, PROMPT_CHATCHIT
from utils.timekeeper import timing_decorator
from utils.utils_users import UserHelper
from utils.schemas import GradeReWrite
from configs.config_system  import SYSTEM_CONFIG
from logs.logger import set_logging_terminal

logger_terminal = set_logging_terminal()
CONVERSATION_PATH = SYSTEM_CONFIG.CONVERSATION_STORAGE
ASSISTANT_AVT = "static/avt_bot.png"
USER_AVT = "static/avt_user.png"


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
    logger_terminal.info(f"Query User: {query}")

    llm_with_output = SYSTEM_CONFIG.load_rag_model().with_structured_output(GradeReWrite)
    query_rewrite = llm_with_output.invoke(PROMPT_HISTORY.format(question=query, chat_history=history)).rewrite
    logger_terminal.info(f"Query Rewrite: {query_rewrite}")
    
    return query_rewrite


@timing_decorator
def chat_interface(query: int, 
                   user_name: Optional[str] = None) -> str:
    """

    Hàm chính để tương tác với người dùng, dựa vào query, user_name, seasion_id của người dùng, đưa qua pipeline và trả về câu trả lời.
    Args:
        - query: câu hỏi của người dùng
        - user_name: tên người dùng
        - seasion_id: id cuộc hội thoại của người dùng.
    Returns:
        - trả về câu trả lời cho người dùng.

    """
    history_conversation = UserHelper().load_conversation(user_name=user_name)
    query_rewrited = rewrite_query(query=query, history=history_conversation)
    print(query_rewrited)

    type = decision_search_type(query_rewrited) # sử dụng function calling để gọi các hàm custom.
    print(type)
    results = {"type": type, "out_text": None, "extract_similarity": False}

    PROMPT_HEADER_TEMPLATE = PromptTemplate(
        input_variables=['context', 'question'],
        template=PROMPT_HEADER)
    rag_chain = PROMPT_HEADER_TEMPLATE | ModelLoader().load_rag_model() | StrOutputParser()

    if type.split("|")[0].strip() == "SIMILARITY": # sản phẩm tương tự
        product_name = type.split("|")[1].strip()
        engine = SimilarProductSearchEngine()
        response = engine.invoke(query=query_rewrited, product_name=product_name)
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
    
    elif type == "ORDER":
        PROMPT_TEMPLATE = PromptTemplate(
            input_variables=['question'],
            template=PROMPT_ORDER
        )

        chain = PROMPT_TEMPLATE | ModelLoader().load_rag_model() | StrOutputParser()
        response = chain.invoke({"question": query_rewrited})
        results["out_text"] = response

    else: # elastic search
        # instruction_answer = Retriever().get_context(query=query_rewrited, db_name="fqa")
        demands = classify_intent(query_rewrited)
        print("= = = = result few short = = = =:", demands)
        response_elastic, products_info = search_db(demands)
        ic(response_elastic)
        ic("=" * 100)
        response = rag_chain.invoke({'context': response_elastic, 
                                     'question': query_rewrited})
        results['out_text'] = response
    
    return results["out_text"]

def display_conversation(user_name: str, container):  
    """

    Hiện thại đoạn hội thoại giữa người dùng và chatbot trên giao diện streamlit và lưu lại đoạn hội thoại.
    Args:
        - user_name: tên người dùng
        - seasion_id: id cuộc hội thoại của người dùng.
        - container: container để hiện thị hội thoại.

    """
    if not os.path.exists(CONVERSATION_PATH) or os.path.getsize(CONVERSATION_PATH) == 0:
        with container:
            with st.chat_message(name="assistant", avatar=ASSISTANT_AVT):
                st.markdown(f"Xin chào anh/chị, em là CHATBOT VCC được phát triển bởi VCC. Em sẽ tư vấn cho anh chị các sản phẩm điều hòa bên em. Hãy nói chuyện với em để bắt đầu nhé!")
    prompt = st.chat_input("Nhập tin nhắn của bạn tại đây !!")
    if prompt:
        with container:
            with st.chat_message(name="user", avatar=USER_AVT):
                st.markdown(prompt)
            response = chat_interface(query=prompt, user_name=user_name)
            with st.chat_message(name="assistant", avatar=ASSISTANT_AVT):
                st.markdown(response)

        # persit conversation
        UserHelper().save_conversation(user_name=user_name, 
                                       query=prompt, 
                                       response=response)