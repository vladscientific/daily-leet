from datetime import time, timedelta, timezone

import pytest

from daily_leet.config import Config, ConfigError, REQUIRED_VARS

VALID_ENV = {
    "DB_URL": "postgresql://u:p@h/db",
    "BOT_ID": "1:abc",
    "CHAT_ID": "-1",
    "SEND_AT": "09:00:00+05:00",
    "COUNTRY": "US",
}


def test_from_env_reads_required_vars():
    config = Config.from_env(VALID_ENV)
    assert config.db_url == VALID_ENV["DB_URL"]
    assert config.bot_id == VALID_ENV["BOT_ID"]
    assert config.chat_id == VALID_ENV["CHAT_ID"]
    assert config.send_at == time(9, 0, 0, tzinfo=timezone(timedelta(hours=5)))
    assert config.country == "US"


def test_from_env_normalizes_country():
    assert Config.from_env({**VALID_ENV, "COUNTRY": "us"}).country == "US"


def test_from_env_rejects_unknown_country():
    with pytest.raises(ConfigError, match="COUNTRY"):
        Config.from_env({**VALID_ENV, "COUNTRY": "ZZ"})


def test_from_env_rejects_invalid_send_at():
    with pytest.raises(ConfigError, match="SEND_AT"):
        Config.from_env({**VALID_ENV, "SEND_AT": "nine"})


def test_from_env_rejects_send_at_without_timezone():
    with pytest.raises(ConfigError, match="timezone"):
        Config.from_env({**VALID_ENV, "SEND_AT": "09:00:00"})


def test_from_env_accepts_send_at_zulu():
    assert Config.from_env({**VALID_ENV, "SEND_AT": "09:00:00Z"}).send_at == time(
        9, 0, 0, tzinfo=timezone.utc
    )


@pytest.mark.parametrize("missing", REQUIRED_VARS)
def test_from_env_requires_each_var(missing):
    env = dict(VALID_ENV)
    del env[missing]
    with pytest.raises(ConfigError, match=missing):
        Config.from_env(env)
