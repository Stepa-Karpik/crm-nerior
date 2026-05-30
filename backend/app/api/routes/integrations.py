from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, get_request_id
from app.schemas.common import UserContext
from app.schemas.integration import DocumentLinkCreate, EntityLinkRead, PlannerSettingsRead, PlannerSettingsUpdate
from app.services.integration_service import get_planner_settings, link_document, update_planner_settings

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("/planner/settings", response_model=PlannerSettingsRead)
def planner_settings(db: Session = Depends(get_db), user: UserContext = Depends(get_current_user)):
    return get_planner_settings(db, user)


@router.patch("/planner/settings", response_model=PlannerSettingsRead)
def update_planner(payload: PlannerSettingsUpdate, db: Session = Depends(get_db), user: UserContext = Depends(get_current_user)):
    return update_planner_settings(db, payload, user)


@router.post("/documents/links", response_model=EntityLinkRead)
def add_document_link(payload: DocumentLinkCreate, db: Session = Depends(get_db), user: UserContext = Depends(get_current_user), request_id: str = Depends(get_request_id)):
    return link_document(db, payload, user, request_id)
