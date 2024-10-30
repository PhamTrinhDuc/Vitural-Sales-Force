# from elasticsearch import Elasticsearch
# import json
# import os
# import dotenv

# dotenv.load_dotenv()
# # Kết nối đến Elasticsearch
# es = Elasticsearch(
#             cloud_id=os.getenv("ELASTIC_CLOUD_ID"),
#             api_key=os.getenv("ELASTIC_API_KEY"),
#         )

# def create_index(index_name):
#     """Tạo một index mới với cấu hình tiếng Việt"""
#     settings = {
#         "settings": {
#             "analysis": {
#                 "analyzer": {
#                     "vietnamese_analyzer": {
#                         "type": "standard",  # Có thể thay bằng analyzer tiếng Việt chuyên dụng
#                         "tokenizer": "standard",
#                         "filter": ["lowercase"]
#                     }
#                 }
#             }
#         },
#         "mappings": {
#             "properties": {
#                 "title": {
#                     "type": "text",
#                     "analyzer": "vietnamese_analyzer"
#                 },
#                 "content": {
#                     "type": "text",
#                     "analyzer": "vietnamese_analyzer"
#                 }
#             }
#         }
#     }
    
#     es.indices.create(index=index_name, body=settings)

# def add_document(index_name, document):
#     """Thêm một document vào index"""
#     es.index(index=index_name, body=document)

# def search_documents(index_name, query_text):
#     """Tìm kiếm document theo text"""
#     query = {
#         "query": {
#             "multi_match": {
#                 "query": query_text,
#                 "fields": ["title", "content"],
#                 "fuzziness": "AUTO"  # Cho phép tìm kiếm gần đúng
#             }
#         }
#     }
    
#     result = es.search(index=index_name, body=query)
#     return result

# # Ví dụ sử dụng
# def main():
#     index_name = "blog_posts"
    
#     # Tạo index mới
#     if not es.indices.exists(index=index_name):
#         create_index(index_name)
    
#     # Thêm một số documents mẫu
#     documents = [
#         {
#             "title": "Công nghệ thông tin tại Việt Nam",
#             "content": "Ngành công nghệ thông tin đang phát triển nhanh chóng tại Việt Nam"
#         },
#         {
#             "title": "Học lập trình Python",
#             "content": "Python là ngôn ngữ lập trình dễ học và được sử dụng rộng rãi"
#         },
#         {
#             "title": "Trí tuệ nhân tạo AI",
#             "content": "AI đang thay đổi cách chúng ta làm việc và sinh sống"
#         },
#         {
#             "title": "computer vision",
#             "content": "1 nhánh của trí tuệ nhân tạo là computer vision"
#         }
#     ]
    
#     # Thêm documents vào index
#     for doc in documents:
#         add_document(index_name, doc)
        
#     # Đợi 1 giây để Elasticsearch index documents
#     import time
#     time.sleep(1)
    
#     # Thực hiện tìm kiếm
#     results = search_documents(index_name, "trí tuệ nhân tạo")
    
#     print(results["hits"]['hits'])
#     # In kết quả
#     # for hit in results['hits']['hits']:
#     #     print(f"\nScore: {hit['_score']}")
#     #     print(f"Title: {hit['_source']['title']}")
#     #     print(f"Content: {hit['_source']['content']}")

# if __name__ == "__main__":
#     main()



from qdrant_client import QdrantClient
import json

from qdrant_client import models
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import Filter, FieldCondition, MatchValue
from qdrant_client.models import PointStruct


client = QdrantClient(
    url="https://d0e469f1-1893-4323-8fc4-b97ec513b82b.us-east4-0.gcp.cloud.qdrant.io:6333", 
    api_key="PlpYK0AAzzFzmHOA8WXZfVeZkIFYWZHJrrk2K1LjKiOqMjHC151mDA",
)

if not client.collection_exists(collection_name="test_collection"):
    client.create_collection(
        collection_name="test_collection",
        vectors_config=VectorParams(size=4, distance=Distance.DOT),
        optimizers_config=models.OptimizersConfigDiff(indexing_threshold=10000)
    )
# client.delete_points(collection_name="test_collection")

# print(client.get_collection(collection_name="test_collection"))


operation_info = client.upsert(
    collection_name="test_collection",
    wait=True,
    points=[
        PointStruct(id=1, vector=[0.05, 0.61, 0.76, 0.74], payload={"city": "Berlin", 
                                                                    "address": "lj Main Street"}),
        PointStruct(id=2, vector=[0.19, 0.81, 0.75, 0.11], payload={"city": "London", 
                                                                    "address": "sdf Main Street"}),
        PointStruct(id=3, vector=[0.36, 0.55, 0.47, 0.94], payload={"city": "Moscow",
                                                                    "address": "fsdf Main Street"}),
        PointStruct(id=4, vector=[0.18, 0.01, 0.85, 0.80], payload={"city": "New York", 
                                                                    "address": "fsdg Main Street"}),
        PointStruct(id=5, vector=[0.24, 0.18, 0.22, 0.44], payload={"city": "Beijing", 
                                                                    "address": "123 Main Street"}),
        PointStruct(id=6, vector=[0.35, 0.08, 0.11, 0.44], payload={"city": "London", 
                                                                    "address": "1274 Main Street"}),
    ],
)

search_result = client.query_points(
    collection_name="test_collection",
    query=[0.2, 0.1, 0.9, 0.7],
    query_filter=Filter(
        must=[FieldCondition(key="city", match=MatchValue(value="London"))],
        # should=[FieldCondition(key="city", match=MatchValue(value="Berlin"))],
    ),
    # using="text",
    with_payload=True,
    with_vectors=False,
    limit=3,
).points


for point in search_result:
    print(json.dumps(point.dict(), indent=4))

search_result = client.scroll(
    collection_name="test_collection",
    scroll_filter=models.Filter(
        must=[
            models.FieldCondition(key="city", match=models.MatchValue(value="London")),
        ]
    ),
    limit=1,
    with_payload=True,
    with_vectors=False,
    order_by="city",
)
print(search_result)


search_result = client.facet(
    collection_name="test_collection",
    key="city",
    facet_filter=models.Filter(must=[models.Match("address", "123 Main Street")]),
)
print(search_result)