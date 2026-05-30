from datetime import datetime, timezone

from app.services.fire_indicator import fire_color, fire_stage
from app.services.week_board import day_key, is_burned, week_range_moscow


def dt(value: str):
    return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)


def test_week_starts_on_monday_moscow():
    week = week_range_moscow(dt("2026-05-30T12:00:00"))
    assert week.start.isoformat() == "2026-05-25T00:00:00+03:00"
    assert week.end.isoformat() == "2026-06-01T00:00:00+03:00"


def test_day_key_places_past_previous_week_into_burned():
    assert day_key(dt("2026-05-20T10:00:00"), dt("2026-05-30T12:00:00")) == "burned"


def test_day_key_places_future_deadline_outside_current_board():
    assert day_key(dt("2026-06-08T10:00:00"), dt("2026-05-30T12:00:00")) == "future"


def test_burned_ignores_done_tasks():
    assert is_burned(dt("2026-05-20T10:00:00"), "done", dt("2026-05-30T12:00:00")) is False


def test_fire_stage_has_thirty_steps_and_disappears_after_deadline():
    now = dt("2026-05-30T00:00:00")
    assert fire_stage(dt("2026-06-29T00:00:00"), now) == 1
    assert fire_stage(dt("2026-05-31T00:00:00"), now) == 30
    assert fire_stage(dt("2026-05-29T23:59:00"), now) == 0


def test_fire_color_follows_priority():
    assert fire_color("critical") == "red"
    assert fire_color("low") == "amber"
