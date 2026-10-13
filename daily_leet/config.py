from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import time

import holidays

REQUIRED_VARS = ("DB_URL", "BOT_ID", "CHAT_ID", "SEND_AT", "COUNTRY")


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class Config:
    db_url: str
    bot_id: str
    chat_id: str
    send_at: time
    country: str

    @classmethod
    def from_env(cls, environ: dict[str, str] | None = None) -> Config:
        env = os.environ if environ is None else environ
        missing = [name for name in REQUIRED_VARS if not env.get(name)]
        if missing:
            raise ConfigError(f"Missing environment variables: {', '.join(missing)}")
        return cls(
            db_url=env["DB_URL"],
            bot_id=env["BOT_ID"],
            chat_id=env["CHAT_ID"],
            send_at=_parse_send_at(env["SEND_AT"]),
            country=_parse_country(env["COUNTRY"]),
        )


def _parse_send_at(value: str) -> time:
    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = time.fromisoformat(normalized)
    except ValueError as exc:
        raise ConfigError(
            "SEND_AT must be an ISO 8601 time with a timezone "
            "(e.g. 09:00:00+05:00 or 09:00:00Z)"
        ) from exc
    if parsed.tzinfo is None:
        raise ConfigError(
            "SEND_AT must be an ISO 8601 time with a timezone "
            "(e.g. 09:00:00+05:00 or 09:00:00Z)"
        )
    return parsed


def _parse_country(value: str) -> str:
    code = value.strip().upper()
    try:
        holidays.country_holidays(code, years=2026)
    except NotImplementedError as exc:
        raise ConfigError(
            f"COUNTRY is not supported by the holidays library: {code}"
        ) from exc
    return code
