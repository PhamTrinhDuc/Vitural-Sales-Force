import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz, process
from typing import List, Optional, Dict, Union, Any
from sklearn.metrics.pairwise import cosine_similarity
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from configs import SYSTEM_CONFIG
from source.prompt.template import PROMPT_SIMILAR_PRODUCT
from source.model.loader import ModelLoader
from utils import timing_decorator


class SimilarProductSearchEngine:
    def __init__(self, 
                 product_find: str,
                 user_info: Dict[str, Any],
                 product_similar_path: Optional[str] = SYSTEM_CONFIG.SIMILAR_PRODUCT_STORAGE,
                 product_origin_path: Optional[str] = SYSTEM_CONFIG.ALL_PRODUCT_FILE_CSV_STORAGE):
        
        self.model_embed = ModelLoader().load_embed_baai_model()
        self.llm = ModelLoader().load_rag_model()
        self.dataframe_similar = pd.read_csv(product_similar_path) # dataframe chứa sản phẩm tương tự
        self.dataframe_product = pd.read_excel(product_origin_path) # dataframe chứ sản phẩm chính 
        self.list_product_similar = self.dataframe_similar["product_name"].tolist()
        self.list_origin_product = self.dataframe_product["product_name"].tolist() 
        self.product_find = self.find_nearest_product(product_find, self.list_origin_product)
        self.user_info = user_info


    def find_nearest_products(self, query_product: str, list_product: List[str], top_k: Optional[int] = 5) -> List:
        """
        Hàm này dùng để tìm top_k sản phẩm gần giống nhất với câu query của người dùng trong list_product.

        Args:
            - query_product: sản phầm từ câu query của người dùng
            - list_product: list chứa tên các sản phẩm
            - n: số lượng sản phẩm muốn tìm

        Returns:
            - trả về danh sách các cặp (tên sản phẩm, độ match) theo thứ tự giảm dần của độ match
        """
        if query_product:
            matches = process.extract(query_product, list_product, scorer=fuzz.partial_ratio, limit=top_k)
            # for match in matches:
            #     print(f"Có phải bạn tìm kiếm sản phẩm {match[0]}")
            #     print("Độ match:", match[1])
            return matches
        return []
    
    def find_nearest_product(self, query_product: str, list_product: List[str]) -> Union[str, None]:
        """
        Hàm này dùng để tìm sản phẩm gần giống nhất với câu query của người dùng trong list_product.

        Args:
            - query_product: sản phầm từ câu query của người dùng
            - list_product: list chứa tên các sản phẩm

        Returns:
            - trả về tên sản phẩm gần giống nhất
        """
        match = process.extractOne(query_product, list_product, scorer=fuzz.partial_ratio)
        if match[1] >= 65:
            return match[0]
        return None
    
    def find_nearest_price(self, 
                           price_product_find: float, 
                           price_product_similar: float, 
                           threshold_down: Optional[float] = 0.8,
                           threshold_up: Optional[float] = 1.25)-> Union[float, None]:

        """
        Giá tiền của sản phẩm tương tự có gần với sản phẩm cần tìm không. Nếu chênh lệch nhỏ hơn 2tr thì trả về giá sản phẩm tương tự, nếu không trả về None.
        Args:
            - price_product: giá tiền của sản phẩm cần tìm
            - price_product_similar: giá tiền của sản phẩm tương tự
            - threshold_up, threshold_down: ngưỡng giá tiền chênh lệch
        Returns:
            - giá tiền của sản phẩm tương tự hoặc None
        """

        scale = price_product_find / price_product_similar
        if scale <= threshold_down or scale >= threshold_up:
            return price_product_similar
        return None
    

    def find_nearest_specifications(self, 
                                    specifications_product_find: str, 
                                    specifications_product_similar: str, 
                                    threhold: Optional[float] = 0.3)-> Union[str, None]:
        """
        Thông số kỹ thuật của sản phẩm tương tự có gần với sản phẩm cần tìm không. Nếu độ similar lớn hơn ngưỡng thì trả về thông số sản phẩm tương tự, nếu không trả về None.
        Args:
            - specifications_product: thông số kỹ thuật của sản phẩm cần tìm
            - specifications_product_similar: thông số kỹ thuật của sản phẩm tương tự
            - weight_similar: trọng số của độ tương đồng
        Returns:
            - similar_product_found: thông số kỹ thuật của sản phẩm tương tự hoặc None
        """
        vector_embed = list(self.model_embed.embed(documents=[specifications_product_find, 
                                                              specifications_product_similar]))
        vector1 = np.array(vector_embed[0]).reshape(-1, 1)
        vector2 = np.array(vector_embed[1]).reshape(-1, 1)

        score_similarity = cosine_similarity(vector1, vector2)[0][0]
        if score_similarity >= threhold:
            return specifications_product_similar
        return None
        
    @timing_decorator
    def search(self) -> List[str]:
        """
        1. Tìm 5 sản phẩm gần giống với sản phẩm cần tìm(product_find) trong danh sách sp tương tự(list_product_similar)
        2. Duyệt qua ds sp tìm được, so sánh giá(find_nearest_price) và thông số kỹ thuật của sản phẩm (find_nearest_specifications) cần tìm (product_find) với sp trong danh sách. 
        Args:
            - product_name: tên sản phẩm cần tìm kiếm
        Returns:
            - Danh sách các sản phẩm tương tự tìm được
        """

        similar_product_found = []
        matches_product = self.find_nearest_products(self.product_find, self.list_product_similar)
        if len(matches_product) == 0:
            return similar_product_found
        matches_product = [(value[0], value[1]) for value in matches_product if value[1] >= 65] # những sản phẩm tương tự với sản phẩm cần tìm.
        for idx, (product_match, match_score) in enumerate(matches_product):
            # break
            price_product_find = float(self.dataframe_product.loc[self.dataframe_product['product_name'].str.lower() == self.product_find.lower()]['lifecare_price'].values[0]) # HIÊN ĐANG GẶP LỖI NẾU TRONG FILE KH CÓ SẢN PHẨM 'product_find'
            specifications_product_find = self.dataframe_product.loc[self.dataframe_product['product_name'].str.lower() == self.product_find.lower()]['specification'].values[0]

            price_product_similar = float(self.dataframe_similar.loc[self.dataframe_similar['product_name'].str.lower() == product_match.lower()]['product_price'].values[0])
            specifications_product_similar = " ".join(self.dataframe_similar.loc[self.dataframe_similar['product_name'].str.lower() == product_match.lower()]['specifications'].values[0].split("\n"))

            price_similar = self.find_nearest_price(price_product_find, price_product_similar)
            specifications_similar = self.find_nearest_specifications(specifications_product_find, specifications_product_similar)

            product_details = {
                'product_name': product_match,
                'lifecare_price': price_similar,
                'specification': specifications_similar
            }

            # print(product_details)
            if price_similar and specifications_similar:
                similar_product_found.append(self.format_product_output(idx, product_details))
        
        return similar_product_found
                
    def format_product_output(self, index: int, product_details: Dict[str, Any]) -> str:
        return (f"{index + 1}. Sản phẩm: {product_details['product_name']} - Giá tiền: {product_details['lifecare_price']:,.0f} đ*\n")
                # f"  Thông số sản phẩm: {product_details['specification']}\n")
    
    @timing_decorator
    def invoke(self, query: str) -> str:
        """
        Nhận câu hỏi tìm sản phẩm tương tự và sản phẩm tương tự trong câu hỏi đó, sau đó trả ra kết quả.
        Args:
            - query: câu hỏi tìm sản phẩm tương tự
            - product_name: tên sản phẩm cần tìm
        Returns:
            - response: câu trả lời cho người dùng
        """
        PROMPT_TEMPLATE = PromptTemplate(
            input_variables=['question', 'context', 'user_info'],
            template=PROMPT_SIMILAR_PRODUCT
        )

        chain = PROMPT_TEMPLATE | self.llm | StrOutputParser()
        similer_product_found = self.search()

        response = chain.invoke({
            'question': query,
            'context': similer_product_found,
            'user_info': self.user_info['name']
        })
        print(self.user_info)
        return response

if __name__ == "__main__":
    pass