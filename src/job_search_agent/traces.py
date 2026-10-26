"""Local trace in SQLite (`data/local/traces.db`): tables `turns` and `steps`.

Every text that enters the trace (the user's text, step arguments and results) is masked with
`masking.mask` and the names of the configuration. Nothing leaves the machine; the trace is opened
in the app or with any SQLite client.
"""

import json
import sqlite3
from collections.abc import Iterator
from contextlib import closing, contextmanager
from datetime import date, datetime
from pathlib import Path
from typing import Any

from job_search_agent.costs import Usage
from job_search_agent.masking import mask

TURN_STATUSES = ("answered", "awaiting_approval", "declined", "budget_exceeded", "error")
STEP_KINDS = ("model", "tool", "approval")
STEP_ORIGINS = ("chat", "dashboard")
MAX_SUMMARY = 500  # characters kept of step arguments and results
NO_USAGE = Usage()

SCHEMA = """
CREATE TABLE IF NOT EXISTS turns (
    id INTEGER PRIMARY KEY,
    thread_id TEXT NOT NULL,
    started_at TEXT NOT NULL,
    user_text TEXT NOT NULL,
    origin TEXT,
    reference_date TEXT,
    route TEXT,
    agent TEXT,
    status TEXT,
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    cached_tokens INTEGER NOT NULL DEFAULT 0,
    cost_usd REAL NOT NULL DEFAULT 0,
    over_turn_limit INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS steps (
    turn_id INTEGER NOT NULL REFERENCES turns(id),
    seq INTEGER NOT NULL,
    kind TEXT NOT NULL,
    name TEXT NOT NULL,
    origin TEXT NOT NULL,
    args TEXT,
    result TEXT,
    tokens INTEGER NOT NULL DEFAULT 0,
    cost_usd REAL NOT NULL DEFAULT 0,
    duration_ms INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (turn_id, seq)
);
"""


def summarize(value: Any, names: tuple[str, ...]) -> str | None:
    """JSON of `value` (text stays as is), masked and cut to MAX_SUMMARY characters."""
    if value is None:
        return None
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, default=str)
    text = mask(text, names)
    return text if len(text) <= MAX_SUMMARY else text[: MAX_SUMMARY - 3] + "..."


class TraceStore:
    def __init__(self, path: Path, names: tuple[str, ...] = ()) -> None:
        self.path = Path(path)
        self.names = tuple(names)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(SCHEMA)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        with closing(sqlite3.connect(self.path)) as connection:
            connection.row_factory = sqlite3.Row
            with connection:  # commit, or rollback on error
                yield connection

    def start_turn(
        self,
        thread_id: str,
        user_text: str,
        origin: str | None = None,
        reference_date: date | None = None,
        started_at: datetime | None = None,
    ) -> int:
        """Open a turn (local time) and return its id."""
        started_at = started_at or datetime.now().astimezone()
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO turns (thread_id, started_at, user_text, origin, reference_date)"
                " VALUES (?, ?, ?, ?, ?)",
                (
                    thread_id,
                    started_at.isoformat(timespec="seconds"),
                    mask(user_text, self.names),
                    origin,
                    reference_date.isoformat() if reference_date else None,
                ),
            )
            return cursor.lastrowid

    def add_step(
        self,
        turn_id: int,
        kind: str,
        name: str,
        origin: str = "chat",
        args: Any = None,
        result: Any = None,
        tokens: int = 0,
        cost_usd: float = 0.0,
        duration_ms: int = 0,
    ) -> int:
        """Append a step to the turn and return its `seq`. An approval decision is
        `kind="approval"`, `name` the proposed tool and `args` with proposal_id, decision and
        result code."""
        if kind not in STEP_KINDS:
            raise ValueError(f"Unknown step kind {kind!r}; use one of {STEP_KINDS}")
        if origin not in STEP_ORIGINS:
            raise ValueError(f"Unknown step origin {origin!r}; use one of {STEP_ORIGINS}")
        with self._connect() as connection:
            seq = connection.execute(
                "SELECT COALESCE(MAX(seq), 0) + 1 FROM steps WHERE turn_id = ?", (turn_id,)
            ).fetchone()[0]
            connection.execute(
                "INSERT INTO steps VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    turn_id,
                    seq,
                    kind,
                    name,
                    origin,
                    summarize(args, self.names),
                    summarize(result, self.names),
                    tokens,
                    cost_usd,
                    duration_ms,
                ),
            )
            return seq

    def finish_turn(
        self,
        turn_id: int,
        status: str,
        usage: Usage = NO_USAGE,
        cost_usd: float = 0.0,
        route: str | None = None,
        agent: str | None = None,
        over_turn_limit: bool = False,
    ) -> None:
        if status not in TURN_STATUSES:
            raise ValueError(f"Unknown turn status {status!r}; use one of {TURN_STATUSES}")
        with self._connect() as connection:
            connection.execute(
                "UPDATE turns SET status = ?, route = ?, agent = ?, input_tokens = ?,"
                " output_tokens = ?, cached_tokens = ?, cost_usd = ?, over_turn_limit = ?"
                " WHERE id = ?",
                (
                    status,
                    route,
                    agent,
                    usage.input_tokens,
                    usage.output_tokens,
                    usage.cached_tokens,
                    cost_usd,
                    int(over_turn_limit),
                    turn_id,
                ),
            )

    def turn(self, turn_id: int) -> dict | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM turns WHERE id = ?", (turn_id,)).fetchone()
        return dict(row) if row else None

    def steps(self, turn_id: int) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM steps WHERE turn_id = ? ORDER BY seq", (turn_id,)
            ).fetchall()
        return [dict(row) for row in rows]

    def tokens_on(self, day: date) -> int:
        """Tokens (input + output) of the turns started on `day` (local date)."""
        with self._connect() as connection:
            return connection.execute(
                "SELECT COALESCE(SUM(input_tokens + output_tokens), 0) FROM turns"
                " WHERE substr(started_at, 1, 10) = ?",
                (day.isoformat(),),
            ).fetchone()[0]

    def cost_by_day(self, start: date, end: date) -> list[tuple[str, float]]:
        """(day, cost in US$) of each day with turns between `start` and `end`, for the
        dashboard."""
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT substr(started_at, 1, 10) AS day, SUM(cost_usd) FROM turns"
                " WHERE day BETWEEN ? AND ? GROUP BY day ORDER BY day",
                (start.isoformat(), end.isoformat()),
            ).fetchall()
        return [(row[0], row[1]) for row in rows]
