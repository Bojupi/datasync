import time
from functools import wraps


def retry(max_retries: int = 3):
    """在函数抛出异常的情况下，（等待后）重试`max_retries`次"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Retrying {func.__name__} due to {str(e)}")
                    time.sleep(5 * _)
            raise RuntimeError(f"Failed after {max_retries} retries")
        return wrapper
    return decorator
