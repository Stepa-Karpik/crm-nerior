from __future__ import annotations

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from app.schemas.common import OrmModel


class PlannerSettingsUpdate(BaseModel):
    crm_routes_enabled: bool | None = None
    crm_deadline_notifications_enabled: bool | None = None
    crm_deadline_notice_hours: int | None = Field(default=None, ge=1, le=720)
    crm_deadline_notice_start_time: str | None = Field(default=None, pattern=r"^\d{2}:\d{2}$")


class PlannerSettingsRead(OrmModel):
    id: UUID
    user_id: UUID
    crm_routes_enabled: bool
    crm_deadline_notifications_enabled: bool
    crm_deadline_notice_hours: int
    crm_deadline_notice_start_time: str
    created_at: datetime
    updated_at: datetime


class DocumentLinkCreate(BaseModel):
    workspace_id: UUID
    source_type: str
    source_id: UUID
    document_id: str
    relation_type: str = "related"


class EntityLinkRead(OrmModel):
    id: UUID
    workspace_id: UUID
    source_type: str
    source_id: UUID
    target_service: str
    target_type: str
    target_id: str
    relation_type: str
    created_by_user_id: UUID
    created_at: datetime
