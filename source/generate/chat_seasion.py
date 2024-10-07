import os
import re
import markdown
import logging
import pandas as pd
from typing import Dict, Any, List
from langchain_core.prompts import PromptTemplate
from langchain_community.callbacks.manager import get_openai_callback
from api.deep_link import create_short_link
from source.retriever.chroma.retriever import Retriever
from source.router.router import decision_search_type, classify_product
from source.retriever.elastic_search import search_db, classify_intent
from source.similar_product.searcher import SimilarProductSearchEngine
from source.model.loader import ModelLoader
from source.prompt.template import PROMPT_HISTORY, PROMPT_HEADER, PROMPT_CHATCHIT, PROMPT_ORDER
from utils import GradeReWrite, UserHelper, timing_decorator
from configs.config_system import SYSTEM_CONFIG

# Helper functions

class HelperPiline:
    def __init__(self):
        pass
    
    def _product_seeking(self, output_from_llm: str, dataframe: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Get info product in output from llm.
        Args:
            - output_from_llm: output of llm.
            - path_df: data frame constain list product
        Returns:
            - results: product information obtained
        """
        link_header = SYSTEM_CONFIG.LINK_SEVER
        result = []
        for index, row in dataframe.iterrows():
            if any(str(item).lower() in output_from_llm.lower() for item in (row['product_name'], row['product_info_id'])):
                product = {
                    "product_id": int(str(row['product_info_id']).replace(',', '')), # không ổn
                    "product_name": row['product_name'],
                    "link_image": link_header + row['file_path']
                }
                result.append(product)
        return result
    
    def _format_to_HTML(self, markdown_text: str) -> str:
        """Converts a given markdown text from output llm to HTML format.
        Args:
            markdown_text (str): The markdown text to be converted.
        Returns:
            str: The converted HTML text.
        """
        md = markdown.Markdown(extensions=['tables'])
        html_output = md.convert(markdown_text)
        return html_output
    
    def _add_short_link(self, output_from_llm: str, product_info: List[Dict[str, Any]]) -> str:

        """Adds a short link to the output from LLM if a quantity is found in the output.
        Args:
            output_from_llm (str): The output string from the LLM which may contain a quantity in a specific format.
        Returns:
            str: The modified output string with an added short link if a quantity is found, otherwise returns the original output string.
        """
        if len(product_info) == 0: # nếu không tìm thấy sản phẩm
            return output_from_llm
        
        pattern = r'<li><strong>Số lượng:</strong>\s*(\d+)</li>'
        match = re.search(pattern, output_from_llm)
        quantity = match.group(1) if match else None
        print(quantity)
        if quantity: # nếu tìm thấy số lượng
            short_link = create_short_link(product_id=product_info['product_id'], quantity=quantity)
            if short_link:
                return f"""{output_from_llm} \n <hr /> \n <p>Nếu thông tin đã đúng vui lòng ấn <a href={short_link['shortLink']} style="color: blue;">Xác nhận</a> để qua trang đặt hàng giúp em nhé. 😊</p>"""
            else:
                return output_from_llm


class Pipeline:
    def __init__(self):
        self.LLM_RAG = ModelLoader().load_rag_model()
        self.LLM_CHAT_CHIT = ModelLoader().load_chatchit_model()
        self.USER_HELPER =  UserHelper()  
        self.PIPELINE_HELPER = HelperPiline()     
        self.user_info = None
        
    def _execute_llm_call(self, llm, prompt, structured_output=None):

        """Executes a call to a language model (LLM) with the given prompt and optional structured output.
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
    
    def _rewrite_query(self, query: str, history: str) -> Dict[str, Any]:
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
                self.LLM_RAG, 
                PROMPT_HISTORY.format(question=query, chat_history=history),
                GradeReWrite
            )
        except Exception as e :
            logging.error("REWRITE QUERY ERROR: " + str(e))
            return {"content": query, "total_token": 0, 'total_cost': 0}


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
            response['content'] = self.PIPELINE_HELPER._format_to_HTML(markdown_text=response['content'])
        except Exception as e:
            response = {"content": "", "total_token": 0, 'total_cost': 0}
            logging.error("SIMILARITY QUERY ERROR: " + str(e))
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
            prompt = PromptTemplate(input_variables=['question', 'user_info'], template=PROMPT_ORDER)
            response =  self._execute_llm_call(self.LLM_RAG, prompt.format(question=query, user_info=self.user_info))
            response['content'] = self.PIPELINE_HELPER._format_to_HTML(markdown_text=response['content'])
            
            response['products'] = self.PIPELINE_HELPER._product_seeking(output_from_llm=response['content'], dataframe=pd.read_excel(SYSTEM_CONFIG.ALL_PRODUCT_FILE_CSV_STORAGE))
            if len(response['products']) > 0: # nếu có sản phẩm trong câu trả lời
                print("PRODUCTS: ", response['products'])
                response['content'] = self.PIPELINE_HELPER._add_short_link(output_from_llm=response['content'], product_info=response['products'][0])
                
        except Exception as e:
            response = {"content": "", "total_token": 0, 'total_cost': 0}
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
        try:
            if product_id == -1:
                template = PromptTemplate(input_variables=['question', 'user_info'], template=PROMPT_CHATCHIT)
                response = self._execute_llm_call(self.LLM_CHAT_CHIT, template.format(question=query, user_info=self.user_info))
            else:
                db_name = SYSTEM_CONFIG.ID_2_NAME_PRODUCT[product_id]
                context = Retriever().get_context(query=query, product_name=db_name)
                prompt = PromptTemplate(input_variables=['context', 'question', 'user_info'], template=PROMPT_HEADER)
                response = self._execute_llm_call(self.LLM_RAG, prompt.format(context=context, question=query, user_info=self.user_info))
                
                specified_product_data  = pd.read_csv(os.path.join(SYSTEM_CONFIG.SPECIFIC_PRODUCT_FOLDER_CSV_STORAGE, db_name + ".csv"))
                response['products'] = self.PIPELINE_HELPER._product_seeking(output_from_llm=response['content'], dataframe=specified_product_data)
        
            response['content'] = self.PIPELINE_HELPER._format_to_HTML(markdown_text=response['content'])
            response['total_token'] += result_classify['total_token']
            response['total_cost'] += result_classify['total_cost']
        except Exception as e:
            response = {"content": "", "total_token": 0, 'total_cost': 0}
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
            demands = classify_intent(query)
            response_elastic, products_info = search_db(demands)

            prompt = PromptTemplate(input_variables=['context', 'question', 'user_info'], template=PROMPT_HEADER)
            response = self._execute_llm_call(self.LLM_RAG, prompt.format(context=response_elastic, question=query, user_info=self.user_info))
            
            response['content'] = self.PIPELINE_HELPER._format_to_HTML(markdown_text=response['content'])
            response['products'] = self.PIPELINE_HELPER._product_seeking(output_from_llm=response['content'], dataframe=pd.DataFrame(products_info))
        except Exception as e:
            response = {"content": "", "total_token": 0, 'total_cost': 0}
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
    ) :
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
        self.USER_HELPER.save_users(UserInfor)
        self.user_info = self.USER_HELPER.get_user_info(UserInfor['phone_number'])

        storage_info_output = {
            "products": [], "terms": [], "content": "", "total_token": 0, 'total_cost': 0,
            "status": 200, "message": "",
        }

        try:
            history_conversation = self.USER_HELPER.load_conversation(conv_user=UserInfor['phone_number'], id_request=IdRequest)
            # print("HISTORY: ", history_conversation)
            result_rewriten = self._rewrite_query(query=InputText, history=history_conversation)
            query_rewritten = result_rewriten['content']
            print("QUERY REWRITE:", query_rewritten)
            storage_info_output['total_token'] += result_rewriten['total_token']
            storage_info_output['total_cost'] += result_rewriten['total_cost']

            result_type = decision_search_type(result_rewriten['content'])
            search_type = result_type['content']
            storage_info_output['total_token'] += result_type['total_token']
            storage_info_output['total_cost'] += result_type['total_cost']
            
            print("TYPE SEARCH:", search_type)
            if "SIMILARITY" in search_type: 
                product_name = search_type.split("|")[1].strip()
                results = self._handle_similarity_search(query_rewritten, product_name, self.user_info)
            elif "ORDER" in search_type:
                results = self._handle_order_query(query_rewritten)
            elif "TEXT" in search_type:
                results = self._handle_text_query(query_rewritten)
            else:  # Elastic search
                results = self._handle_elastic_search(query_rewritten)

            storage_info_output.update({
                'content': results['content'],
                'total_token': storage_info_output['total_token'] + results['total_token'],
                'total_cost': storage_info_output['total_cost'] + results['total_cost'],
                'products': results.get('products', []),
                'message': "Request processed successfully."
            })
            self.USER_HELPER.save_conversation(phone_number=UserInfor['phone_number'], query=query_rewritten, id_request=IdRequest, response=storage_info_output['content'])
        
        except Exception as e:
            storage_info_output.update({"status": 500, "message": f"Error processing request: {e}"})
            logging.error("CHAT SESSION ERROR: " + str(e))
        return storage_info_output

if __name__ == "__main__":
    pass