import os
import requests
import logging
import pandas as pd
from pathlib import Path
from configs.config_system import LoadConfig
from .indexing_data import DataIndexer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

path_not_merge = LoadConfig.ALL_PRODUCT_FILE_NOT_MERGE_STORAGE
path_merged = LoadConfig.ALL_PRODUCT_FILE_MERGED_STORAGE


def fast_merge() -> pd.DataFrame:
    url: str = "http://10.207.112.54:8808/aio/product/filterProductForAI"
    headers = {
        'x-api-key': 'VCC#SUPERAPP#UIHO',
        'Content-Type': 'application/json'
    }

    for code_member in LoadConfig.MEMBER_CODE:
        data = {
            "dataRequest": {
                "keyWord": None,
                "brand": None,
                "productGroupIds": [],
                "productBrandIds": [],
                "unionGroupCode": code_member
            },
            "pageRequest": {
                "page": 0,
                "size": 300
            }
        }
        
        if code_member == 'NORMAL':
            data['dataRequest'].pop('unionGroupCode')
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            if response.status_code == 200:
                response = response.json()
                product_list = []

                # Trích xuất các trường thông tin cần thiết
                for product in response['data']['content']:
                    product_info = {
                        'productId': product['productId'],
                        'productGroupId': product['productGroupId'],
                        'productName': product['productName'],
                        'shortDescription': product['shortDescription'],
                        'productCode': product['productCode'],
                        'imgList': ", ".join(product['imgList']),  # Nối danh sách ảnh thành chuỗi
                        'productDescription': product['productDescription'],
                        'specifications': product['specifications'],
                        'soldQuantity': product['soldQuantity'],
                        'price': product['productPrice']['price']
                    }
                    product_list.append(product_info)

                # Chuyển dữ liệu sang DataFrame
                new_df = pd.DataFrame(product_list)
        except: 
            new_df = pd.read_excel(path_not_merge.format(member_code=code_member))
        origin_df = pd.read_excel("data/data_private/data_final_superappv10.xlsx")
        origin_df.rename(columns={"specification": "specifications"}, inplace=True)
        # lấy cột giá của df mới thay vào giá của df cũ
        for index1, row1 in origin_df.iterrows():
            for index2, row2 in new_df.iterrows():
                if row1['product_info_id'] == row2['productId']:
                    origin_df.at[index1, 'lifecare_price'] = row2['price']
        origin_df.to_excel(path_merged.format(member_code=code_member), index=False)

def indexing_data():
    indexer = DataIndexer()
    indexer.restart_index_name()
    indexer.embedding_data()
    logger.info(f"Converted and indexed data sucessfully")


if __name__ == "__main__":
    fast_merge()
    indexing_data()