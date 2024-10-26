import requests
import pandas as pd
import os
import json
import logging
from typing import List, Literal

def download_superapp_data(code_member: str =  Literal['G-JLVIYR', 'G-XNAWVM', 'G-MIMWPJ', 'G-QAXOHL', "NORMAL"]) -> pd.DataFrame:
    
    url: str = "http://10.207.112.54:8808/aio/product/filterProductForAI"

    headers = {
        'x-api-key': 'VCC#SUPERAPP#UIHO',
        'Content-Type': 'application/json'
    }
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
            # Danh sách lưu thông tin sản phẩm
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
            df = pd.DataFrame(product_list)
            return df 
        else:
            logging.error(f"Error when get data from superapp: {response.status_code}")
            return None  # Thêm return None khi có lỗi
    except Exception as e:
        logging.info(f"Error when get data from superapp: {e}")
    return None
