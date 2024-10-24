# from configs.config_system import SYSTEM_CONFIG
# from icecream import ic


######## TEST ELASTICSEARCH ########
# from source.retriever.elastic_search import search_db, classify_intent
# query = "bán cho tôi sản phẩm điều hòa bán chạy nhất bên bạn "
# demands = classify_intent(question=query)
# response = search_db(demands=demands)
# print(response[0])

# from source.retriever.elastic_search.extract_specifications import extract_info
# from source.retriever.elastic_search.query_engine_cp import search_db

# query = "Điều hòa MDV 1 chiều 12000 BTU - Model 2023 bên bạn có không ?"
# demands = extract_info(query=query)
# response = search_db(demands=demands)
# print(response[0])

# from source.retriever.elastic_search.elastic_helper import ElasticHelper
# es = ElasticHelper()
# es.check_specific_field("sold_quantity")
####### TEST CHAT SEASION ########
# from source.generate.chat_seasion import chat_interface
# while True:
#     query = input("Nhập câu hỏi: ")
#     if query == "exits":
#         break
#     response = chat_interface(query=query)
#     ic(response)

######### TEST CHAT GRADIO ########
# from source.generate.gradio_chat import chat_with_history_copy
# query = "top 10 sản phẩm điều hòa bán chạy 2023"
# response = chat_with_history_copy(query=query)
# print(response)


######### TEST CRAWLER ########
# from utils.crawler.crawler_website import CrawlerWebsites
# crawler = CrawlerWebsite(url="https://www.dienmayxanh.com/may-lanh")
# df = crawler.get_info_product()

######### TEST ROUTER ########
# from source.router.router import decision_search_type
# query = "bán tôi xem sản phẩm điều hòa MDV 2023 đang bán chạy"
# type = decision_search_type(query=query)
# print("Type:\n", type['content'])

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


######### TEST FQA ########
# import pandas as pd
# data  = pd.read_excel("/home/ducpham/Documents/FAQ/Dieu_Hoa/Kịch Bản ChatBot.xlsx")

# data.columns = data.loc[1].values.tolist()
# data = data.loc[2:].reset_index(drop=True)
# data = data.drop(columns=['Title', 'Desire', 'Evaluate'])
# data.head()


######### TEST RETRIEVER ########
# from source.retriever.chroma.retriever import Retriever
# retriever = Retriever()
# # response = retriever.get_context(query="KPI xử lý bảo hành điều hòa", 
# #                                  product_name="dieu_hoa")
# response = retriever.get_info_product(
#     id_product="M&EGD000254",
#     data_path='data/data_private/data_csv/cong_tac.csv')

######### TEST INGEST DATA ########
# from source.ingest_data.ingestion import IngestBuilder
# data = IngestBuilder.load_document_chunked()


######### TEST CHAT CLS PRODUCT ########
# from source.router.router import classify_product
# query = "điều hòa giá 10 triệu"
# response = classify_product(query=query)
# print(response)

######### TEST CHAT API CALL ########
# from source.generate.chat_seasion import Pipeline 
# from api.handle_request import handle_request

# response = handle_request(
#     InputText = "bán cho tôi điều hòa bên bạn",
#     UserName="Hiệp",
#     IdRequest="9989",
#     PhoneNumber='0886945868',
#     Address='Hà Nội',
#     Voice = None,
#     Image=None,
#     NameBot=None)
# print(response)

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

# from source.data_processor.run import process_data_and_save
# from source.data_processor.clone_data import download_superapp_data

# df = download_superapp_data(code_member="G-JLVIYR")
# print(df.head())    
# # process_data_and_save()

from source.data_processor.run import DataProcessingPipeline

pipeline = DataProcessingPipeline()
pipeline.processing()