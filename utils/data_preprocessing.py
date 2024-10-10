import pandas as pd
import re
from unidecode import unidecode
from fuzzywuzzy import process, fuzz

class DataProcessing:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = pd.read_excel(file_path)
        self.col = ['weight', 'volume', 'power']
        
    def data_adding(self):
        self.df['power'] = self.df['specification'].apply(self.extract_power)
        self.df['weight'] = self.df['specification'].apply(self.extract_weight)
        self.df['volume'] = self.df['specification'].apply(self.extract_volume)

        self.df[self.col] = self.df[self.col].astype(float)
        self.df['product_code'] = self.df['product_code'].astype(str)
        self.df.to_excel(self.file_path, index=False)
        # self.df.info()
    
    def data_checking(self, old_file_path):
        old_df = pd.read_excel(old_file_path)
        old_df['product_code'] = old_df['product_code'].astype(str)
        old_df[self.col] = old_df[self.col].astype(float)
        
        quantity = 0
        missing_count = 0
        for index, row in self.df.iterrows():
            matching_row = old_df[old_df['product_code'] == row['product_code']]
            if not matching_row.empty:
                matching_row = matching_row.iloc[0]  
                
                difference = []
                for field in self.col:
                    if row[field] != matching_row[field]:
                        difference.append(f"{field}: Cũ = {matching_row[field]}, Mới = {row[field]}\n")
                        quantity += 1

                # if difference:
                #     print(f"Thông số mới: {row['specification']}")
                #     print(f"Product code: {row['product_code']}, Name: {row['product_name']}: \n Các thay đổi: {', '.join(difference)}")
            else:
                #print(f"Sản phẩm mới không có trong file cũ: {row['product_code']}, Name: {row['product_name']}\n")
                #print(f"Thông số mới: {row['specification']}")
                #print(f"{row[self.col]}")
                missing_count += 1

        print("Số lượng khác biệt:", quantity, " trên ", self.df.shape[0] * 3)
        print("Số sản phẩm mới không xuất hiện trong file cũ:", missing_count)
            
    def extract_volume(self, description):
        description = description.replace(',', '.')
        volume_liters = re.findall(r'(\d+(\.\d+)?)\s*l\b|(\d+(\.\d+)?)\s*lít\b', description, re.IGNORECASE)
        volume_ml = re.findall(r'(\d+(\.\d+)?)\s*ml\b', description, re.IGNORECASE)
        volume_value = 0
        if volume_ml:
            volume_value = float(volume_ml[0][0]) / 1000
        if volume_liters:
            volume_value = float(volume_liters[0][0]) if volume_liters[0][0] else float(volume_liters[0][2])

        return volume_value

    def extract_power(self, description):
        description = description.replace(',', '.')

        def clean_number(value):
            if re.match(r'^\d{1,3}\.\d{3}$', value):
                return value.replace('.', '')
            else:
                return value

        power_btu = re.findall(r'(\d+(?:[.,]\d+)?)\s*btu\b[^\d]*', description, re.IGNORECASE)
        power_kw = re.findall(r'(\d+(?:[.,]\d+)?)\s*kw\b[^\d]*', description, re.IGNORECASE)
        power_w = re.findall(r'(\d+(?:[.,]\d+)?)\s*w\b[^\d]*', description, re.IGNORECASE)

        power_value = 0

        if power_btu:
            power_value = float(clean_number(power_btu[0]))

        elif power_kw:
            power_value = float(clean_number(power_kw[0])) * 1000

        elif power_w:
            power_value = float(clean_number(power_w[0]))

        return power_value
    
    def extract_weight(self, description):
        weight = re.findall(r'(\d+(\.\d+)?)\s*kg\b', description, re.IGNORECASE)
        weight_kg = re.findall(r'(\d+(\.\d+)?)\s*g\b', description, re.IGNORECASE)
        weight_value = 0
        if weight:
            weight_value = weight[0][0]
        if weight_kg:
            weight_value = float(weight_kg[0][0])/1000
        return weight_value

def convert_words_to_numbers(text):
    vietnamese_number_dict = {
        'không': '0',
        'một': '1',
        'hai': '2',
        'ba': '3',
        'bốn': '4',
        'năm': '5',
        'sáu': '6',
        'bảy': '7',
        'tám': '8',
        'chín': '9'
    }
    for word, number in vietnamese_number_dict.items():
        text = re.sub(r'\b' + re.escape(word) + r'\b', number, text, flags=re.IGNORECASE)
    text = re.sub(r'([0-9]+)([a-zA-Z]+)', r'\1 \2', text)  
    return text

def preprocess(text):
    text = re.sub(r'[^\w\s]', '', text) 
    text = re.sub(r'([0-9]+)([a-zA-Z]+)', r'\1 \2', text) 
    text = re.sub(r'nlmt', r'năng lượng mặt trời', text) 
    text = re.sub(r'mln', r'lọc nước', text) 
    text = re.sub(r'máy', r'', text) 
    text = re.sub(r'[.,]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = ' '.join(convert_words_to_numbers(word) if word.isalpha() else word for word in text.split())
    return text

def contains_digit(msp):
    return bool(re.search(r'\d', msp))

def contains_all_words(product_name, search_query):
    normalized_product_name = preprocess(product_name)
    normalized_search_query = preprocess(search_query)
    
    words = set(unidecode(normalized_search_query.lower()).split())
    product_words = set(unidecode(normalized_product_name.lower()).split())
    return words.issubset(product_words)


