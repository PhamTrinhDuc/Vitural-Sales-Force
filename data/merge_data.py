import pandas as pd

# Đọc dữ liệu từ file 1 và file 2
file1_path = '/home/aiai01/Production/Chatbot_Proactive_mainv1/Main/data/data_private/product_final_300_extract.xlsx'  # Thay đổi đường dẫn đến file 1
file2_path = '/home/aiai01/Production/Chatbot_Proactive_mainv1/Main/data/data_private/product_info_superapp.xlsx'  # Thay đổi đường dẫn đến file 2

# Giả sử file 1 và file 2 là file CSV. Nếu là file Excel, sử dụng pd.read_excel
df1 = pd.read_excel(file1_path)
df2 = pd.read_excel(file2_path)

# Kiểm tra thông tin của các DataFrame
print("File 1 DataFrame:")
print(df1.head())
print("File 2 DataFrame:")
print(df2.head())

# Thực hiện phép merge để thêm group_product_name và group_name từ file 1 vào file 2
df_merged = pd.merge(df2, df1[['product_code', 'group_product_name', 'group_name', 'specification']],
                     left_on='productCode', right_on='product_code', how='left')

# Cập nhật cột specifications từ file 1 vào file 2
df_merged['specifications'] = df_merged['specification'].combine_first(df_merged['specifications'])

print(df_merged.columns)

# Chọn lại các cột cần thiết
df_final = df_merged[['productId', 'productCode', 'productGroupId','group_product_name', 'productName', 'shortDescription',
                      'imgList', 'productDescription', 'specifications', 'price',
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
    'specifications': 'specification',
    'price': 'lifecare_price',
}, inplace=True)
print(df_final.columns)
# Đảm bảo group_product_name được điền giống nhau cho các hàng có cùng group_product_id
df_final['group_product_name'] = df_final.groupby('group_product_id')['group_product_name'].transform('first')

# Tạo cột group_name bằng cách cộng group_product_name và product_name
df_final['group_name'] = df_final['group_product_name'] + ' ' + df_final['product_name']

# Lưu dữ liệu đã đồng bộ vào file Excel hoặc CSV
output_file_path = 'data/data_private/data_final_superapp.xlsx'  # Đường dẫn đến file kết quả
df_final.to_excel(output_file_path, index=False)
print(f"Dữ liệu đã được lưu vào {output_file_path}")
# Lưu các file CSV theo từng group_product_name
import os
from unidecode import unidecode
for group_name, group_data in df_final.groupby('group_product_name'):
    # Xóa dấu và thay thế bằng dấu gạch dưới
    sanitized_group_name = ''.join(e for e in group_name if e.isalnum() or e.isspace()).replace(' ', '_')
    csv_file_path = os.path.join('data/data_private/data_detail_superapp/', f"{unidecode(sanitized_group_name)}.csv")
    group_data.to_csv(csv_file_path, index=False)
    print(f"Dữ liệu của nhóm '{group_name}' đã được lưu vào {csv_file_path}")

