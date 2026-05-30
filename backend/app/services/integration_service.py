from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import EntityLink, PlannerIntegrationSettings
from app.schemas.common import UserContext
from app.schemas.integration import DocumentLinkCreate, PlannerSettingsUpdate
from app.services.audit import log_action
from app.services.workspace_service import get_workspace


def get_planner_settings(session: Session, user: UserContext) -> PlannerIntegrationSettings:
    item = session.scalar(select(PlannerIntegrationSettings).where(PlannerIntegrationSettings.user_id == user.user_id))
    if item:
        return item
    item = PlannerIntegrationSettings(user_id=user.user_id)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def update_planner_settings(session: Session, payload: PlannerSettingsUpdate, user: UserContext) -> PlannerIntegrationSettings:
    item = get_planner_settings(session, user)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    session.commit(); session.refresh(item); return item


def link_document(session: Session, payload: DocumentLinkCreate, user: UserContext, request_id: str | None = None) -> EntityLink:
    get_workspace(session, payload.workspace_id, user)
    item = EntityLink(workspace_id=payload.workspace_id, source_type=payload.source_type, source_id=payload.source_id, target_service="documents", target_type="document", target_id=payload.document_id, relation_type=payload.relation_type, created_by_user_id=user.user_id)
    session.add(item); session.flush()
    log_action(session, actor_user_id=user.user_id, action="document.link", target_type=payload.source_type, target_id=str(payload.source_id), workspace_id=payload.workspace_id, metadata={"document_id": payload.document_id}, request_id=request_id)
    session.commit(); session.refresh(item); return item
