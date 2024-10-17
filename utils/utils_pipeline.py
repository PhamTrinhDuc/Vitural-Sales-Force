# Helper functions
import re
import markdown
import logging 
import pandas as pd
from typing import List, Dict, Any
from ast import literal_eval
from source.model.loader import ModelLoader

class HelperPiline:
    def __init__(self):
        pass
    
    def _clean_html(self, html_text: str) -> str:
        """
        Xóa các thẻ html từ phần output của chatbot
        Args:
            html_text: str: phần trả lời của bot sau khi đã format sang html
        Returns:
            clean_text: str: phần trả lời của bot sau khi đã xóa các thẻ html
        """
        clean_text = re.sub(r'<[^>]+>', '', html_text)
        clean_text = re.sub(r'\n+', '\n', clean_text)
        clean_text = clean_text.strip()
        return clean_text
    
    def _product_seeking(self, output_from_llm: str, query_rewritten: str,  dataframe: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Get info product in output from llm.
        Args:
            - output_from_llm: output of llm.
            - path_df: data frame constain list product
        Returns:
            - results: product information obtained
        """
        results = []
        try: 
            for index, row in dataframe.iterrows():
                if any(str(item).lower() in output_from_llm.lower() or str(item) in query_rewritten for item in (row['product_name'], row['product_info_id'])):
                    product = {
                        "product_id": row['product_info_id'],
                        "product_name": row['product_name'],
                        "link_image": row['file_path']
                    }
                    results.append(product)
            return results
        except Exception as e:
            logging.error("PRODUCT SEEKING ERROR: " + str(e))
            return results
    
    
    def _product_confirms(self, output_from_llm: str, query_rewritten: str, dataframe: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Get info product in output from llm.
        Args:
            - output_from_llm: output of llm.
            - query_rewritten: rewritten query.
            - dataframe: data frame containing list of products
        Returns:
            - results: product information obtained
        """
        llm = ModelLoader().load_rag_model()
        
        AMOUNT_PROMPT = """Lấy ra số lượng sản phẩm và giá sản phẩm khách đã chốt trong form đơn hàng:
        Ví dụ:
        Input:  <p>Thông tin đơn hàng:</p><ul>
                <li><strong>Tên:</strong> Hoàng  </li>
                <li><strong>SĐT:</strong> 0886945868  </li>
                <li><strong>Sản phẩm:</strong> Điều hòa MDV - Inverter 9000 BTU  </li>
                <li><strong>Số lượng:</strong> 3 cái  </li>
                <li><strong>Giá 1 sản phẩm:</strong> 6,000,000 đồng  </li>
        Format output: 3 | 6,000,000
        ---------
        From đơn hàng:
        {output_from_llm}
        Lưu ý: trả ra đúng format, không trả ra gì khác"""
        try: 
            results = {}
            response = llm.invoke(AMOUNT_PROMPT.format(output_from_llm=output_from_llm)).content
            if '|' in response:
                amount = response.split("|")[0].strip()
                price = response.split("|")[1].strip()
                print("AMOUNT: ", amount)
                print("PRICE: ", price)
                if amount:
                    results['amount'] = amount
                if price: 
                    results['price'] = price
            else:
                return results
            
            for index, row in dataframe.iterrows():
                if any(str(item).lower() in output_from_llm.lower() or str(item).lower() in query_rewritten.lower() 
                       for item in (row['product_name'], row['product_info_id'])):
                    results.update({
                        "product_id": row['product_info_id'],
                        "product_name": row['product_name'],
                        "link_image": row['file_path']
                    })
            return results
        except Exception as e:
            logging.error("PRODUCT CONFIRMS ERROR: " + str(e))
            return results
        
    def _format_to_HTML(self, markdown_text: str) -> str:
        """Converts a given markdown text from output llm to HTML format.
        Args:
            markdown_text (str): The markdown text to be converted.
        Returns:
            str: The converted HTML text.
        """
        md = markdown.Markdown(extensions=['tables'])
        html_output = md.convert(markdown_text)
        return html_output
    
    def _double_check(self, question: str, dataframe: pd.DataFrame) -> str:
        """
        Double check the product in question.
        Args:
            - question: question from user.
            - dataframe: data frame constain list product
        Returns:
            - results: product information obtained
        """
        result = ""
        try: 
            for index, row in dataframe.iterrows():
                if any(str(item).lower() in question.lower() for item in (row['product_name'], row['product_info_id'])):
                    result += f"Name: {row['product_name']} - ID: {row['product_info_id']} - Price: {row['lifecare_price']}\n"
            return result
        except Exception as e:
            logging.error("DOUBLE CHECK ERROR: " + str(e))
            return result
        