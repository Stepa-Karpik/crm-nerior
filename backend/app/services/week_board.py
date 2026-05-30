from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

MOSCOW_TZ = ZoneInfo("Europe/Moscow")


@dataclass(frozen=True)
class WeekRange:
    start: datetime
    end: datetime


def to_moscow(value: datetime) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(MOSCOW_TZ)


def week_range_moscow(now: datetime) -> WeekRange:
    local = to_moscow(now)
    start_date = (local - timedelta(days=local.weekday())).date()
    start = datetime.combine(start_date, datetime.min.time(), tzinfo=MOSCOW_TZ)
    return WeekRange(start=start, end=start + timedelta(days=7))


def day_key(deadline_at: datetime | None, now: datetime) -> str:
    if deadline_at is None:
        return "backlog"
    week = week_range_moscow(now)
    local_deadline = to_moscow(deadline_at)
    if local_deadline < week.start:
        return "burned"
    if local_deadline >= week.end:
        return "future"
    return ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"][local_deadline.weekday()]


def is_burned(deadline_at: datetime | None, status: str, now: datetime) -> bool:
    if deadline_at is None or status in {"done", "archived"}:
        return False
    return to_moscow(deadline_at) < to_moscow(now)
