# from configs.config_system import SYSTEM_CONFIG
# from icecream import ic


######## TEST ELASTICSEARCH ########
# from source.retriever.elastic_search import search_db, classify_intent
# query = "điều hòa giá đắt nhất"
# demands = classify_intent(question=query)
# print(demands)
# response = search_db(demands=demands)
# print(response[0])

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
# query = "tôi muốn tìm sản phẩm điều hòa MDV - inverter 9000 btu có giá 20 triệu"
# type = decision_search_type(query=query)
# print("Type:\n", type)

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
# from source.generate.chat import classify_product
# query = "điều hòa giá 10 triệu"
# response = classify_product(query=query)
# print(response)

######### TEST CHAT API CALL ########
# from source.generate.chat_seasion import Pipeline 
# from api.handle_request import handle_request

# response = handle_request(
#     InputText="giảm giá cho tôi còn 10 triệu thôi nhé", 
#     UserName="Văn Thiện",
#     IdRequest="123",
#     PhoneNumber='030983479',
#     Address='Hà Nội',
#     NameBot=None,
#     Image=None,
#     Voice=None)
# print(response['content'])

# from utils.user_helper import UserHelper
# UserHelper().save_conversation(phone_number="0123456789", id_request="123", query="gmsdgsdm,m,g", response="sdmn")
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

# import time
# st = time.time()
# from langchain_openai import ChatOpenAI
# from langchain_community.callbacks import get_openai_callback

# model = ChatOpenAI(api_key="sk-dTKKIChoB9Odh6JlFCbuaKpJVeojvF-FvhwP9x3aWCT3BlbkFJaeYHlewA30a4pENbXXSCl8qKU1KVuogMStcdmka00A")

# with get_openai_callback() as cb:
#     response = model.invoke("Hello").content
# print(response)
# print(type(cb.total_tokens))
# print(type(cb.total_cost))

# print(time.time() - st)


############# TEST REWRITE ###############
# from utils.schemas import GradeReWrite
# from configs.config_system import SYSTEM_CONFIG
# from source.prompt.template import PROMPT_HISTORY
# from source.model.loader import ModelLoader


# llm = ModelLoader().load_rag_model().with_structured_output(GradeReWrite)
# response = llm.invoke(PROMPT_HISTORY.format(question = "chốt cho anh 3 cái",
#                                             chat_history = "Em xin giới thiệu cho anh chị mẫu điều hòa MDV 900BTU có giá 10 triệu")).base
# print(response)


# import os
# import dotenv
# from langchain_openai import ChatOpenAI
# dotenv.load_dotenv()
# os.environ['LANGCHAIN_TRACING_V2'] = 'true'
# os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
# os.environ['LANGCHAIN_API_KEY'] = os.getenv("LANGCHAIN_API_KEY")
# os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


# response = ChatOpenAI(model='gpt-4o-mini').invoke(input="Hello").content
# print(response)
