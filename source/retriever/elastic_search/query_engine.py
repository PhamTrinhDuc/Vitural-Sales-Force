import ast
import pandas as pd
from icecream import ic
from typing import Dict, List, Tuple, Optional
from elasticsearch import Elasticsearch
from utils import timing_decorator
from source.retriever.elastic_search import ElasticHelper
from configs import SYSTEM_CONFIG


NUMBER_SIZE_ELAS = SYSTEM_CONFIG.NUM_SIZE_ELAS
DATAFRAME = pd.read_excel(SYSTEM_CONFIG.ALL_PRODUCT_FILE_CSV_STORAGE)
INDEX_NAME = SYSTEM_CONFIG.INDEX_NAME
MATCH_THRESHOLD = 75

def create_filter_range(field: str, value: str) -> Dict:
    """
    Hàm này tạo ra filter range cho câu query.

    Args:
        - field: tên field cần filter
        - value: giá trị cần filter
    Return:
        - trả về dictionary chứa thông tin filter range
    """
    min_value, max_value = ElasticHelper().parse_specification_range(value)
    range_filter = {
        "range": {
            field: {
                "gte": min_value,
                "lte": max_value
            }
        }
    }
    return range_filter

def create_elasticsearch_query(product: str, product_name: str, 
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
        "size": NUMBER_SIZE_ELAS
    }

    for field, value in [('lifecare_price', price), ('power', power), ('weight', weight), ('volume', volume)]:
        if value:  # Nếu có thông số cần filter
            order, word, _value = ElasticHelper().get_keywords(value)
            if word: # Nếu cần search lớn nhất, nhỏ nhất, min, max
                query["sort"] = [
                    {field: {"order": order}}
                ]
                value = _value
            query['query']['bool']['must'].append(create_filter_range(field, value))
    return query

def bulk_search_products(client: Elasticsearch, queries: List[Dict]) -> List[Dict]:
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
        body.extend([{"index": INDEX_NAME}, query])
    
    results = client.msearch(body=body)
    return results['responses']


@timing_decorator
def search_db(demands: Dict)-> Tuple[str, List[Dict], int]:

    """
    Hàm này dùng để search thông tin sản phẩm trên elasticsearch.

    Args:
        - demands: dictionary chứa thông tin cần search
    Returns:
        - trả về câu trả lời, list chứa thông tin sản phẩm, và số lượng sản phẩm tìm thấy
    """

    client = ElasticHelper().init_elastic(DATAFRAME, INDEX_NAME)
    list_products = DATAFRAME['group_name'].unique()
    product_names = demands['object']
    
    prices = ast.literal_eval(demands['price']) if isinstance(demands['price'], str) else demands['price']
    prices = prices * len(product_names) if len(prices) == 1 else prices

    queries = []
    for product_name, price in zip(product_names, prices):
        match_product, match_score = ElasticHelper().find_closest_match(product_name, list_products)

        if match_score < MATCH_THRESHOLD:
            continue
        product = DATAFRAME[DATAFRAME['group_name'] == match_product]['group_product_name'].iloc[0]
    
        query = create_elasticsearch_query(
            product, product_name, demands.get('specifications'),
            price, demands.get('power'), demands.get('weight'), demands.get('volume')
        )
        # print(query)

        queries.append(query)
    
    if not queries:
        return "", []
    
    results = bulk_search_products(client, queries)
    out_text = ""
    products_info = []

    for product_name, result in zip(product_names, results):
        for i, hit in enumerate(result['hits']['hits'][:4]):
            product_details = hit['_source']
            out_text += format_product_output(i, product_details)
            products_info.append({
                "product_info_id": product_details['product_info_id'],
                "product_name": product_details['product_name'],
                "file_path": product_details['file_path']
            })
    # print(out_text)
    return out_text, products_info


def format_product_output(index: int, product_details: Dict) -> str:
    return (f"\n{index + 1}. *{product_details['product_name']} - Mã: {product_details['product_code']}\n"
            f"  Thông số sản phẩm: {product_details['specification']}\n"
            f"  Giá tiền: {product_details['lifecare_price']:,.0f} đ*\n")