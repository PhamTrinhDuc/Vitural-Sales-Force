import time
import schedule
from configs.config_system import SYSTEM_CONFIG
from source.data_processor.run import DataProcessingPipeline

pipeline = DataProcessingPipeline()
# Lập lịch để chạy công việc vào lúc 6 giờ sáng hàng ngày
schedule.every().day.at("18:14").do(pipeline.processing())
while True:
    print(time.strftime('%Y-%m-%d %H:%M:%S'))
    schedule.run_pending()
    time.sleep(60)  # Chờ 1 phút trước khi kiểm tra lại
