import time
import functools
from logs.logger import set_logging_time

logger = set_logging_time()

def timing_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Hàm {str(func.__name__).upper()} thực thi trong {execution_time:.4f} giây")
        return result
    return wrapper
