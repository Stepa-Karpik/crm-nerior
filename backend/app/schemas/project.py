from __future__ import annotations

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from app.core.enums import ProjectRole, ProjectStatus, Visibility
from app.schemas.common import OrmModel


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    description: str | None = None
    manager_user_id: str | None = None
    visibility: Visibility = Visibility.PROJECT


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=180)
    description: str | None = None
    manager_user_id: str | None = None
    status: ProjectStatus | None = None
    visibility: Visibility | None = None


class ProjectRead(OrmModel):
    id: UUID
    workspace_id: UUID
    name: str
    description: str | None
    status: str
    visibility: str
    manager_user_id: str | None
    planner_calendar_id: str | None
    documents_scope_id: str | None
    created_by_user_id: str
    created_at: datetime
    updated_at: datetime


class ProjectMemberUpsert(BaseModel):
    user_id: str
    role_key: ProjectRole = ProjectRole.EXECUTOR


class ProjectMemberRead(OrmModel):
    id: UUID
    project_id: UUID
    user_id: str
    role_key: str
    created_at: datetime
