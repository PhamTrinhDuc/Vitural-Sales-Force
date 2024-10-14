# Helper functions
import re
import markdown
import logging 
import pandas as pd
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI


class HelperPiline:
    def __init__(self):
        pass
    
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
            - path_df: data frame constain list product
        Returns:
            - results: product information obtained
        """
        llm = ChatOpenAI()
        PROMPT = """Lấy ra số lượng sản phẩm mà khách đã chốt trong form thông tin đơn hàng:
        
        Ví dụ:
        In: <p>Thông tin đơn hàng:</p><ul>
            <li><strong>Tên:</strong> Hoàng  </li>
            <li><strong>SĐT:</strong> 0886945868  </li>
            <li><strong>Sản phẩm:</strong> Điều hòa MDV - Inverter 9000 BTU  </li>
            <li><strong>Số lượng:</strong> 3 cái  </li>
            <li><strong>Tổng giá trị:</strong> 6,015,000 đồng  </li>
        Out: 3
        
        {output_from_llm}
        Lưu ý: Nếu không có thì trả ra 0. Chỉ trả ra con số, không trả ra gì khác"""
        
        amount = llm.invoke(PROMPT.format(output_from_llm=output_from_llm)).content
        print("AMOUNT: ", amount)
        
        results = self._product_seeking(output_from_llm, query_rewritten, dataframe)
        if amount:
            for result in results:
                result.pop("link_image", None)
                result['amount'] = amount
        else:
            results = []
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
    
    def _add_short_link(self, output_from_llm: str, product_info: List[Dict[str, Any]]) -> str:

        """Adds a short link to the output from LLM if a quantity is found in the output.
        Args:
            output_from_llm (str): The output string from the LLM which may contain a quantity in a specific format.
        Returns:
            str: The modified output string with an added short link if a quantity is found, otherwise returns the original output string.
        """
        try:
            if len(product_info) == 0: # nếu không tìm thấy sản phẩm
                return output_from_llm
            
            pattern = r'<li><strong>Số lượng:</strong>\s*(\d+)\s*(cái|sản phẩm|)</li>' or r'Số lượng:\s*(\d+)\s*(cái|sản phẩm|)' or r'<br\s*/?>\s*Số lượng:\s*(\d+)\s*(cái|sản phẩm|)\s*<br\s*/?>' or r'<li><strong>Số lượng:</strong>\s*(\d+)\s*</li>' or r'Số lượng:\s*(\d+)\s*(cái|sản phẩm|)'  
            
            match = re.search(pattern, output_from_llm.lower())
            quantity = match.group(1) if match else None
            print(quantity)
            if quantity and product_info['product_id']: # nếu tìm thấy số lượng
                short_link = create_short_link(product_id=product_info['product_id'], quantity=quantity)
                return f"""{output_from_llm} <a href={short_link['shortLink']} style="color: blue;">Xác nhận</a>"""
            return output_from_llm
        except Exception as e:
            logging.error("ADD SHORT LINK ERROR: " + str(e))
            return output_from_llm
        
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
        