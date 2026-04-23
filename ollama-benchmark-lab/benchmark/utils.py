import time


def now():
    return time.time()


def safe_div(a, b):
    return a / b if b else 0.0