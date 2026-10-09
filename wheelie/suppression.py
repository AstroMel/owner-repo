"""Suppression list: everyone who has asked us to stop.

Backed by SQLite so opt-outs survive restarts. Entries are append-only: there
is deliberately no delete. Adding an address that is already suppressed is a
no-op, so reprocessing the same mail is safe.

Compliance clocks recorded per entry (confirm with a lawyer before launch):
  - email (CAN-SPAM): honor within 10 business days
  - text/SMS (Florida): stop within 15 days
We aim to suppress the same day; the deadline is a backstop, not the target.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from email.utils import parseaddr
from pathlib import Path

from .models import Classification, Email

EMAIL_BUSINESS_DAYS = 10
TEXT_CALENDAR_DAYS = 15

_SCHEMA = """
CREATE TABLE IF NOT EXISTS suppressed (
    address     TEXT NOT NULL,
    channel     TEXT NOT NULL,
    reason      TEXT NOT NULL,
    source      TEXT NOT NULL DEFAULT '',
    logged_at   TEXT NOT NULL,
    honor_by    TEXT NOT NULL,
    PRIMARY KEY (address, channel)
)
"""


def normalize_address(value: str) -> str:
    """'Jo <Jo@Example.com>' -> 'jo@example.com'. Returns '' if no usable address."""
    addr = parseaddr(value)[1].strip().lower()
    return addr if addr.count("@") == 1 and not addr.startswith("@") and not addr.endswith("@") else ""


def add_business_days(start: date, days: int) -> date:
    current = start
    while days > 0:
        current += timedelta(days=1)
        if current.weekday() < 5:  # Mon-Fri; federal holidays ignored, which only errs early
            days -= 1
    return current


def honor_by(channel: str, logged: date) -> date:
    if channel == "text":
        return logged + timedelta(days=TEXT_CALENDAR_DAYS)
    return add_business_days(logged, EMAIL_BUSINESS_DAYS)


@dataclass(frozen=True)
class Entry:
    address: str
    channel: str
    reason: str
    source: str
    logged_at: datetime
    honor_by: date


class SuppressionList:
    def __init__(self, path: str | Path = ":memory:"):
        self._db = sqlite3.connect(str(path))
        self._db.execute(_SCHEMA)
        self._db.commit()

    def close(self) -> None:
        self._db.close()

    def add(
        self,
        address: str,
        *,
        channel: str = "email",
        reason: str = "opt-out request",
        source: str = "",
        now: datetime | None = None,
    ) -> bool:
        """Suppress an address. Returns True if newly added, False if already present."""
        addr = normalize_address(address)
        if not addr:
            raise ValueError(f"not a valid address: {address!r}")
        if channel not in {"email", "text"}:
            raise ValueError(f"unknown channel: {channel!r}")
        now = now or datetime.now(timezone.utc)
        cur = self._db.execute(
            "INSERT OR IGNORE INTO suppressed VALUES (?, ?, ?, ?, ?, ?)",
            (addr, channel, reason, source, now.isoformat(), honor_by(channel, now.date()).isoformat()),
        )
        self._db.commit()
        return cur.rowcount == 1

    def is_suppressed(self, address: str, channel: str = "email") -> bool:
        addr = normalize_address(address)
        if not addr:
            return True  # fail closed: never contact something we can't identify
        row = self._db.execute(
            "SELECT 1 FROM suppressed WHERE address = ? AND channel = ?", (addr, channel)
        ).fetchone()
        return row is not None

    def can_contact(self, address: str, channel: str = "email") -> bool:
        return not self.is_suppressed(address, channel)

    def entries(self) -> list[Entry]:
        rows = self._db.execute(
            "SELECT address, channel, reason, source, logged_at, honor_by FROM suppressed ORDER BY logged_at"
        ).fetchall()
        return [
            Entry(a, c, r, s, datetime.fromisoformat(l), date.fromisoformat(h)) for a, c, r, s, l, h in rows
        ]

    def __len__(self) -> int:
        return self._db.execute("SELECT COUNT(*) FROM suppressed").fetchone()[0]


def record_opt_out(
    email: Email, classification: Classification, suppression: SuppressionList, *, now: datetime | None = None
) -> bool:
    """If the sorter flagged an opt-out, suppress the sender. Returns True if newly suppressed."""
    if not classification.opt_out_request:
        return False
    return suppression.add(
        email.sender,
        channel="email",
        reason="opt-out request",
        source=email.subject[:120],
        now=now,
    )
