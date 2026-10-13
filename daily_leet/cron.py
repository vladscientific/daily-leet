from __future__ import annotations

import os
from datetime import date, datetime, time, timezone
from pathlib import Path

from daily_leet.config import REQUIRED_VARS

SEND_COMMAND = "cd /app && PYTHONPATH=/app /usr/local/bin/python -m daily_leet send"
CRON_ENV_VARS = (*REQUIRED_VARS, "PYTHONPATH")


def utc_cron_fields(send_at: time) -> tuple[int, int]:
    """Minute and hour in UTC for a daily crontab at `send_at`."""
    if send_at.tzinfo is None:
        raise ValueError("SEND_AT must include a timezone offset")
    local = datetime.combine(date(2026, 6, 15), send_at)
    utc = local.astimezone(timezone.utc)
    return utc.minute, utc.hour


def crontab_body(send_at: time, environ: dict[str, str] | None = None) -> str:
    env = os.environ if environ is None else environ
    minute, hour = utc_cron_fields(send_at)
    lines = [
        "SHELL=/bin/sh",
        "PATH=/usr/local/bin:/usr/bin:/bin",
    ]
    for name in CRON_ENV_VARS:
        value = env.get(name)
        if value:
            lines.append(f"{name}={value}")
    lines.append(f"{minute} {hour} * * * root {SEND_COMMAND}")
    lines.append("")
    return "\n".join(lines)


def write_crontab(path: str | Path, send_at: time, environ: dict[str, str] | None = None) -> None:
    Path(path).write_text(crontab_body(send_at, environ), encoding="utf-8")
