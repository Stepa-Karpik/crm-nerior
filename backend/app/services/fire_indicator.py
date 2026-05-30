from __future__ import annotations

from datetime import datetime
from math import ceil

from app.services.week_board import to_moscow

PRIORITY_COLORS = {
    "low": "amber",
    "medium": "orange",
    "high": "red-orange",
    "critical": "red",
}


def fire_stage(deadline_at: datetime | None, now: datetime) -> int:
    if deadline_at is None:
        return 1
    local_deadline = to_moscow(deadline_at)
    local_now = to_moscow(now)
    if local_deadline < local_now:
        return 0
    seconds = (local_deadline - local_now).total_seconds()
    days_left = max(0, ceil(seconds / 86400))
    return max(1, min(30, 31 - days_left))


def fire_color(priority: str) -> str:
    return PRIORITY_COLORS.get(priority, "orange")
