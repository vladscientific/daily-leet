from datetime import date, datetime, time
from functools import lru_cache

import holidays


def now_for_send_at(send_at: time) -> datetime:
    if send_at.tzinfo is None:
        raise ValueError("SEND_AT must include a timezone offset")
    return datetime.now(send_at.tzinfo)


@lru_cache(maxsize=16)
def _public_holidays(country: str, year: int):
    return holidays.country_holidays(country, years=year)


def is_working_day(day: date, country: str) -> bool:
    """Weekends and public holidays for `country` are non-working days."""
    if day.weekday() >= 5:
        return False
    return day not in _public_holidays(country, day.year)
