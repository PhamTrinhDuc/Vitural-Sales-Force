import os
import pandas as pd
import logging
from unidecode import unidecode
from typing import Literal, Optional
from configs.config_system import LoadConfig

class DataMerger:
    def __init__(self, 
                 origin_data_path: Optional[str], 
                 new_data_path: Optional[str], 
                 output_file_path: Optional[str]):
        
        self.origin_df = pd.read_excel(origin_data_path)
        self.new_df = pd.read_excel(new_data_path)
        self.output_file_path = output_file_path

    def mergering(self) -> pd.DataFrame:
        try:
            # Thực hiện phép merge để thêm group_product_name và group_name từ file 1 vào file 2
            df_merged = pd.merge(self.new_df, self.origin_df[['product_code', 'group_product_name', 'group_name', 'specification']],
                                left_on='productCode', right_on='product_code', how='left')

            # Cập nhật cột specifications từ file 1 vào file 2
            df_merged['specifications'] = df_merged['specification'].combine_first(df_merged['specifications'])

            # Chọn lại các cột cần thiết
            df_final = df_merged[['productId', 'productCode', 'productGroupId','group_product_name', 'productName', 'shortDescription',
                                'imgList', 'productDescription', 'specifications', 'soldQuantity', 'price',
                                'power', 'weight', 'volume']]


            # Đổi tên cột cho rõ ràng nếu cần
            df_final.rename(columns={'group_product_name': 'groupProductName'}, inplace=True)
            df_final.rename(columns={
                'productId': 'product_info_id',
                'productGroupId': 'group_product_id',
                'groupProductName': 'group_product_name',
                'productCode': 'product_code',
                'productName': 'product_name',
                'shortDescription': 'short_description',
                'imgList': 'file_path',
                'productDescription': 'product_info',
                # 'specifications': 'specification',
                'soldQuantity': 'sold_quantity',
                'price': 'lifecare_price',
            }, inplace=True)
            # Đảm bảo group_product_name được điền giống nhau cho các hàng có cùng group_product_id
            df_final['group_product_name'] = df_final.groupby('group_product_id')['group_product_name'].transform('first')
            # Tạo cột group_name bằng cách cộng group_product_name và product_name
            df_final['group_name'] = df_final['group_product_name'] + ' ' + df_final['product_name']
            df_final.to_excel(self.output_file_path, index=False)
            logging.info(f"Successfully merged data to {self.output_file_path}")
            return df_final
        except Exception as e:
            logging.error(f"Error when merging data: {e}")

    @staticmethod
    def group_data( 
            member_code: str, 
            df: pd.DataFrame,
            folder_data_csv: str = LoadConfig.SPECIFIC_PRODUCT_FOLDER_CSV_STORAGE):
        try:
            for group_name, group_data in df.groupby('group_product_name'):
                # Xóa dấu và thay thế bằng dấu gạch dưới
                sanitized_group_name = ''.join(e for e in group_name if e.isalnum() or e.isspace()).replace(' ', '_')
                csv_file_path = os.path.join(folder_data_csv.format(member_code=member_code), f"{unidecode(sanitized_group_name)}.csv")
                group_data.to_csv(csv_file_path, index=False)
            logging.info("Successfully grouped data.")
        except Exception as e:
            logging.error(f"Error when grouping data: {e}")