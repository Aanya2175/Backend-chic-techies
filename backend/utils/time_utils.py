
def duration_seconds(start: int, end: int) -> int:
    try:
        return max(0, int(end) - int(start))
    except:
        return 0
