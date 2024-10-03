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
# from source.generate.chat import chat_with_history_copy
# query = "chốt đơn cho tôi điều hòa 10 triệu nhé"
# response = chat_with_history_copy(query=query)
# ic(response)


######### TEST CRAWLER ########
# from utils.crawler.crawler_website import CrawlerWebsites
# crawler = CrawlerWebsite(url="https://www.dienmayxanh.com/may-lanh")
# df = crawler.get_info_product()

######### TEST ROUTER ########
# from source.router.router import decision_search_type
# query = "tôi muốn tìm sản phẩm tương tự điều hòa MDV - inverter 9000 btu"
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
# response = retriever.get_context(query="KPI xử lý bảo hành điều hòa", 
#                                  product_name="dieu_hoa")
# print(response)

######### TEST FUNCTION CALLING ########
######### TEST INGEST DATA ########
# from source.ingest_data.ingestion import IngestBuilder
# data = IngestBuilder.load_document_chunked()


######### TEST CHAT CLS PRODUCT ########
# from source.generate.chat import classify_product
# query = "điều hòa giá 10 triệu"
# response = classify_product(query=query)
# print(response)

######### TEST CHAT API CALL ########
# from source.generate.chat_seasion import QuestionHandler

# handler = QuestionHandler()
# response = handler.chat_session(
#     input_text="đèn nặng lượng mặt trời", 
#     user_name="ducpham",
#     id_request="123")
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
# print(cb.total_tokens)
# print(cb.total_cost)

# print(time.time() - st)