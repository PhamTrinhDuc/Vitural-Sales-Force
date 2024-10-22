import requests
import pandas as pd
import re
import json
import logging
from configs.config_system import LoadConfig

CONFIG_SYSTEM = LoadConfig()


# Hàm lấy dữ liệu từ API
def get_superapp_data(code_member: str) -> pd.DataFrame:
    url = "http://10.207.112.54:8808/aio/product/filterProductForAI"
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
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        if response.status_code == 200:
            response = response.json()
            # Danh sách lưu thông tin sản phẩm
            product_list = []

            # Trích xuất các trường thông tin cần thiết
            for product in data['data']['content']:
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
            return df  # Di chuyển return vào trong if
        else:
            logging.info(f"GET CODE MEMBER: Lỗi khi gọi API: {response.status_code}")
            return None  # Thêm return None khi có lỗi
    except requests.Timeout:
        logging.info("GET CODE MEMBER: Yêu cầu đã vượt quá thời gian chờ")
    except requests.RequestException as e:
        logging.info(f"GET CODE MEMBER: Đã xảy ra lỗi khi gửi yêu cầu: {str(e)}")
    except json.JSONDecodeError:
        logging.info("GET CODE MEMBER: Không thể giải mã phản hồi JSON")
    except Exception as e:
        logging.info(f"GET CODE MEMBER: Lỗi không mong đợi: {str(e)}")
    return None

# Class xử lý dữ liệu
class DataProcessing:
    def __init__(self, data):
        self.df = pd.DataFrame(data)
        self.col = ['weight', 'volume', 'power']
        self.data_adding()
        
    def data_adding(self):
        self.df['power'] = self.df['specifications'].apply(self.extract_power)
        self.df['weight'] = self.df['specifications'].apply(self.extract_weight)
        self.df['volume'] = self.df['specifications'].apply(self.extract_volume)
        self.df['specifications'] = self.df['specifications'].apply(self.clean_html)
        self.df['shortDescription'] = self.df['shortDescription'].apply(self.clean_html)
        self.df['productDescription'] = self.df['productDescription'].apply(self.clean_html)

        self.df[self.col] = self.df[self.col].astype(float)
        self.df['productCode'] = self.df['productCode'].astype(str)
    
    def clean_html(self, html_text: str) -> str:
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
    
    def extract_volume(self, description):

        # Thay đổi dấu phẩy thành dấu chấm (nếu có)
        description = description.replace(',', '.')

        # Tìm thể tích với các đơn vị L, lít, và ml
        volume_liters = re.findall(r'(\d+(\.\d+)?)\s*l(?:ít)?\b', description, re.IGNORECASE)
        volume_ml = re.findall(r'(\d+(\.\d+)?)\s*ml\b', description, re.IGNORECASE)
        
        volume_value = 0
        
        # Nếu tìm thấy thể tích lít
        if volume_liters:
            volume_value = float(volume_liters[0][0])
        # Nếu tìm thấy thể tích ml
        if volume_ml:
            volume_value += float(volume_ml[0][0]) / 1000  # Chuyển đổi ml sang lít

        return volume_value
    def extract_power(self, description):
        # Thay đổi dấu phẩy thành dấu chấm (nếu có)
        description = description.replace(',', '.')

        def clean_number(value):
            # Nếu số có dạng 1.000 (chấm là phân cách nghìn), ta loại bỏ dấu chấm
            if re.match(r'^\d{1,3}\.\d{3}$', value):
                return value.replace('.', '')
            else:
                return value

        # Sử dụng regex để tìm các đơn vị công suất khác nhau trong chuỗi
        power_w = re.findall(r'(\d+(?:[.,]\d+)?)\s*w\b', description, re.IGNORECASE)
        power_kw = re.findall(r'(\d+(?:[.,]\d+)?)\s*kw\b', description, re.IGNORECASE)
        power_vw = re.findall(r'(\d+(?:[.,]\d+)?)\s*v(?:/|\\| )?w\b', description, re.IGNORECASE)  # Dạng V/W
        power_btu = re.findall(r'(\d+(?:[.,]\d+)?)\s*btu\b', description, re.IGNORECASE)  # Dạng BTU

        power_value = 0

        # Nếu tìm thấy đơn vị BTU
        if power_btu:
            power_value = float(clean_number(power_btu[0]))
        
        # Nếu tìm thấy đơn vị W (Watt)
        elif power_w:
            power_value = float(clean_number(power_w[0]))
        
        # Nếu tìm thấy đơn vị kW (Kilowatt)
        elif power_kw:
            power_value = float(clean_number(power_kw[0])) * 1000  # Chuyển kW sang W
        
        # Nếu tìm thấy đơn vị V/W (Volts/Watt, thông thường trong các bảng năng lượng mặt trời)
        elif power_vw:
            # Bạn có thể tùy chỉnh cách xử lý trường hợp này, ví dụ như nhân với một hệ số nếu cần
            power_value = float(clean_number(power_vw[0]))  # Dạng này có thể chỉ để mô tả chứ không phải công suất thực

        return power_value
    
    def extract_weight(self, description):

        # Thay đổi dấu phẩy thành dấu chấm (nếu có)
        description = description.replace(',', '.')

        # Tìm trọng lượng với các đơn vị kg và g
        weight_kg = re.findall(r'(\d+(?:[.,]\d+)?)\s*kg\b', description, re.IGNORECASE)
        weight_g = re.findall(r'(\d+(?:[.,]\d+)?)\s*g\b', description, re.IGNORECASE)
        
        weight_value = 0
        
        # Nếu tìm thấy trọng lượng kg
        if weight_kg:
            weight_value = float(weight_kg[0])
        # Nếu tìm thấy trọng lượng g
        elif weight_g:
            weight_value = float(weight_g[0]) / 1000  # Chuyển đổi g sang kg

        return weight_value
    
# Function xử lý dữ liệu cho từng member và lưu xuống Excel
def process_data_and_save():
    for code in CONFIG_SYSTEM.MEMBER_CODE:
        # Gọi API để lấy dữ liệu
        data = get_superapp_data(code)
        
        if data is not None and not data.empty:
            # Tạo đối tượng DataProcessing và xử lý dữ liệu
            data_processor = DataProcessing(data)
            
            data_processor.df = data_processor.df.sort_values(by='productGroupId')
            # Lưu dữ liệu vào Excel
            file_path = f'data/data_private/product_superapp_{code}.xlsx'
            data_processor.df.to_excel(file_path, index=False)
            print(f"Dữ liệu đã được lưu vào {file_path}")
        else:
            print("Không có dữ liệu để xử lý.")


if __name__ == "__main__":
    process_data_and_save()