from __future__ import annotations

import logging
import sys
from collections.abc import Callable
from datetime import datetime

from daily_leet.calendar import is_working_day, now_for_send_at
from daily_leet.config import Config, ConfigError
from daily_leet.cron import write_crontab
from daily_leet.db import (
    claim_next,
    connect,
    ensure_schema,
    mark_sent,
    peek_next,
    problem_stats,
)
from daily_leet.messages import NO_MORE_PROBLEMS, startup_message
from daily_leet.telegram import send_message

log = logging.getLogger(__name__)

SendFn = Callable[[str, str, str], None]
ConnectFn = Callable[[str], object]


def startup(
    config: Config,
    *,
    send: SendFn = send_message,
    connect_db: ConnectFn = connect,
) -> int:
    db_ok = False
    stats = None
    next_url = None
    db_error = None
    try:
        with connect_db(config.db_url) as conn:
            ensure_schema(conn)
            stats = problem_stats(conn)
            nxt = peek_next(conn)
            next_url = None if nxt is None else nxt.url
        db_ok = True
    except Exception as exc:
        db_error = str(exc)
        log.exception("db_unavailable")

    send(
        config.bot_id,
        config.chat_id,
        startup_message(
            send_at=config.send_at,
            country=config.country,
            db_ok=db_ok,
            stats=stats,
            next_url=next_url,
            db_error=db_error,
        ),
    )
    return 0 if db_ok else 1


def send_daily(
    config: Config,
    *,
    now: datetime | None = None,
    send: SendFn = send_message,
    connect_db: ConnectFn = connect,
) -> int:
    moment = now if now is not None else now_for_send_at(config.send_at)
    if not is_working_day(moment.date(), config.country):
        log.info("skip_non_working_day date=%s country=%s", moment.date(), config.country)
        return 0

    with connect_db(config.db_url) as conn:
        ensure_schema(conn)
        problem = claim_next(conn)
        if problem is None:
            conn.rollback()
            send(config.bot_id, config.chat_id, NO_MORE_PROBLEMS)
            log.info("empty_queue")
            return 0
        try:
            send(config.bot_id, config.chat_id, problem.url)
        except Exception:
            conn.rollback()
            log.exception("send_failed id=%s", problem.id)
            raise
        mark_sent(conn, problem.id)
        conn.commit()
        log.info("sent id=%s url=%s", problem.id, problem.url)
    return 0


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )


def _load_config() -> Config | None:
    try:
        return Config.from_env()
    except ConfigError as exc:
        log.error("%s", exc)
        return None


def main(argv: list[str] | None = None) -> int:
    _configure_logging()
    args = list(sys.argv[1:] if argv is None else argv)
    command = args[0] if args else "startup"

    if command not in {"startup", "send", "write-crontab"}:
        log.error("Unknown command %s (use startup, send, or write-crontab)", command)
        return 2

    config = _load_config()
    if config is None:
        return 1

    if command == "startup":
        return startup(config)
    if command == "send":
        return send_daily(config)

    path = args[1] if len(args) > 1 else "/etc/cron.d/daily-leet"
    write_crontab(path, config.send_at)
    log.info("wrote_crontab path=%s", path)
    return 0
