from __future__ import annotations

from datetime import time

from daily_leet.models import ProblemStats

NO_MORE_PROBLEMS = "No more problems left to send."


def startup_message(
    *,
    send_at: time,
    country: str,
    db_ok: bool,
    stats: ProblemStats | None = None,
    next_url: str | None = None,
    db_error: str | None = None,
) -> str:
    lines = [
        "daily-leet started",
        "",
        "params:",
        f"  SEND_AT: {send_at.isoformat()}",
        f"  COUNTRY: {country} (holidays library)",
    ]
    if db_ok and stats is not None:
        lines.extend(
            [
                "DB connection: ok",
                f"problems: {stats.total}",
                f"unsent: {stats.unsent}",
                f"next: {next_url or 'none'}",
            ]
        )
    else:
        detail = db_error or "unknown error"
        lines.extend(
            [
                f"DB connection: failed ({detail})",
                "problems: n/a",
                "unsent: n/a",
            ]
        )
    return "\n".join(lines)
