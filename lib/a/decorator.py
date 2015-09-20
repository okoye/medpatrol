'''
Simple decorator functions
'''
import time

def infinite(func):
    def wrapper(**kwargs):
        oldstate = None
        while True:
            state = func(oldstate, **kwargs)
            oldstate = state
            time.sleep(2)
    return wrapper
