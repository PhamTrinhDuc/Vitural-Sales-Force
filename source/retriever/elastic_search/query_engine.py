import ast
import pandas as pd
# from icecream import ic
from typing import Dict, List, Tuple, Optional
from elasticsearch import Elasticsearch
from utils import timing_decorator
from .elastic_helper import ElasticHelper
from configs import SYSTEM_CONFIG

class ElasticQueryEngine:
    NUMBER_SIZE_ELAS = SYSTEM_CONFIG.NUM_SIZE_ELAS
    MATCH_THRESHOLD = 60

    def __init__(self, member_code: str):
        self.index_name = member_code.replace("-", "").lower()
        self.elastic_helper = ElasticHelper()
        self.dataframe = pd.read_excel(SYSTEM_CONFIG.ALL_PRODUCT_FILE_MERGED_STORAGE.format(member_code=member_code))

    def create_filter_range(self, field: str, value: str) -> Dict:
        """
        Hàm này tạo ra filter range cho câu query.

        Args:
            - field: tên field cần filter
            - value: giá trị cần filter
        Return:
            - trả về dictionary chứa thông tin filter range
        """
        min_value, max_value = self.elastic_helper.parse_specification_range(value)
        range_filter = {
            "range": {
                field: {
                    "gte": min_value,
                    "lte": max_value
                }
            }
        }
        return range_filter

    def create_elasticsearch_query(
            self,
            product: str, product_name: str, 
            specifications: Optional[str] = None,
            price: Optional[str] = None,
            power: Optional[str] = None,
            weight: Optional[str] = None,
            volume: Optional[str] = None,) -> Dict:
        """
        Tạo một truy vấn Elasticsearch dựa trên các tham số đầu vào.

        Hàm này tạo ra một truy vấn Elasticsearch phức tạp, bao gồm các điều kiện tìm kiếm
        và sắp xếp dựa trên các tham số được cung cấp.

        Args:
            product (str): Tên nhóm sản phẩm chính.
            product_name (str): Tên cụ thể của sản phẩm.
            specifications (Optional[str]): Thông số kỹ thuật của sản phẩm (không được sử dụng trong hàm hiện tại).
            price (Optional[str]): Giá sản phẩm, có thể bao gồm từ khóa sắp xếp.
            power (Optional[str]): Công suất sản phẩm, có thể bao gồm từ khóa sắp xếp.
            weight (Optional[str]): Trọng lượng sản phẩm, có thể bao gồm từ khóa sắp xếp.
            volume (Optional[str]): Thể tích sản phẩm, có thể bao gồm từ khóa sắp xếp.

        Returns:
            Dict: Một từ điển đại diện cho truy vấn Elasticsearch.

        Note:
            - Hàm này sử dụng hằng số NUMBER_SIZE_ELAS để giới hạn kích thước kết quả trả về.
            - Các tham số tùy chọn (price, power, weight, volume) có thể chứa các từ khóa
            để chỉ định thứ tự sắp xếp (ví dụ: "lớn nhất", "nhỏ nhất").
            - Hàm get_keywords() được sử dụng để phân tích các từ khóa sắp xếp.
            - Hàm create_filter_range() được sử dụng để tạo bộ lọc phạm vi cho các trường số.
        """
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"group_product_name": product}},
                        {"match": {"group_name": product_name}}
                    ]
                }
            },
            "size": ElasticQueryEngine.NUMBER_SIZE_ELAS
        }

        for field, value in [('lifecare_price', price), ('power', power), ('weight', weight), ('volume', volume)]:
            if value:  # Nếu có thông số cần filter
                order, word, _value = ElasticHelper().get_keywords(value)
                if word: # Nếu cần search lớn nhất, nhỏ nhất, min, max
                    query["sort"] = [
                        {field: {"order": order}}
                    ]
                    value = _value
                query['query']['bool']['must'].append(self.create_filter_range(field, value))
        
        if all(param == '' for param in (power, weight, volume, price)):
            query['sort'] = [
                {"sold_quantity": {"order": "desc"}}
            ]
            value = ""
        print(query)
        return query

    def bulk_search_products(self, client: Elasticsearch, queries: List[Dict]) -> List[Dict]:
        """
        Hàm này dùng để search nhiều query trên elasticsearch.

        Args:
            - client: elasticsearch client
            - queries: list chứa các query cần search
        Return:
            - trả về list chứa kết quả search
        """
        body = []
        for query in queries:
            body.extend([{"index": self.index_name}, query])
        
        results = client.msearch(body=body)
        return results['responses']


    @timing_decorator
    def search_db(self, demands: Dict)-> Tuple[str, List[Dict], int]:

        """
        Hàm này dùng để search thông tin sản phẩm trên elasticsearch.

        Args:
            - demands: dictionary chứa thông tin cần search
        Returns:
            - trả về câu trả lời, list chứa thông tin sản phẩm, và số lượng sản phẩm tìm thấy
        """
        print(demands)
        client = self.elastic_helper.init_elastic(df=self.dataframe, 
                                                  index_name=self.index_name)
        
        list_products = self.dataframe['group_name'].unique()
        product_names = demands['object']
        
        prices = ast.literal_eval(demands['price']) if isinstance(demands['price'], str) else demands['price']
        prices = prices * len(product_names) if len(prices) == 1 else prices

        queries = []
        for product_name, price in zip(product_names, prices):
            match_product, match_score = self.elastic_helper.find_closest_match(product_name, list_products)

            if match_score < ElasticQueryEngine.MATCH_THRESHOLD:
                continue
            product = self.dataframe[self.dataframe['group_name'] == match_product]['group_product_name'].iloc[0]
        
            query = self.create_elasticsearch_query(
                product, product_name, demands.get('specifications'),
                price, demands.get('power'), demands.get('weight'), demands.get('volume')
            )
            queries.append(query)
        
        if not queries:
            return "", []
        
        results = self.bulk_search_products(client, queries)
        out_text = ""
        products_info = []

        for product_name, result in zip(product_names, results):
            for i, hit in enumerate(result['hits']['hits'][:4]):
                product_details = hit['_source']
                out_text += self.format_product_output(i, product_details)
                products_info.append({
                    'object': demands['object'],
                    "product_info_id": product_details['product_info_id'],
                    "product_name": product_details['product_name'],
                    "file_path": product_details['file_path'],
                })
        # print("OUTPUT ELS:", out_text)
        # print("=" * 100)
        return out_text, products_info

    @staticmethod
    def format_product_output(index: int, product_details: Dict) -> str:
        return f"""\n{index + 1}. Tên: '{product_details['product_name']}' 
        - Mã sản phẩm: {product_details['product_info_id']} 
        - Giá: {product_details['lifecare_price']:,.0f} đ
        - Số lượng đã bán: {product_details['sold_quantity']}
        - Thông số : {product_details['specifications']}\n"""