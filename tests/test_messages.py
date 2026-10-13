from datetime import time, timezone

from daily_leet.messages import startup_message
from daily_leet.models import ProblemStats


def test_startup_message_ok():
    text = startup_message(
        send_at=time(9, 0, 0, tzinfo=timezone.utc),
        country="US",
        db_ok=True,
        stats=ProblemStats(total=3, unsent=2),
        next_url="https://leetcode.com/problems/jewels-and-stones/",
    )
    assert text.startswith("daily-leet started")
    assert "SEND_AT: 09:00:00+00:00" in text
    assert "COUNTRY: US (holidays library)" in text
    assert "DB connection: ok" in text
    assert "problems: 3" in text
    assert "unsent: 2" in text
    assert "next: https://leetcode.com/problems/jewels-and-stones/" in text


def test_startup_message_db_failed():
    text = startup_message(
        send_at=time(9, 0, 0, tzinfo=timezone.utc),
        country="KZ",
        db_ok=False,
        db_error="timeout",
    )
    assert "COUNTRY: KZ (holidays library)" in text
    assert "DB connection: failed (timeout)" in text
    assert "problems: n/a" in text
    assert "next:" not in text


def test_startup_message_no_next_problem():
    text = startup_message(
        send_at=time(9, 0, 0, tzinfo=timezone.utc),
        country="US",
        db_ok=True,
        stats=ProblemStats(total=3, unsent=0),
        next_url=None,
    )
    assert "next: none" in text
