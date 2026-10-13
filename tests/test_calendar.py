from datetime import date

import pytest

from daily_leet.calendar import is_working_day


@pytest.mark.parametrize(
    ("day", "expected"),
    [
        (date(2026, 10, 19), True),   # Monday
        (date(2026, 10, 13), True),   # Tuesday
        (date(2026, 10, 16), True),   # Friday
        (date(2026, 10, 10), False),  # Saturday
        (date(2026, 10, 11), False),  # Sunday
        (date(2026, 1, 1), False),    # New Year's Day (US)
        (date(2026, 11, 26), False),  # Thanksgiving (US)
    ],
)
def test_is_working_day(day, expected):
    assert is_working_day(day, "US") is expected
