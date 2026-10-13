from __future__ import annotations

import psycopg

from daily_leet.models import Problem, ProblemStats

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS problems (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL UNIQUE,
    sent_at TIMESTAMPTZ
)
"""

CREATE_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS problems_unsent_idx ON problems (id) WHERE sent_at IS NULL
"""

NEXT_UNSENT_SQL = """
SELECT id, url
FROM problems
WHERE sent_at IS NULL
ORDER BY id
LIMIT 1
"""

CLAIM_SQL = NEXT_UNSENT_SQL + "\nFOR UPDATE SKIP LOCKED"

MARK_SENT_SQL = "UPDATE problems SET sent_at = NOW() WHERE id = %s"

STATS_SQL = """
SELECT COUNT(*), COUNT(*) FILTER (WHERE sent_at IS NULL)
FROM problems
"""


def connect(db_url: str) -> psycopg.Connection:
    return psycopg.connect(db_url)


def ensure_schema(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute(CREATE_TABLE_SQL)
        cur.execute(CREATE_INDEX_SQL)
    conn.commit()


def _problem_from_row(row) -> Problem | None:
    if row is None:
        return None
    return Problem(id=row[0], url=row[1])


def peek_next(conn: psycopg.Connection) -> Problem | None:
    with conn.cursor() as cur:
        cur.execute(NEXT_UNSENT_SQL)
        return _problem_from_row(cur.fetchone())


def claim_next(conn: psycopg.Connection) -> Problem | None:
    with conn.cursor() as cur:
        cur.execute(CLAIM_SQL)
        return _problem_from_row(cur.fetchone())


def mark_sent(conn: psycopg.Connection, problem_id: int) -> None:
    with conn.cursor() as cur:
        cur.execute(MARK_SENT_SQL, (problem_id,))


def problem_stats(conn: psycopg.Connection) -> ProblemStats:
    with conn.cursor() as cur:
        cur.execute(STATS_SQL)
        total, unsent = cur.fetchone()
    return ProblemStats(total=total, unsent=unsent)
