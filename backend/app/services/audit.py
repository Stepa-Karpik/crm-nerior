from __future__ import annotations

from uuid import UUID
from sqlalchemy.orm import Session

from app.models import AuditLog


def log_action(session: Session, *, actor_user_id: str | None, action: str, target_type: str, target_id: str, workspace_id: UUID | None = None, project_id: UUID | None = None, metadata: dict | None = None, request_id: str | None = None) -> AuditLog:
    item = AuditLog(actor_user_id=actor_user_id, action=action, target_type=target_type, target_id=target_id, workspace_id=workspace_id, project_id=project_id, metadata_json=metadata or {}, request_id=request_id)
    session.add(item)
    return item
