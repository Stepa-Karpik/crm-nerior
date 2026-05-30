from __future__ import annotations

import uuid
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class PlannerEventPayload(BaseModel):
    title: str
    description: str | None = None
    deadline_at: datetime
    calendar_id: str | None = None
    location: str | None = None
    workspace_id: UUID
    project_id: UUID | None = None
    crm_task_id: UUID


class PlannerClient:
    def create_calendar(self, *, name: str, owner_user_id: str, scope: str) -> str:
        return f"crm-{scope}-cal-{uuid.uuid4()}"

    def create_or_update_task_event(self, payload: PlannerEventPayload, existing_event_id: str | None = None) -> tuple[str, str]:
        return existing_event_id or f"crm-task-event-{uuid.uuid4()}", "synced"

    def mark_task_done(self, event_id: str | None) -> None:
        return None
