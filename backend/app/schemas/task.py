from __future__ import annotations

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from app.core.enums import Priority, TaskStatus
from app.schemas.common import OrmModel


class TaskCreate(BaseModel):
    workspace_id: UUID
    project_id: UUID | None = None
    deal_id: UUID | None = None
    company_id: UUID | None = None
    contact_id: UUID | None = None
    title: str = Field(min_length=1, max_length=220)
    description: str | None = None
    priority: Priority = Priority.MEDIUM
    assignee_user_id: str | None = None
    deadline_at: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=220)
    description: str | None = None
    priority: Priority | None = None
    status: TaskStatus | None = None
    assignee_user_id: str | None = None
    deadline_at: datetime | None = None


class TaskRead(OrmModel):
    id: UUID
    workspace_id: UUID
    project_id: UUID | None
    deal_id: UUID | None
    company_id: UUID | None
    contact_id: UUID | None
    title: str
    description: str | None
    priority: str
    status: str
    assignee_user_id: str | None
    deadline_at: datetime | None
    planner_event_id: str | None
    planner_sync_status: str
    burned_at: datetime | None
    created_by_user_id: str
    created_at: datetime
    updated_at: datetime
    fire_stage: int = 0
    fire_color: str = "orange"
    day_key: str = "backlog"
    is_burned: bool = False


class WeeklyBoardRead(BaseModel):
    week_start: datetime
    week_end: datetime
    columns: dict[str, list[TaskRead]]
