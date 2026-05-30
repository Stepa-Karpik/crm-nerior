from __future__ import annotations

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserContext(BaseModel):
    user_id: UUID
    username: str = "user"
    display_name: str | None = None
    email: str | None = None
    is_platform_admin: bool = False


class AuditRead(OrmModel):
    id: UUID
    workspace_id: UUID | None
    project_id: UUID | None
    actor_user_id: UUID | None
    action: str
    target_type: str
    target_id: str
    metadata_json: dict | None = None
    created_at: datetime
