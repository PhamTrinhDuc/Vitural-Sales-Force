import re
import ast
import os
import dotenv
import pandas as pd
import logging
from fuzzywuzzy import fuzz, process
from elasticsearch import Elasticsearch
from typing import Tuple, List
from configs.config_system import LoadConfig

dotenv.load_dotenv()

class ElasticHelper:
    def __init__(self):
        pass

    @staticmethod
    def init_elastic(df: pd.DataFrame, index_name: str = LoadConfig.INDEX_NAME) -> Elasticsearch:
        # Create the client instance
        # client = Elasticsearch(
        # # For local development
        #     hosts=['http://10.248.243.105:9200']
        # )
        client = Elasticsearch(
            cloud_id=os.getenv("ELASTIC_CLOUD_ID"),
            api_key=os.getenv("ELASTIC_API_KEY"),
            timeout=LoadConfig.TIMEOUT
        )
        # Define the mappings
        mappings = {
            "properties": {
                "product_info_id": {"type": "integer"},
                "product_code": { "type":"text"},
                "group_product_name":{"type": "keyword"},
                "product_name": {"type": "text"},
                "short_description": {"type": "text"},
                "file_path": {"type" : "text"},
                "product_info": {"type": "text"},
                "specifications": {"type": "text"},
                "sold_quantity": {"type": "integer"},
                "lifecare_price": {"type": "float"},
                "power": {"type": "float"},
                "weight": {"type": "float"},
                "volume": {"type": "float"},
                "group_name": {"type": "text"},
            }
        }
        # Create the index with mappings
        try:
            if not client.indices.exists(index=index_name):
                client.indices.create(index=index_name, body={"mappings": mappings})
                # Index documents
                for i, row in df.iterrows():
                    doc = {
                        "product_info_id": row["product_info_id"],
                        "product_code": row["product_code"],
                        "group_product_name": row["group_product_name"],
                        "product_name": row["product_name"],
                        "short_description": row["short_description"],
                        "file_path": row["file_path"],
                        "product_info": row["product_info"],
                        "specifications": row["specifications"],
                        "sold_quantity": row["sold_quantity"],
                        "lifecare_price": row["lifecare_price"],
                        "power": row["power"],
                        "weight": row["weight"],
                        "volume": row["volume"],
                        "group_name": row["group_name"],
                    }
                    client.index(index=index_name, id=i, document=doc)

                client.indices.refresh(index=index_name)
                print(f"------Index {index_name} created.-------")
            else:
                # client.indices.delete(index=index_name)
                print(f"-----Index {index_name} already exists.------")
            return client
        except Exception as e:
            logging.error(f"An error occurred while connecting to Elastic Search: {str(e)}")
    
    @staticmethod
    def check_specific_field(field_name: str):

        client = Elasticsearch(
            cloud_id=os.getenv("ELASTIC_CLOUD_ID"),
            api_key=os.getenv("ELASTIC_API_KEY"),
        )
        query = {
            "query": {
                "exists": {
                    "field": field_name
                }
            }
        }
        result = client.search(index=LoadConfig.INDEX_NAME, body=query, size=10)
        if result:
            print(result)
            print(f"\nCác document có trường '{field_name}':")
        else:
            print(f"\nKhông có document nào có trường '{field_name}'")

        count = client.count(index=LoadConfig.INDEX_NAME)['count']
        print(f"\nSố lượng document trong index {LoadConfig.INDEX_NAME}: {count}")
    
    @staticmethod
    def parse_string_to_dict(input_string: str) -> dict:
        """
            Nhận string từ function calling trả về, xử lí string và đưa về dạng dictionary chứa thông tin của các thông số kĩ thuật.
            Dictionary này sẽ là đầu vào cho hàm search_db trong module_elastic/query_engine.py
            Args:
                - input_string: string trả về từ function calling
            Return:
                
        """
        try:
            # Thay thế các giá trị rỗng bằng None để ast có thể xử lý
            input_string = input_string.replace('""', 'None')
            data_dict = ast.literal_eval(input_string)
            
            # Chuyển lại None thành chuỗi rỗng nếu cần
            for key, value in data_dict.items():
                if value is None:
                    data_dict[key] = ""
            
            return data_dict
        except (SyntaxError, ValueError) as e:
            return f"Error: Invalid input string - {str(e)}"
        

    @staticmethod
    def parse_specification_range(specification: str) -> Tuple[float, float]:
        """
        Nếu thông số là giá thì xử lí và trả về khảng giá, nếu không thì trả về giá trị mặc định.
        Args:
            - specification: thông số kĩ thuật cần xử lí
        Returns:
            - trả về min_value, max_value; khoảng cần tìm kiếm của thông số kĩ thuật
        """
        pattern = r"(?P<prefix>\b(dưới|trên|từ|đến|khoảng)\s*)?(?P<number>\d+(?:,\d+)*)\s*(?P<unit>triệu|nghìn|tr|k|kg|l|lít|kw|w|t|btu)?\b"
        min_value = 0
        max_value = 100000000
        for match in re.finditer(pattern, specification, re.IGNORECASE):
            prefix = match.group('prefix') or ''
            number = float(match.group('number').replace(',', ''))
            unit = match.group('unit') or ''
            if unit.lower() == '':
                return min_value, max_value # nếu không phải giá thì trả về giá trị mặc định

            if unit.lower() in ['triệu','tr','t']:
                number *= 1000000
            elif unit.lower() in ['nghìn','k']:
                number *= 1000
            elif unit.lower() in ['kw']:
                number *= 1000

            if prefix.lower().strip() == 'dưới':
                max_value = min(max_value, number)
            elif prefix.lower().strip() == 'trên':
                min_value = min(max_value, number)
            elif prefix.lower().strip() == 'từ':
                min_value = min(max_value, number)
            elif prefix.lower().strip() == 'đến':
                max_value = max(min_value, number)
            else:  # Trường hợp không có từ khóa
                min_value = number * 0.8
                max_value = number * 1.2

        if min_value == float('inf'):
            min_value = 0
        print('min_value, max_value:',min_value, max_value)
        return min_value, max_value
    
    @staticmethod
    def get_keywords(specification: str)-> Tuple[str, str, str]:
        """
        Từ các thông số kĩ thuật do function calling extract ra, nếu có các cụm như: giá đắt nhất, công suất rẻ nhất...).
        Extract ra phần order, word, specification để đưa vào câu query của elastic search.
        
        Args:
            specifications: str: phần fewshot từ câu hỏi của elastic search
        Returns:
            order: str: thứ tự sắp xếp của giá (tăng dần hoặc giảm dần) -> keyword để elastic search giảm hoặc tăng dấn của sản phẩm đó.
            word: str: từ khóa giá, công suất, khối lượng, dung tích
            specifications: str = "": thông số kĩ thuật
        """

        order, word = "asc", ""  # Default order
        cheap_keywords = LoadConfig.CHEAP_KEYWORDS
        expensive_keywords = LoadConfig.EXPENSIVE_KEYWORDS

        for keyword in cheap_keywords:
            if keyword in specification.lower():
                order = "asc"
                word = keyword
                specification = ""
        for keyword in expensive_keywords:
            if keyword in specification.lower():
                order = "desc"
                word = keyword
                specification = ""
        return order, word, specification

    @staticmethod
    def find_closest_match(query_product: str, list_product: List[str]) -> List:
        """

        Hàm này dùng để tìm sản phẩm gần giống nhất với câu query của người dùng trong list_product.
        Args:
            - query: câu query của người dùng
            - list_product: list chứa tên các sản phẩm
        Returns:
            - trả về tên sản phẩm gần giống nhất và độ match

        """
        match = process.extractOne(query_product, list_product, scorer=fuzz.partial_ratio)
        print(f"Có phải bạn tìm kiếm sản phẩm {match[0]}")
        print("Độ match:", match[1])
        # if match[1] >= 60:
        #     return match[0]
        # else:
        #     return 0
        return match