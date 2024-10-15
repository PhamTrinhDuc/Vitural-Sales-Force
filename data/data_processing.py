import requests
import pandas as pd
import re

# Hàm lấy dữ liệu từ API
def get_superapp_data():
    url = 'https://apis-public.congtrinhviettel.com.vn/aio/product/filterProduct'
    headers = {'Content-Type': 'application/json'}
    payload = {
        "dataRequest": {
            "keyWord": None,
            "brand": None,
            "productGroupIds": [],
            "productBrandIds": []
        },
        "pageRequest": {
            "page": 0,
            "size": 300
        }
    }

    # Gọi API với phương thức POST
    response = requests.post(url, headers=headers, json=payload)
    # Kiểm tra xem API trả về kết quả thành công không
    if response.status_code == 200:
        data = response.json()

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
                'price': product['productPrice']['price']
            }
            product_list.append(product_info)

        # Chuyển dữ liệu sang DataFrame
        df = pd.DataFrame(product_list)
        return df  # Di chuyển return vào trong if
    else:
        print(f"Lỗi khi gọi API: {response.status_code}")
        return None  # Thêm return None khi có lỗi

# Class xử lý dữ liệu
class DataProcessing:
    def __init__(self, data):
        self.df = pd.DataFrame(data)
        self.col = ['weight', 'volume', 'power']
        
    def data_adding(self):
        self.df['power'] = self.df['specifications'].apply(self.extract_power)
        self.df['weight'] = self.df['specifications'].apply(self.extract_weight)
        self.df['volume'] = self.df['specifications'].apply(self.extract_volume)

        self.df[self.col] = self.df[self.col].astype(float)
        self.df['productCode'] = self.df['productCode'].astype(str)
    
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

        power_value = 0

        # Nếu tìm thấy đơn vị W (Watt)
        if power_w:
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
    
# Function xử lý dữ liệu và lưu xuống Excel
def process_data_and_save():
    # Gọi API để lấy dữ liệu
    data = get_superapp_data()
    
    if data is not None and not data.empty:
        # Tạo đối tượng DataProcessing và xử lý dữ liệu
        data_processor = DataProcessing(data)
        data_processor.data_adding()
        
        data_processor.df = data_processor.df.sort_values(by='productGroupId')
        # Lưu dữ liệu vào Excel
        file_path = 'data/data_private/product_info_superapp.xlsx'
        data_processor.df.to_excel(file_path, index=False)
        print(f"Dữ liệu đã được lưu vào {file_path}")
    else:
        print("Không có dữ liệu để xử lý.")

if __name__ == "__main__":
    process_data_and_save()