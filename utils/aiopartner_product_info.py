import schedule
import re
import time
import os
import requests
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
import pandas as pd
# from config_app.config import get_config
# from utils.data_preprocessing import DataProcessing


def remove_html(text):
     text_only = re.sub(pattern=r"<[^>]*>", string = text, repl="")
     return text_only


def download_data_super_app():
    # super app
    url = "http://10.248.242.181:8808/aio/product/filterProduct"

    headers = {
        'Content-Type': 'application/json'
    }

    data = {
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
    list_id_product_superapp = [] 
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
    
        data = response.json()
        with open("data/data_private/data_super_app.json", 'w', encoding="utf-8") as file:
            json.dump(data, file)
            
        df = pd.read_json("data/data_private/data_super_app.json")['data']['content'] # list json 
        for idx, data in enumerate(df):
            for item, value in data.items():
                if item == "shortDescription":
                    df[idx]['shortDescription'] = remove_html(value)

        df = pd.DataFrame(df)
        df.to_excel("data/data_private/data_super_app.xlsx", index=False)

# aio partner
def download_data_aio_partner():
    host = "10.248.242.90"
    port = 5000
    dbname = "vcc_dw"
    username = "postgres"
    password = "Vcc@123#20200"

    encoded_password = quote_plus(password)
    # Tạo URL kết nối
    dsn = f"postgresql+psycopg2://{username}:{encoded_password}@{host}:{port}/{dbname}"
    # Tạo engine kết nối
    engine = create_engine(dsn)
    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()
    query = "select * from vcc_cntt.online_cntt_ai_project_ds_san_pham_aio_partner"
    result = session.execute(query)
    rows = result.fetchall()
    columns = result.keys()
    # Close the session
    session.close()
    # Convert the result to a Pandas DataFrame
    df = pd.DataFrame(rows, columns=columns)
    df.to_excel("data/data_private/aio_partner_original.xlsx", index=False)
    return df


def match_product_ID():
    df = pd.read_excel("./data/data_private/product_final_300_aio_partner.xlsx")
    list_product_code_superapp = pd.read_excel("./data/data_private/data_super_app.xlsx")['productCode'].tolist()
    list_product_code_superapp = [str(i).strip() for i in list_product_code_superapp]
    print(len(list_product_code_superapp))


    index_to_drop = []
    for index, row in df.iterrows():
        if str(row['product_code']).strip() not in list_product_code_superapp:
            print(row['product_code'])
            index_to_drop.append(index)
    df = df.drop(index_to_drop)
    df.to_excel("./data/data_private/product_aio_partner_after_match.xlsx", index=False)
    print(len(df))
        
        
        
def job():
    df = db()
    original_file_path = config_app["parameter"]["data_private"]
    df_old = pd.read_excel(original_file_path)
    
    # Lưu lại data excel cũ
    current_time = time.strftime("%m%d")  
    base_name, extension = os.path.splitext(original_file_path)
    new_file_name = f"{base_name}_{current_time}{extension}"
    df_old.to_excel(new_file_name, index=False)
    print(f"Old data stored to {new_file_name} at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Xử lý data mới
    processor = DataProcessing(original_file_path)
    processor.data_adding()
    print(f"New data stored to {original_file_path} at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # So sánh với data chuẩn nhất trước đó:
    processor.data_checking("data/product_final_300_check.xlsx")

# # Lập lịch để chạy công việc vào lúc 6 giờ sáng hàng ngày
# schedule.every().day.at("18:14").do(job)

# while True:
#     print(time.strftime('%Y-%m-%d %H:%M:%S'))
#     schedule.run_pending()
#     time.sleep(60)  # Chờ 1 phút trước khi kiểm tra lại
# job()

if __name__ == "__main__":
    # data = down_data_super_app()
    # print(data)
    match_product_ID()