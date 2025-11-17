"""Normalize human-readable dates into ISO-8601 strings."""
from datetime import datetime
from typing import List, Tuple

DATE_FORMATS: List[str] = [
    '%Y-%m-%d',
    '%m/%d/%Y',
    '%Y/%m/%d',
    '%d-%m-%Y',
    '%d/%m/%Y',
    '%b %d, %Y',
    '%B %d, %Y',
    '%Y.%m.%d',
]


def normalize_date(value: str) -> Tuple[str, bool]:
    """Return a tuple (normalized, changed) after coercing to YYYY-MM-DD."""
    candidate = value.strip()
    try:
        datetime.strptime(candidate, '%Y-%m-%d')
        return candidate, False
    except ValueError:
        pass

    for fmt in DATE_FORMATS[1:]:
        try:
            dt = datetime.strptime(candidate, fmt)
            return dt.strftime('%Y-%m-%d'), True
        except ValueError:
            continue

    return candidate, False
