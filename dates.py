from datetime import datetime


def get_next_month(year: int, month: int):
    if month == 12:
        return year + 1, 1
    return year, month + 1


# Gets list of (year, month) tuples from start to end date
# e.g. [(2025, 9), (2025, 10), (2025, 11), (2025, 12), ...]
def get_month_ranges_between(start: datetime, end: datetime):
    months: list[tuple[int, int]] = []
    current = datetime(start.year, start.month, 1)

    while current <= end:
        months.append((current.year, current.month))

        if current.month == 12:
            current = datetime(current.year + 1, 1, 1)
        else:
            current = datetime(current.year, current.month + 1, 1)

    return months
