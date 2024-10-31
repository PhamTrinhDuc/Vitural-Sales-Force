import os
import time
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
from langchain_core.globals import set_llm_cache
from langchain_core.prompts import PromptTemplate
from langchain_core.caches import InMemoryCache
from source.model.loader import ModelLoader
from langchain_community.callbacks.manager import get_openai_callback
from source.retriever.chroma.retriever import ChromaQueryEngine
from source.router.router import decision_search_type, classify_product
# from source.retriever.elastic_search import ElasticQueryEngine, classify_intent
from source.retriever.elastic_search.query_engine_cp import ElasticQueryEngine
from source.retriever.elastic_search.extract_specifications import extract_info
from source.similar_product.searcher import SimilarProductSearchEngine
from source.prompt.template import PROMPT_HISTORY, PROMPT_HEADER, PROMPT_CHATCHIT, PROMPT_ORDER
from utils import GradeReWrite, UserHelper, timing_decorator, PostgreHandler, HelperPiline
from configs.config_system import LoadConfig


cache = InMemoryCache()
set_llm_cache(cache)

class Pipeline:
    def __init__(self, member_code: str):
        self.member_code = member_code
        self.llm_rag = ModelLoader.load_rag_model()
        self.llm_chatchit = ModelLoader.load_chatchit_model()
        self.els_seacher = ElasticQueryEngine(member_code=self.member_code)
        self.chroma_seacher = ChromaQueryEngine(member_code=self.member_code)
        self.user_helper =  UserHelper()  
        self.pipeline_helper = HelperPiline()  
        self.db_logger = PostgreHandler()   
        self.user_info = None
        
    def _execute_llm_call(self, llm, prompt, structured_output=None):

        """
        
        Executes a call to a language model (LLM) with the given prompt and optional structured output.
        Args:
            llm: OpenAI: The language model instance to be called.
            prompt (str): The input prompt to be sent to the LLM.
            structured_output (Basemodel): An optional structured output format for the LLM response.
        Returns:
            dict: A dictionary containing the following keys:
            - "content": The content of the LLM response.
            - "total_token": The total number of tokens used in the LLM call.
            - "cost": The total cost of the LLM call.

        """
        with get_openai_callback() as cb:
            if structured_output:
                llm_with_output = llm.with_structured_output(structured_output)
                response = llm_with_output.invoke(prompt).rewrite 
            else:
                response = llm.invoke(prompt)
            return {
                "content": response.content if hasattr(response, 'content') else response,
                "total_token": cb.total_tokens,
                'total_cost': cb.total_cost
            }    
    
    def _rewrite_query(self, query: str, history: list) -> Dict[str, Any]:
        """

        Rewrite the user query based on chat history.

        Args:
            query (str): The original user query.
            history (str): The chat history.

        Returns:
            str: The rewritten query.

        """
        try:
            return self._execute_llm_call(
                self.llm_rag, 
                PROMPT_HISTORY.format(question=query, chat_history=history),
                GradeReWrite
            )
        except Exception as e :
            logging.error("REWRITE QUERY ERROR: " + str(e))
            response = {"content": LoadConfig.SYSTEM_MESSAGE['error_system'], 
                        "total_token": 0, 'total_cost': 0,
                        "status": 500, 
                        "message": f"QUERY REWRITE ERR: {str(e)}"}
            return response

    def _handle_similarity_search(self, query: str, product_name: str, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """

        Handle similarity-based product search.

        Args:
            query (str): The user's query.
            product_name (str): The name of the product to search for.

        Returns:
            Dict[str, Any]: The search results and token usage.

        """
        try:
            engine = SimilarProductSearchEngine(product_find=product_name, user_info=user_info)
            response =  self._execute_llm_call(engine,  query)
            response['content'] = self.pipeline_helper._format_to_HTML(markdown_text=response['content'])
        except Exception as e:
            response = {"content": LoadConfig.SYSTEM_MESSAGE['error_system'], 
                        "total_token": 0, 'total_cost': 0,
                        "status": 500, 
                        "message": f"SIMILARITY QUERY ERROR: {str(e)}"}
        return response

    def _handle_order_query(self, query: str) -> Dict[str, Any]:
        """

        Handles an order query by generating a response using a language model and processing the response.
        Args:
            query (str): The order query string.
        Returns:
            Dict[str, Any]: A dictionary containing the processed response content, total tokens used, and total cost.
        Logic:
        1. Creates a prompt using the provided query and user information.
        2. Executes a call to the language model with the generated prompt.
        3. Formats the response content to HTML.
        4. Adds a short link to the response content based on the product information.
        5. Extracts product information from the response content using a product seeking pipeline.
        6. Handles any exceptions by logging the error and returning a default response.
        
        """
        try:
            all_product_data = pd.read_excel(LoadConfig.ALL_PRODUCT_FILE_MERGED_STORAGE.format(member_code=self.member_code))
            original_product_info = self.pipeline_helper._double_check(question=query, dataframe=all_product_data)
            prompt = PromptTemplate(input_variables=['question', 'user_info', 'original_product_info'], template=PROMPT_ORDER)
            response =  self._execute_llm_call(self.llm_rag, prompt.format(question=query, 
                                                                           user_info=self.user_info, 
                                                                           original_product_info = original_product_info))
            response['content'] = self.pipeline_helper._format_to_HTML(markdown_text=response['content'])
            
            response['products'] = self.pipeline_helper._product_seeking(output_from_llm=response['content'], 
                                                                         query_rewritten=query, 
                                                                         dataframe=all_product_data)
            response['product_confirms'] = self.pipeline_helper._product_confirms(output_from_llm=response['content'], 
                                                                                  query_rewritten=query, 
                                                                                  dataframe=all_product_data)
                
        except Exception as e:
            response = {"content": LoadConfig.SYSTEM_MESSAGE['error_system'], 
                        "total_token": 0, 'total_cost': 0,
                        "status": 500, 
                        "message": f"Error processing request: {str(e)}"}
            logging.error("ORDER QUERY ERROR: " + str(e))
        return response 

    def _handle_text_query(self, query: str) -> Dict[str, Any]:
        """

        Handle text-based queries.
        Args:
            query (str): The user's query.
            rag_chain: The RAG chain for processing.
        Returns:
            Dict[str, Any]: The response and token usage.
        
        """
        result_classify = classify_product(query=query)
        product_id = result_classify['content']
        print("PRODUCT ID: ", product_id)
        try:
            if product_id == -1:
                template = PromptTemplate(input_variables=['question', 'user_info'], template=PROMPT_CHATCHIT)
                response = self._execute_llm_call(self.llm_chatchit, template.format(question=query, user_info=self.user_info))
            else:
                db_name = LoadConfig.ID_2_NAME_PRODUCT[product_id]
                print("DB NAME: ", db_name)
                context = self.chroma_seacher.get_context(query=query, product_name=db_name)
                prompt = PromptTemplate(input_variables=['context', 'question', 'user_info'], template=PROMPT_HEADER)
                response = self._execute_llm_call(self.llm_rag, prompt.format(context=context, 
                                                                              question=query, 
                                                                              user_info=self.user_info))
                
                specified_product_data_path = os.path.join(LoadConfig.SPECIFIC_PRODUCT_FOLDER_CSV_STORAGE.format(member_code=self.member_code), db_name + ".csv")
                specified_product_data  = pd.read_csv(os.path.join(specified_product_data_path))
                response['products'] = self.pipeline_helper._product_seeking(output_from_llm=response['content'], 
                                                                             query_rewritten=query, 
                                                                             dataframe=specified_product_data)
                response['product_name'] = db_name
                
            response['content'] = self.pipeline_helper._format_to_HTML(markdown_text=response['content'])
            response['total_token'] += result_classify['total_token']
            response['total_cost'] += result_classify['total_cost']
        except Exception as e:
            response = {"content": LoadConfig.SYSTEM_MESSAGE['error_system'], 
                        "total_token": 0, 'total_cost': 0,
                        "status": 500, 
                        "message": f"Error processing request: {str(e)}"}
            logging.error("TEXT QUERY ERROR: " + str(e))
        return response

    def _handle_elastic_search(self, query: str) -> Dict[str, Any]:
        """

        Handle queries using elastic search.

        Args:
            query (str): The user's query.
            rag_chain: The RAG chain for processing.

        Returns:
            Dict[str, Any]: The response and product information and token usage.
        
        """
        try:
            demands = extract_info(query)
            response_elastic, products_info = self.els_seacher.search_db(demands)
            if not response_elastic: # nếu els không search được thì chuyển sang text
                response = self._handle_text_query(query=query)
                return response

            prompt = PromptTemplate(input_variables=['context', 'question', 'user_info'], template=PROMPT_HEADER)
            response = self._execute_llm_call(self.llm_rag, prompt.format(context=response_elastic, 
                                                                          question=query, 
                                                                          user_info=self.user_info))
            
            response['product_name'] = demands['object']
            response['content'] = self.pipeline_helper._format_to_HTML(markdown_text=response['content'])
            response['products'] = self.pipeline_helper._product_seeking(output_from_llm=response['content'], 
                                                                         query_rewritten= query, 
                                                                         dataframe=pd.DataFrame(products_info))
        except Exception as e:
            response = {"content": LoadConfig.SYSTEM_MESSAGE['error_system'], 
                        "total_token": 0, 'total_cost': 0,
                        "status": 500, 
                        "message": f"Error processing request: {str(e)}"}
            logging.error("ELASTIC SEARCH QUERY ERROR: " + str(e))
        return response

    # Main function
    @timing_decorator
    def chat_session(
        self,
        InputText = None,
        IdRequest = None,
        NameBot = None,
        Voice = None,
        Image =  None,
        UserInfor = None,
    ):
        """

        Main function to interact with the user, process the query through the pipeline, and return an answer.
        Args:
            InputText (Optional[str]): The user's query.
            id_request (Optional[str]): The session ID for the user's conversation.
            name_bot (Optional[str]): The name of the bot.
            voice (Optional[Any]): Voice data (if applicable
            image (Optional[Any]): Image data (if applicable).
        Returns:
            Dict[str, Any]: A dictionary containing the response and related information.
        
        """
        self.user_helper.save_users(UserInfor)
        self.user_info = self.user_helper.get_user_info(UserInfor['phone_number'])

        storage_info_output = {
            "product_name": None,
            "products": [], "product_confirms": [], "terms": [], "content": "", "total_token": 0, 'total_cost': 0,
            "status": 200, "message": None, "time_processing": None,
        }
        time_in = time.time()
        try:
            history_conversation = self.user_helper.load_conversation(conv_user=UserInfor['phone_number'], id_request=IdRequest)
            # print("HISRORY", history_conversation)
            result_rewriten = self._rewrite_query(query=InputText, history=history_conversation)
            query_rewritten = result_rewriten['content']
            print("QUERY REWRITE:", query_rewritten)
            storage_info_output['total_token'] += result_rewriten['total_token']
            storage_info_output['total_cost'] += result_rewriten['total_cost']

            result_type = decision_search_type(result_rewriten['content'])
            search_type = result_type['content']
            print("TYPE SEARCH:", search_type)
            storage_info_output['total_token'] += result_type['total_token']
            storage_info_output['total_cost'] += result_type['total_cost']
            
            if "SIMILARITY" in search_type: 
                product_name = search_type.split("|")[1].strip()
                results = self._handle_similarity_search(query_rewritten, product_name, self.user_info)
            elif "ORDER" in search_type:
                results = self._handle_order_query(query_rewritten)
            elif "TEXT" in search_type:
                results = self._handle_text_query(query_rewritten)
            else:  # Elastic search
                results = self._handle_elastic_search(query_rewritten)

            # if len(results.get("product_confirms", [])) > 0:
            #     results['content'] += "<hr />🌟 Qúy khách đã sẵn sàng sở hữu sản phẩm tuyệt vời này chưa? Hãy bấm nút 'Mua hàng' ngay để  tiến hành thanh toán! 🛒✨. Viettel Construction xin chân thành cảm ơn !!"
            
            storage_info_output.update({
                'product_name': results.get("product_name", None),
                'content': results['content'],
                'total_token': storage_info_output['total_token'] + results['total_token'],
                'total_cost': storage_info_output['total_cost'] + results['total_cost'],
                'product_confirms': results.get('product_confirms', []),
                'products': results.get('products', []),
                'message': "Request processed successfully."
            })
            self.user_helper.save_conversation(phone_number=UserInfor['phone_number'], query=InputText, id_request=IdRequest, response=results['content'])
        
        except Exception as e:
            storage_info_output.update({"content": LoadConfig.SYSTEM_MESSAGE['error_system'],
                                        "status": 500, 
                                        "message": f"Error processing request in func CHAT SESSION: {str(e)}"})
            logging.error("CHAT SESSION ERROR: " + str(e))
            
        storage_info_output['time_processing'] = time.time() - time_in
        
        # Save log to database
        try:
            self.db_logger.insert_data(
                user_name=UserInfor['name'],
                phone_number=UserInfor['phone_number'],
                object_product=storage_info_output['product_name'],
                name_bot=NameBot,
                rewritten_human=query_rewritten,
                session_id=IdRequest,
                human=InputText,
                ai=storage_info_output['content'],
                status=storage_info_output['status'],
                total_token=storage_info_output['total_token'],
                toal_cost=storage_info_output['total_cost'],
                date_request=datetime.now().strftime("%A, %d %B %Y, %H:%M:%S"),
                error_message=storage_info_output['message'],
                time_request=storage_info_output['time_processing']
            )
        except Exception as e:
            logging.error("ERROR WHILE INSERT TO DATABSE: " + str(e))
            
        return storage_info_output

if __name__ == "__main__":
    pass