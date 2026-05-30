from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, get_request_id
from app.schemas.common import UserContext
from app.schemas.crm import CompanyCreate, CompanyRead, ContactCreate, ContactRead, DealCreate, DealRead, LeadCreate, LeadRead
from app.services.crm_service import create_company, create_contact, create_deal, create_lead, list_companies, list_contacts, list_deals, list_leads

router = APIRouter(prefix="/workspaces/{workspace_id}/crm", tags=["crm"])


@router.get("/companies", response_model=list[CompanyRead])
def companies(workspace_id: UUID, q: str | None = None, db: Session = Depends(get_db), user: UserContext = Depends(get_current_user)):
    return list_companies(db, workspace_id, user, q)


@router.post("/companies", response_model=CompanyRead)
def add_company(workspace_id: UUID, payload: CompanyCreate, db: Session = Depends(get_db), user: UserContext = Depends(get_current_user), request_id: str = Depends(get_request_id)):
    payload.workspace_id = workspace_id
    return create_company(db, payload, user, request_id)


@router.get("/contacts", response_model=list[ContactRead])
def contacts(workspace_id: UUID, q: str | None = None, db: Session = Depends(get_db), user: UserContext = Depends(get_current_user)):
    return list_contacts(db, workspace_id, user, q)


@router.post("/contacts", response_model=ContactRead)
def add_contact(workspace_id: UUID, payload: ContactCreate, db: Session = Depends(get_db), user: UserContext = Depends(get_current_user), request_id: str = Depends(get_request_id)):
    payload.workspace_id = workspace_id
    return create_contact(db, payload, user, request_id)


@router.get("/deals", response_model=list[DealRead])
def deals(workspace_id: UUID, q: str | None = None, db: Session = Depends(get_db), user: UserContext = Depends(get_current_user)):
    return list_deals(db, workspace_id, user, q)


@router.post("/deals", response_model=DealRead)
def add_deal(workspace_id: UUID, payload: DealCreate, db: Session = Depends(get_db), user: UserContext = Depends(get_current_user), request_id: str = Depends(get_request_id)):
    payload.workspace_id = workspace_id
    return create_deal(db, payload, user, request_id)


@router.get("/leads", response_model=list[LeadRead])
def leads(workspace_id: UUID, q: str | None = None, db: Session = Depends(get_db), user: UserContext = Depends(get_current_user)):
    return list_leads(db, workspace_id, user, q)


@router.post("/leads", response_model=LeadRead)
def add_lead(workspace_id: UUID, payload: LeadCreate, db: Session = Depends(get_db), user: UserContext = Depends(get_current_user), request_id: str = Depends(get_request_id)):
    payload.workspace_id = workspace_id
    return create_lead(db, payload, user, request_id)
