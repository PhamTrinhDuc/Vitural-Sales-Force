# Helper functions
import re
import json
import markdown
import logging 
import pandas as pd
from typing import List, Dict, Any, Union
from source.model.loader import ModelLoader

class HelperPiline:
    def __init__(self):
        pass

    @staticmethod
    def _clean_html(html_text: str) -> str:
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
    
    @staticmethod
    def _product_seeking(output_from_llm: str, query_rewritten: str,  dataframe: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Tìm kiếm sản phẩm dựa trên đầu ra từ mô hình ngôn ngữ và truy vấn đã được viết lại.
        Hàm này duyệt qua từng hàng trong DataFrame và kiểm tra xem tên sản phẩm hoặc ID thông tin sản phẩm
        có xuất hiện trong đầu ra từ mô hình ngôn ngữ hoặc truy vấn đã viết lại hay không. Nếu có, nó sẽ thêm
        sản phẩm vào danh sách kết quả.
        Args:
            output_from_llm (str): Đầu ra từ mô hình ngôn ngữ.
            query_rewritten (str): Truy vấn đã được viết lại.
            dataframe (pd.DataFrame): DataFrame chứa thông tin sản phẩm.
        Returns:
            List[Dict[str, Any]]: Danh sách các sản phẩm tìm được, mỗi sản phẩm là một từ điển chứa ID sản phẩm,
                                    tên sản phẩm và đường dẫn hình ảnh.
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
    
    @staticmethod
    def _extract_single_number(text: str, mode: str) -> Union[int, None]:
        """
        Trích xuất một số duy nhất từ chuỗi văn bản dựa trên chế độ được chỉ định.
        Args:
            text (str): Chuỗi văn bản chứa số cần trích xuất.
            mode (str): Chế độ trích xuất, có thể là 'price' hoặc 'amount'.
                - 'price': Trích xuất số dạng giá tiền, ví dụ: "1,234.56".
                - 'amount': Trích xuất số dạng số lượng, ví dụ: "1234.56".
        Returns:
            int: Số được trích xuất từ chuỗi văn bản. Nếu không tìm thấy số, trả về None.
        """
        if mode == 'price':
            pattern = r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)'
            match = re.search(pattern, text)
            if match:
                number_str = match.group(1)
                number = int(number_str.replace(',', ''))
                return number
        elif mode == 'amount':
            pattern = r'\d+(?:\.\d+)?'
            match = re.search(pattern, text)
            
            if match:
                number = int(match.group())
                return number
        return None
    
    def _product_confirms(self, 
                          output_from_llm: str, 
                          query_rewritten: str, 
                          dataframe: pd.DataFrame) -> List[Dict[str, Any]]:
        """

        Trích xuất thông tin xác nhận sản phẩm từ đầu ra của mô hình ngôn ngữ và đối chiếu với DataFrame đã cho.
        Args:
            output_from_llm (str): Chuỗi đầu ra từ mô hình ngôn ngữ chứa thông tin đơn hàng.
            query_rewritten (str): Chuỗi truy vấn đã được viết lại.
            dataframe (pd.DataFrame): DataFrame chứa thông tin sản phẩm với các cột 'product_name', 'product_info_id', và 'file_path'.
        Returns:
            List[Dict[str, Any]]: Danh sách các từ điển chứa thông tin sản phẩm được trích xuất như số lượng, giá, product_id, product_name, và link_image.
        
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
        Format output: 
        {
            "amount": 3,
            "price": 6,000,000
        }
        ---------
        From đơn hàng:
        {output_from_llm}
        Lưu ý: trả ra đúng format, không trả ra gì khác"""
        results = []
        try: 
            result = {}
            response = llm.invoke(AMOUNT_PROMPT.format(output_from_llm=output_from_llm)).content
            response_json = json.loads(json.dumps(response))
            amount = response_json.get("amount", "")
            price = response_json.get("price", "")
            print("AMOUNT: ", amount)
            print("PRICE: ", price)
            if amount:
                result['amount'] = self._extract_single_number(text=amount, mode='amount')
            if price: 
                result['price'] = self._extract_single_number(text=price, mode='price')
            else:
                return results
            
            for index, row in dataframe.iterrows():
                if any(str(item).lower() in output_from_llm.lower() or str(item).lower() in query_rewritten.lower() 
                       for item in (row['product_name'], row['product_info_id'])):
                    result.update({
                        "product_id": row['product_info_id'],
                        "product_name": row['product_name'],
                        "link_image": row['file_path'],
                        "product_code": row['product_code']
                    })
                    results.append(result)
            return results
        except Exception as e:
            logging.error("PRODUCT CONFIRMS ERROR: " + str(e))
            return results
    
    @staticmethod
    def _format_to_HTML(markdown_text: str) -> str:
        """
        
        Chuyển đổi văn bản Markdown thành HTML.
        Args:
            markdown_text (str): Văn bản Markdown cần chuyển đổi.
        Returns:
            str: Chuỗi HTML đã được chuyển đổi từ Markdown.
        
        """
        md = markdown.Markdown(extensions=['tables'])
        html_output = md.convert(markdown_text)
        return html_output

    @staticmethod
    def _double_check(question: str, dataframe: pd.DataFrame) -> str:
        """

        Kiểm tra lại thông tin sản phẩm trong câu hỏi dựa trên dữ liệu từ dataframe.
        Hàm này sẽ duyệt qua từng hàng trong dataframe và kiểm tra xem tên sản phẩm hoặc ID sản phẩm
        có xuất hiện trong câu hỏi hay không. Nếu có, thông tin về sản phẩm sẽ được thêm vào kết quả.
        Args:
            question (str): Câu hỏi chứa thông tin cần kiểm tra.
            dataframe (pd.DataFrame): DataFrame chứa dữ liệu sản phẩm.
        Returns:
            str: Chuỗi chứa thông tin về các sản phẩm phù hợp với câu hỏi.
        
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
        