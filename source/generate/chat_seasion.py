import time
from typing import Dict, Optional, Any
from langchain_core.prompts import PromptTemplate
from source.retriever.chroma.retriever import Retriever
from source.router.router import decision_search_type, classify_product
from source.retriever.elastic_search import search_db, classify_intent
from source.similar_product.searcher import SimilarProductSearchEngine
from source.model.loader import ModelLoader
from source.prompt.template import PROMPT_HISTORY, PROMPT_HEADER, PROMPT_CHATCHIT, PROMPT_ORDER
from utils import GradeReWrite, UserHelper, timing_decorator
from utils.postgres_connecter.postgres_logger import PostgresHandler
from configs.config_system import SYSTEM_CONFIG

# Helper functions

class QuestionHandler:
    def __init__(self):
        self.DB_LOGGER = PostgresHandler()
        self.LLM_RAG = ModelLoader().load_rag_model()
        self.LLM_CHAT_CHIT = ModelLoader().load_chatchit_model()
        self.USER_HELPER = UserHelper()

    def _rewrite_query(self, query: str, history: str) -> str:
        """
        Rewrite the user query based on chat history.

        Args:
            query (str): The original user query.
            history (str): The chat history.

        Returns:
            str: The rewritten query.
        """
        try:
            llm_with_output = self.LLM_RAG.with_structured_output(GradeReWrite)
            query_rewrite = llm_with_output.invoke(PROMPT_HISTORY.format(question=query, chat_history=history)).rewrite
            return query_rewrite
        except Exception:
            return query

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
        response = engine.invoke(query=query, product_name=product_name)
        return {
            "content": response.content,
            "total_token": response.response_metadata['token_usage']['total_token']
        }

    def _handle_order_query(self, query: str) -> Dict[str, Any]:
        """
        Handle order-related queries.

        Args:
            query (str): The user's query.

        Returns:
            str: The response to the order query and token usage.
        """
        prompt_template = PromptTemplate(input_variables=['question'], template=PROMPT_ORDER)
        response =  self.LLM_RAG.invoke(prompt_template.format(question=query))
        return {
            "content": response.content,
            "total_token": response.response_metadata['token_usage']['total_token']
        }

    def _handle_text_query(self, query: str) -> Dict[str, Any]:
        """
        Handle text-based queries.

        Args:
            query (str): The user's query.
            rag_chain: The RAG chain for processing.

        Returns:
            Dict[str, Any]: The response and token usage.
        """
        product_id = classify_product(query=query)
        if product_id == -1:
            template = PromptTemplate(input_variables=['question'], template=PROMPT_CHATCHIT)
            response = self.LLM_CHAT_CHIT.invoke(template.format(question=query))
        else:
            db_name = SYSTEM_CONFIG.ID_2_NAME_PRODUCT[product_id]
            context = Retriever().get_context(query=query, product_name=db_name)
            prompt = PromptTemplate(input_variables=['context', 'question'], template=PROMPT_HEADER)
            response = self.LLM_RAG.invoke(prompt.format(context=context, question=query))
        return {
            "content": response.content,
            "total_token": response.response_metadata['token_usage']['total_token']
        }


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
        response = self.LLM_RAG.invoke(prompt.format(context=response_elastic, question=query))
        return {
            "content": response.content,
            "products": products_info,
            "total_token": response.response_metadata['token_usage']['total_token']
        }

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
            "products": [], "terms": [], "content": "", "total_token": 0,
            "status": 200, "message": "",
        }

        if not input_text:
            storage_info_output.update({"message": "No input text provided.", "status": 400})
            return storage_info_output

        try:
            history_conversation = self.USER_HELPER.load_conversation(user_name=user_name, id_request=id_request)
            query_rewritten = self.rewrite_query(query=input_text, history=history_conversation)

            search_type = decision_search_type(query_rewritten)

            if search_type.startswith("SIMILARITY"):
                product_name = search_type.split("|")[1].strip()
                results = self._handle_similarity_search(query_rewritten, product_name)
                storage_info_output['content'] = results["content"]
                storage_info_output['total_token'] += results["total_token"]

            elif search_type == "ORDER":
                results = self._handle_order_query(query_rewritten)['content']
                storage_info_output['content'] = results['content']
                storage_info_output['total_token'] += results['total_token']

            elif search_type == "TEXT":
                results = self._handle_text_query(query_rewritten)
                storage_info_output['content'] = results["content"]
                storage_info_output['total_token'] += results["total_token"]

            else:  # Elastic search
                results = self._handle_elastic_search(query_rewritten)
                storage_info_output['content'] = results["content"]
                storage_info_output['products'] = results["products"]
                storage_info_output['total_token'] += results["total_token"]

            storage_info_output['message'] = "Request processed successfully."
            self.USER_HELPER.save_conversation(user_name=user_name, query=input_text, id_request=id_request, response=storage_info_output['content'])

        except Exception as e:
            results.update({"status": 500, "message": f"Error processing request: {str(e)}"})


        self.DB_LOGGER.insert_data(
            user_name=user_name, 
            seasion_id=id_request, 
            total_token=storage_info_output['total_token'],
            status=storage_info_output['status'], 
            error_message=storage_info_output['message'],
            human_chat=input_text, 
            bot_chat=storage_info_output['content']
        )

        return storage_info_output

if __name__ == "__main__":
    pass