import time
import markdown
import os
import pandas as pd
from typing import Dict, Optional, Any
from langchain_core.prompts import PromptTemplate
from langchain_community.callbacks.manager import get_openai_callback
from source.retriever.chroma.retriever import Retriever
from source.router.router import decision_search_type, classify_product
from source.retriever.elastic_search import search_db, classify_intent
from source.similar_product.searcher import SimilarProductSearchEngine
from source.model.loader import ModelLoader
from source.prompt.template import PROMPT_HISTORY, PROMPT_HEADER, PROMPT_CHATCHIT, PROMPT_ORDER
from utils import GradeReWrite, UserHelper, timing_decorator
from configs.config_system import SYSTEM_CONFIG

# Helper functions

class Pipline:
    def __init__(self):
        self.LLM_RAG = ModelLoader().load_rag_model()
        self.LLM_CHAT_CHIT = ModelLoader().load_chatchit_model()
        self.USER_HELPER = UserHelper()

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
                response = llm_with_output.invoke(prompt).write 
            else:
                response = llm.invoke(prompt)
            return {
                "content": response.content if hasattr(response, 'content') else response,
                "total_token": cb.total_tokens,
                'cost': cb.total_cost
            }    

    def _process_output(self, output_from_llm: str, dataframe: pd.DataFrame) -> Dict[str, Any]:
        """
        Get info product in output from llm.
        Args:
            - output_from_llm: output of llm.
            - path_df: data frame constain list product
        Returns:
            - results: product information obtained
        """
        result = []
        for index, row in dataframe.iterrows():
            if any(row['product_name'], row['product_code'], row['lifecare_price']) in output_from_llm:
                product =  {
                    "code" : "",
                    "name" : "",
                    "link" : ""
                }
                product = {
                    "code": row['product_info_id'],
                    "name": row['product_name'],
                    "link": row['file_path']
                }
                result.append(product)
        return result
    
    def _format_to_HTML(self):
        pass

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
        except Exception:
            return {"content": query, "total_token": 0, 'cost': 0}


    def _handle_similarity_search(self, query: str, product_name: str) -> Dict[str, Any]:
        """
        Handle similarity-based product search.

        Args:
            query (str): The user's query.
            product_name (str): The name of the product to search for.

        Returns:
            Dict[str, Any]: The search results and token usage.
        """
        engine = SimilarProductSearchEngine()
        return self._execute_llm_call(engine, {"query": query, "product_name": product_name})


    def _handle_order_query(self, query: str) -> Dict[str, Any]:
        """
        Handle order-related queries.

        Args:
            query (str): The user's query.

        Returns:
            str: The response to the order query and token usage.
        """
        prompt = PromptTemplate(input_variables=['question'], template=PROMPT_ORDER)
        return self._execute_llm_call(self.LLM_RAG, prompt.format(question=query))


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
        
        if product_id == -1:
            template = PromptTemplate(input_variables=['question'], template=PROMPT_CHATCHIT)
            response = self._execute_llm_call(self.LLM_CHAT_CHIT, template.format(question=query))
        else:
            db_name = SYSTEM_CONFIG.ID_2_NAME_PRODUCT[product_id]
            context = Retriever().get_context(query=query, product_name=db_name)
            prompt = PromptTemplate(input_variables=['context', 'question'], template=PROMPT_HEADER)
            response = self._execute_llm_call(self.LLM_RAG, prompt.format(context=context, question=query))
            
            specified_product_data  = pd.read_csv(os.path.join(SYSTEM_CONFIG.SPECIFIC_PRODUCT_FOLDER_CSV_DIRECTORY, db_name, ".csv"))
            response['products'] = self._process_output(output_from_llm=response, dataframe=specified_product_data)
        response['total_token'] += result_classify['total_token']
        response['cost'] += result_classify['cost']
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
        demands = classify_intent(query)
        response_elastic, products_info = search_db(demands)
        prompt = PromptTemplate(input_variables=['context', 'question'], template=PROMPT_HEADER)
        response = self._execute_llm_call(self.LLM_RAG, prompt.format(context=response_elastic, question=query))
        response['products'] = self._process_output(output_from_llm=response, dataframe=pd.DataFrame(products_info))
        return response

    # Main function

    @timing_decorator
    def chat_session(
        self,
        input_text: Optional[str],
        id_request: Optional[str],
        user_name: Optional[str],
        name_bot: Optional[str] = None,
        voice: Optional[Any] = None,
        image: Optional[Any] = None
    ) -> Dict[str, Any]:
        
        """
        Main function to interact with the user, process the query through the pipeline, and return an answer.
        Args:
            input_text (Optional[str]): The user's query.
            id_request (Optional[str]): The session ID for the user's conversation.
            user_name (Optional[str]): The name of the user.
            name_bot (Optional[str]): The name of the bot.
            voice (Optional[Any]): Voice data (if applicable).
            image (Optional[Any]): Image data (if applicable).
        Returns:
            Dict[str, Any]: A dictionary containing the response and related information.
        """

        storage_info_output = {
            "products": [], "terms": [], "content": "", "total_token": 0, 'cost': 0,
            "status": 200, "message": "",
        }

        if not input_text:
            return {**storage_info_output, "message": "No input text provided.", "status": 400}

        try:
            history_conversation = self.USER_HELPER.load_conversation(user_name=user_name, id_request=id_request)
            result_rewrite = self._rewrite_query(query=input_text, history=history_conversation)
            query_rewritten = result_rewrite['content']
            storage_info_output['total_token'] += result_rewrite['total_token']
            storage_info_output['cost'] += result_rewrite['cost']

            result_type = decision_search_type(result_rewrite['content'])
            search_type = result_type['content']
            storage_info_output['total_token'] += result_type['total_token']
            storage_info_output['cost'] += result_type['cost']

            if "SIMILARITY" in search_type: 
                product_name = search_type.split("|")[1].strip()
                results = self._handle_similarity_search(query_rewritten, product_name)
            elif "ORDER" in search_type:
                results = self._handle_order_query(query_rewritten)
            elif "TEXT" in search_type:
                results = self._handle_text_query(query_rewritten)
            else:  # Elastic search
                results = self._handle_elastic_search(query_rewritten)

            storage_info_output.update({
                'content': results['content'],
                'total_token': storage_info_output['total_token'] + results['total_token'],
                'cost': storage_info_output['cost'] + results['cost'],
                'products': results.get('products', []),
                'message': "Request processed successfully."
            })
            self.USER_HELPER.save_conversation(user_name=user_name, query=input_text, id_request=id_request, response=storage_info_output['content'])

        except Exception as e:
            storage_info_output.update({"status": 500, "message": f"Error processing request: {str(e)}"})

        return storage_info_output

if __name__ == "__main__":
    pass