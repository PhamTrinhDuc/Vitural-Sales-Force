# Sử dụng image cơ bản của Python 3.11 slim
FROM python:3.11-slim

# Thiết lập thư mục làm việc
WORKDIR /src

# Copy file phụ thuộc
COPY requirements.txt .

# Cài đặt thư viện
RUN pip install --no-cache-dir -r requirements.txt

# Copy mã nguồn ứng dụng
COPY . .

# Expose cổng mà ứng dụng sử dụng
EXPOSE 8000

# Lệnh chạy ứng dụng
CMD ["uvicorn", "app_api:app", "--host", "0.0.0.0", "--port", "8000"]
