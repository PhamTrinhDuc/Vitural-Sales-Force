# https://qdrant.tech/articles/vector-search-filtering/

import uuid
import os
import json
import logging
import pandas as pd
from dotenv import load_dotenv
from source.model.loader import ModelLoader
from qdrant_client import QdrantClient
from qdrant_client import models
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import Filter
from qdrant_client.models import PointStruct
from configs.config_system import LoadConfig

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QdrantEngine:
    def __init__ (self):
        self.client = QdrantClient(
            url=os.getenv("QDRANT_CLOUD_ID"),
            api_key=os.getenv("QDRANT_API_KEY"),
            timeout=LoadConfig.TIMEOUT
        )
        self.dataframe = pd.read_excel("data/data_private/data_member/data_final_NORMAL_merged.xlsx")

    def delete_colection(self):
        self.client.delete_collection(collection_name=LoadConfig.INDEX_NAME_QDRANT)
    
    def create_collection(self):
        if not self.client.collection_exists(collection_name=LoadConfig.INDEX_NAME_QDRANT):
            self.client.create_collection(
                collection_name=LoadConfig.INDEX_NAME_QDRANT,
                vectors_config=VectorParams(size=LoadConfig.VECTOR_EMBED_OPENAI, distance=Distance.COSINE),
                optimizers_config=models.OptimizersConfigDiff(indexing_threshold=10000),
                hnsw_config=models.HnswConfigDiff(
                    m=32,  # Increase the number of edges per node from the default 16 to 32
                    ef_construct=200,  # Increase the number of neighbours from the default 100 to 200
                ),
                quantization_config=models.ScalarQuantization(
                    scalar=models.ScalarQuantizationConfig(
                        type=models.ScalarType.INT8,
                        quantile=0.99,
                        always_ram=True
                    )
                ),
            )

        logger.info(self.client.get_collection(collection_name=LoadConfig.INDEX_NAME_QDRANT))

    def update_data(self):
        embedder = ModelLoader.load_embed_openai_model()
        
        points = []
        for idx, row in self.dataframe.iterrows():
            embedding = embedder.embed_documents(texts=[row['group_name']])[0]
            metadata = {
                'product_info_id': row['product_info_id'],
                'group_product_name': row['group_product_name'],
                'price': row['lifecare_price'],
                'specifications': row['specifications'],
                'file_path': row['file_path'],
            }
            id = uuid.uuid4().hex
            point = PointStruct(
                vector=embedding,
                payload=metadata,
                id=id
            )
            points.append(point)
        
        logger.info(f"Uploading {len(points)} points to Qdrant")

        self.client.upsert(
            collection_name=LoadConfig.INDEX_NAME_QDRANT,
            wait=True,
            points=points
        )

    def update_payload(self):
        for idx, row in self.dataframe.iterrows():
            metadata = {
                'product_info_id': row['product_info_id'],
                'product_name': row['product_name'],
                'price': row['lifecare_price'],
                'specifications': row['specifications'],
                'file_path': row['file_path'],

            }
            self.client.overwrite_payload(
                collection_name=LoadConfig.INDEX_NAME_QDRANT,
                payload=metadata,
            )
        
        logger.info(f"Overwrite payload to Qdrant sucessfull !!")

    def search(self, 
               query: str, 
               pair_filter: dict[str, any] = None):
        
        query_embed = ModelLoader.load_embed_openai_model().embed_documents(texts=[query])[0]

        search_result = self.client.query_points(
            collection_name="test_collection",
            query=query_embed, 
            query_filter=Filter(
                must=[
                    models.FieldCondition(
                        key="group_product_name", 
                        match=models.MatchValue(value="đèn năng lượng mặt trời")),

                    models.FieldCondition(
                        key="price",
                        range=models.Range(
                            gte=0,
                            lte=5000000
                        )
                    )
                ],
            ),
            score_threshold=None,
            with_payload=True,
            with_vectors=False,
            limit=3,
        ).points
        return search_result

    def format_output(self, output_qdrant: list):
        outtext = ""
        for index, point in enumerate(output_qdrant):
            point = json.loads(json.dumps(point.dict(), indent=4))
            payload = point['payload']
            outtext +=  f"""
                {index+1}. "id": {payload['product_info_id']},
                "product_name": {payload['group_product_name']},
                "price": {payload['price']} \n"""
        return outtext

    def testing(self, query: str):
        results = self.search(query)
        print(self.format_output(results))

if __name__ == "__main__":
    query = "bán cho tôi Bộ Lưu Trữ Năng Lượng Mặt Trời SUNTEK" 
    engine = QdrantEngine()
    engine.testing(query=query)