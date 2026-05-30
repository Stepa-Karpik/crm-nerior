from __future__ import annotations

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from app.core.enums import WorkspaceRole, WorkspaceStatus
from app.schemas.common import OrmModel


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str | None = None
    icon: str | None = None


class WorkspaceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = None
    icon: str | None = None
    status: WorkspaceStatus | None = None


class WorkspaceRead(OrmModel):
    id: UUID
    owner_user_id: UUID
    name: str
    description: str | None
    icon: str | None
    status: str
    default_timezone: str
    planner_calendar_id: str | None
    documents_scope_id: str | None
    created_at: datetime
    updated_at: datetime


class WorkspaceMemberInvite(BaseModel):
    user_id: UUID
    display_name: str | None = None
    email: str | None = None
    role_key: WorkspaceRole = WorkspaceRole.MEMBER


class WorkspaceMemberRead(OrmModel):
    id: UUID
    workspace_id: UUID
    user_id: UUID
    display_name: str | None
    email: str | None
    role_key: str
    status: str
    created_at: datetime
