import math
def safe_div(a, b):
    try:
        return a / b
    except (ZeroDivisionError, TypeError, ValueError):
        return 0.0

