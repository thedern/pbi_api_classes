import time
from functools import wraps

def timethis(func):
    """
    decorator to time a function

    Args:
        func (_type_): function to be timed
    """
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result =  func(*args, **kwargs)
        end = time.time()
        print(func.__name__, end-start)
        return result
    return wrapper
