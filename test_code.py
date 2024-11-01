# from configs.config_system import SYSTEM_CONFIG
# from icecream import ic


######## TEST ELASTICSEARCH ########
# from source.retriever.elastic_search import search_db, classify_intent
# query = "bán cho tôi sản phẩm điều hòa bán chạy nhất bên bạn "
# demands = classify_intent(question=query)
# response = search_db(demands=demands)
# print(response[0])

# from source.retriever.elastic_search.extract_specifications import extract_info
# from source.retriever.elastic_search.query_engine_cp import ElasticQueryEngine

# query = "bán cho tôi điều hòa"
# demands = extract_info(query=query)
# print(demands)
# response = ElasticQueryEngine(member_code="NORMAL").search_db(demands=demands)
# print(response[0])

# from source.retriever.elastic_search.elastic_helper import RetrieveHelper
# es = RetrieveHelper()
# es.check_specific_field("sold_quantity")
####### TEST CHAT SEASION ########
# from source.generate.chat_seasion import chat_interface
# while True:
#     query = input("Nhập câu hỏi: ")
#     if query == "exits":
#         break
#     response = chat_interface(query=query)
#     ic(response)



######### TEST CRAWLER ########
# from utils.crawler.crawler_website import CrawlerWebsites
# crawler = CrawlerWebsite(url="https://www.dienmayxanh.com/may-lanh")
# df = crawler.get_info_product()

######### TEST ROUTER ########
# from source.router.router import decision_search_type
# query = ""
# type = decision_search_type(query=query)
# print("Type: ", type['content'])

# ######### TEST TOOL SEARCH ########
# from source.similar_product.searcher import SimilarProductSearchEngine
# from langchain_core.prompts import PromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from source.prompt.template import PROMPT_SIMILAR_PRODUCT

# engine = SimilarProductSearchEngine()
# similar_product_found = engine.search(product_find=type.split("|")[1].strip())
# product_found_str = "\n".join(similar_product_found)


# prompt = PromptTemplate(
#     input_variables=['question', 
#                      'context'],
#     template=PROMPT_SIMILAR_PRODUCT
# )
# model = SYSTEM_CONFIG.load_rag_model()
# chain = prompt | model | StrOutputParser()
# response = chain.invoke({'question': query, 
#                         'context': product_found_str})
# print(response)



######### TEST CHAT CLS PRODUCT ########
# from source.router.router import classify_product
# query = "điều hòa giá 10 triệu"
# response = classify_product(query=query)
# print(response)

######### TEST CHAT API CALL ########
# from source.generate.chat_seasion import Pipeline 
from api.handle_request import handle_request

response = handle_request(
    timeSeconds=50,
    InputText = "tôi muốn tìm hiểu vài cái wifi",
    UserName="Duc Pham",
    IdRequest="998saasfd",
    PhoneNumber='08354945868',
    Address='Hà Nội',
    MemberCode="NORMAL",
    Voice = None,
    Image=None,
    NameBot=None)
print(response)


# from utils.user_helper import UserHelper
# UserHelper().save_conversation(phone_number="0123456789", id_request="123", query="gmsdgsdm", response="sdmn")
# response = UserHelper().load_conversation(conv_user="0123456789", id_request="123")
# print(response)

######### TEST CHATCHIT  ############
# from langchain_core.prompts import PromptTemplate
# from source.prompt.template import PROMPT_CHATCHIT

# while True:
#     question = input("Nhập câu hỏi của bạn:")
#     if question == "q":
#         break
#     template = PromptTemplate(
#                     input_variables=['question'],
#                     template=PROMPT_CHATCHIT).format(question=question)
#     response = SYSTEM_CONFIG.load_chatchit_model().invoke(template).content
#     print(response)


######### TEST ORDER ############
# from langchain_core.prompts import PromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from source.prompt.template import  PROMPT_ORDER


# query = "đặt hàng điều hòa 2 chiều"
# PROMPT_TEMPLATE = PromptTemplate(
#             input_variables=['question'],
#             template=PROMPT_ORDER
#         )

# chain = PROMPT_TEMPLATE | SYSTEM_CONFIG.load_rag_model() | StrOutputParser()
# response = chain.invoke({"question": query})
# print(response)


######### TEST DATABASE ############
# from utils.postgres_connecter.postgres_logger import PostgresHandle
# postgres_handle = PostgresHandle()
# postgres_handle.create_table()
# postgres_handle.connection.close()

# from source.data_processing.processor import DataProcessingPipeline

# pipeline = DataProcessingPipeline()
# pipeline.processing(member_codes=["G-JLVIYR", "G-XNAWVM", "G-MIMWPJ", "G-QAXOHL", "NORMAL"])

########### TEST MERGE DATA ############
# from source.data_processing.fast_process import fast_merge, indexing_data
# indexing_data()

########### TEST RETRIEVER ############
# from source.retriever.vectorstores.qdrant import QdrantEngine

# engine = QdrantEngine()
# query = "Tôi muốn mua điều hòa giá rẻ"

# # demands = extract_info(query=query)
# engine.testing(query=query)


# from source.retriever.vectorstores.chroma import ChromaQueryEngine

# enegine = ChromaQueryEngine(member_code="NORMAL")
# response = enegine.get_context(query="bán cho tôi điều hòa MDV 9000 BTU")
# print(response)


