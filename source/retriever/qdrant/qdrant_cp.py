# https://qdrant.tech/articles/vector-search-filtering/

import uuid
import os
import json
import logging
import pandas as pd
from datasets import Dataset
from tqdm import tqdm
from dotenv import load_dotenv
from fastembed import SparseTextEmbedding, TextEmbedding
from fastembed.late_interaction import LateInteractionTextEmbedding
from qdrant_client import QdrantClient
from qdrant_client import models
from qdrant_client.models import Filter
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
        self.index_name = LoadConfig.INDEX_NAME_QDRANT
        self.jina_model = TextEmbedding(model_name="jinaai/jina-embeddings-v2-base-en")
        self.bm42_model = SparseTextEmbedding(model_name="Qdrant/bm42-all-minilm-l6-v2-attentions")
        self.late_model = LateInteractionTextEmbedding(model_name="colbert-ir/colbertv2.0")
        self.dataframe = pd.read_excel("data/data_private/data_member/data_final_NORMAL_merged.xlsx")

    def _count_data(self):
        return self.client.count(collection_name=self.index_name)
    
    def _delete_colection(self):
        self.client.delete_collection(collection_name=self.index_name)
    
    def create_collection(self):
        self.client.recreate_collection(
            collection_name=self.index_name,
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
            vectors_config={
                "jina-embeddings-v2": models.VectorParams(
                    size=768,
                    distance=models.Distance.COSINE,
                ),
                "colbertv2.0": models.VectorParams(
                    size=128,
                    distance=models.Distance.COSINE,
                    multivector_config=models.MultiVectorConfig(
                        comparator=models.MultiVectorComparator.MAX_SIM,
                    )
                ),
            },
            sparse_vectors_config={
                "bm42": models.SparseVectorParams(
                    modifier=models.Modifier.IDF,
                )
            }
        )

        logger.info(self.client.get_collection(collection_name=self.index_name))

    def update_data(self):

        batch_size = 4
        dataset = Dataset.from_pandas(self.dataframe, preserve_index=False)
        for batch in tqdm(dataset.iter(batch_size=batch_size), total=len(dataset) // batch_size):

            dense_embedding = list(self.jina_model.embed(documents=batch['group_name']))
            bm42_embedding = list(self.bm42_model.embed(documents=batch['group_name']))
            late_embedding = list(self.late_model.embed(documents=batch['group_name']))

            self.client.upload_points(
                collection_name=self.index_name,
                points= [
                    models.PointStruct(
                        id=uuid.uuid4().hex,
                        
                        payload={
                            'product_info_id': batch['product_info_id'][i],
                            'group_product_name': batch['group_product_name'][i],
                            'product_name': batch['product_name'][i],
                            'price': batch['lifecare_price'][i],
                            'short_description': batch['short_description'][i],
                            'specifications': batch['specifications'][i],
                            'file_path': batch['file_path'][i],
                            'power': batch['power'][i],
                            'weight': batch['weight'][i],
                            'volume': batch['volume'][i]
                        },
                        vector={
                            "jina-embeddings-v2": dense_embedding[i].tolist(),
                            "bm42": bm42_embedding[i].as_object(),
                            "colbertv2.0": late_embedding[i].tolist()
                        },
                    ) for i, _ in enumerate(batch["group_name"])
                ],
                batch_size=batch_size
            )

        logger.info(f"Uploading data to Qdrant successful !!")

    def update_payload(self):
        for idx, row in self.dataframe.iterrows():
            metadata = {
                'product_info_id': row['product_info_id'],
                "group_product_name": row['group_product_name'],
                'product_name': row['product_name'],
                'price': row['lifecare_price'],
                'short_description': row['short_description'],
                'specifications': row['specifications'],
                'file_path': row['file_path'],
                'power': row['power'],
                'weight': row['weight'],
                'volume': row['volume']

            }
            self.client.overwrite_payload(
                collection_name=self.index_name,
                payload=metadata,
            )
        
        logger.info(f"Overwrite payload to Qdrant sucessfull !!")

    def search(self, 
               query: str, 
               pair_filter: dict[str, any] = None):
        
        sparse_embedding = list(self.bm42_model.embed(documents=query))[0]
        dense_embedding = list(self.jina_model.embed(documents=query))[0]
        late_embedding = list(self.late_model.embed(documents=query))[0]

        search_result = self.client.query_points(
            collection_name=self.index_name,
            prefetch=[
                models.Prefetch(query=sparse_embedding.as_object(), using="bm42", limit=3),
                models.Prefetch(query=dense_embedding.tolist(), using="jina-embeddings-v2", limit=3),
                models.Prefetch(query=late_embedding.tolist(), using="colbertv2.0", limit=3),
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF), # <--- Combine the scores of the two embeddings
            query_filter=Filter(
                must=[
                    models.FieldCondition(
                        key="group_product_name", 
                        match=models.MatchValue(value="đèn năng lượng mặt trời")),

                    # models.FieldCondition(
                    #     key="price",
                    #     range=models.Range(
                    #         gte=0,
                    #         lte=5000000
                    #     )
                    # )
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
                "product_name": {payload['product_name']},
                "price": {payload['price']} \n"""
        return outtext

    def testing(self, query: str):
        self.create_collection()
        # self.update_data()

        results = self.search(query)
        print(self.format_output(results))

        # embedding = list(self.jina_model.embed(documents="HELLO"))
        # print(embedding)

        # dataset = Dataset.from_pandas(self.dataframe, preserve_index=False)
        # batch_size = 4
        # for batch in tqdm(dataset.iter(batch_size=batch_size), total=len(dataset) // batch_size):
        #     print(batch['group_name'])


if __name__ == "__main__":
    query = "bán cho tôi Bộ Lưu Trữ Năng Lượng Mặt Trời SUNTEK 12V/25Ah PLUS" 
    engine = QdrantEngine()
    engine.testing(query=query)