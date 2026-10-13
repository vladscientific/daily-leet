from datetime import time, timedelta, timezone

from daily_leet.cron import crontab_body, utc_cron_fields


def test_utc_cron_fields_from_offset():
    send_at = time(9, 0, 0, tzinfo=timezone(timedelta(hours=5)))
    assert utc_cron_fields(send_at) == (0, 4)


def test_crontab_body_includes_env_and_send_command():
    send_at = time(9, 0, 0, tzinfo=timezone(timedelta(hours=5)))
    body = crontab_body(
        send_at,
        {
            "DB_URL": "postgresql://u:p@h/db",
            "BOT_ID": "1:abc",
            "CHAT_ID": "-1",
            "SEND_AT": "09:00:00+05:00",
            "COUNTRY": "US",
        },
    )
    assert "0 4 * * * root " in body
    assert "python -m daily_leet send" in body
    assert "COUNTRY=US" in body
    assert "SEND_AT=09:00:00+05:00" in body
