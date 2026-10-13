from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from daily_leet.config import ConfigError
from daily_leet.main import main, send_daily, startup
from daily_leet.messages import NO_MORE_PROBLEMS
from daily_leet.models import Problem, ProblemStats
from daily_leet.telegram import TelegramError


class FakeConn:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


@pytest.fixture
def conn():
    fake = FakeConn()
    fake.committed = False
    fake.rolled_back = False
    return fake


def test_startup_sends_params_and_db_stats(monkeypatch, config, conn):
    monkeypatch.setattr("daily_leet.main.ensure_schema", lambda c: None)
    monkeypatch.setattr(
        "daily_leet.main.problem_stats",
        lambda c: ProblemStats(total=12, unsent=5),
    )
    monkeypatch.setattr(
        "daily_leet.main.peek_next",
        lambda c: Problem(id=1, url="https://leetcode.com/problems/jewels-and-stones/"),
    )
    send = Mock()
    connect_db = Mock(return_value=conn)

    code = startup(config, send=send, connect_db=connect_db)

    assert code == 0
    text = send.call_args.args[2]
    assert "daily-leet started" in text
    assert "SEND_AT: 09:00:00+00:00" in text
    assert "COUNTRY: US (holidays library)" in text
    assert "DB connection: ok" in text
    assert "problems: 12" in text
    assert "unsent: 5" in text
    assert "next: https://leetcode.com/problems/jewels-and-stones/" in text


def test_startup_reports_db_failure(config, conn):
    send = Mock()
    connect_db = Mock(side_effect=RuntimeError("could not connect"))

    code = startup(config, send=send, connect_db=connect_db)

    assert code == 1
    text = send.call_args.args[2]
    assert "DB connection: failed" in text
    assert "could not connect" in text


def test_skips_non_working_day(config, conn):
    send = Mock()
    connect_db = Mock(return_value=conn)
    code = send_daily(
        config,
        now=datetime(2026, 10, 10, 12, 0, 0, tzinfo=timezone.utc),
        send=send,
        connect_db=connect_db,
    )
    assert code == 0
    connect_db.assert_not_called()
    send.assert_not_called()


def test_empty_queue_notifies_telegram(monkeypatch, config, conn):
    monkeypatch.setattr("daily_leet.main.ensure_schema", lambda c: None)
    monkeypatch.setattr("daily_leet.main.claim_next", lambda c: None)
    send = Mock()
    connect_db = Mock(return_value=conn)

    code = send_daily(
        config,
        now=datetime(2026, 10, 13, 9, 0, 0, tzinfo=timezone.utc),
        send=send,
        connect_db=connect_db,
    )

    assert code == 0
    send.assert_called_once_with("123:token", "-1001", NO_MORE_PROBLEMS)
    assert conn.rolled_back is True
    assert conn.committed is False


def test_sends_and_marks_claimed_problem(monkeypatch, config, conn):
    problem = Problem(id=3, url="https://leetcode.com/problems/two-sum/")
    monkeypatch.setattr("daily_leet.main.ensure_schema", lambda c: None)
    monkeypatch.setattr("daily_leet.main.claim_next", lambda c: problem)
    mark = Mock()
    monkeypatch.setattr("daily_leet.main.mark_sent", mark)
    send = Mock()
    connect_db = Mock(return_value=conn)

    code = send_daily(
        config,
        now=datetime(2026, 10, 13, 9, 0, 0, tzinfo=timezone.utc),
        send=send,
        connect_db=connect_db,
    )

    assert code == 0
    send.assert_called_once_with("123:token", "-1001", problem.url)
    mark.assert_called_once_with(conn, 3)
    assert conn.committed is True


def test_rollback_when_send_fails(monkeypatch, config, conn):
    problem = Problem(id=3, url="https://leetcode.com/problems/two-sum/")
    monkeypatch.setattr("daily_leet.main.ensure_schema", lambda c: None)
    monkeypatch.setattr("daily_leet.main.claim_next", lambda c: problem)
    mark = Mock()
    monkeypatch.setattr("daily_leet.main.mark_sent", mark)
    send = Mock(side_effect=TelegramError("boom"))
    connect_db = Mock(return_value=conn)

    with pytest.raises(TelegramError):
        send_daily(
            config,
            now=datetime(2026, 10, 13, 9, 0, 0, tzinfo=timezone.utc),
            send=send,
            connect_db=connect_db,
        )

    mark.assert_not_called()
    assert conn.rolled_back is True
    assert conn.committed is False


def test_skips_public_holiday(config, conn):
    send = Mock()
    connect_db = Mock(return_value=conn)
    code = send_daily(
        config,
        now=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        send=send,
        connect_db=connect_db,
    )
    assert code == 0
    connect_db.assert_not_called()
    send.assert_not_called()


def test_main_exits_when_env_missing(monkeypatch):
    monkeypatch.setattr(
        "daily_leet.main.Config.from_env",
        Mock(side_effect=ConfigError("Missing environment variables: DB_URL")),
    )
    assert main([]) == 1


def test_main_rejects_unknown_command(monkeypatch, config):
    monkeypatch.setattr("daily_leet.main.Config.from_env", Mock(return_value=config))
    assert main(["nope"]) == 2
