from __future__ import annotations

from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ForbiddenError
from app.models import Company, Contact, Deal, Lead
from app.schemas.common import UserContext
from app.schemas.crm import CompanyCreate, ContactCreate, DealCreate, LeadCreate
from app.services.audit import log_action
from app.services.permissions import check_permission
from app.services.workspace_service import get_workspace


def _can(session: Session, user: UserContext, workspace_id: UUID, action: str) -> None:
    get_workspace(session, workspace_id, user)
    result = check_permission(session, user_id=user.user_id, action=action, target_type="workspace", target_id=workspace_id, workspace_id=workspace_id, is_platform_admin=user.is_platform_admin)
    if not result.allowed:
        raise ForbiddenError(f"No permission: {action}")


def list_companies(session: Session, workspace_id: UUID, user: UserContext, q: str | None = None) -> list[Company]:
    _can(session, user, workspace_id, "crm.view_companies")
    stmt = select(Company).where(Company.workspace_id == workspace_id)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where((Company.name.ilike(like)) | (Company.legal_name.ilike(like)))
    return list(session.scalars(stmt.order_by(Company.name.asc())))


def create_company(session: Session, payload: CompanyCreate, user: UserContext, request_id: str | None = None) -> Company:
    _can(session, user, payload.workspace_id, "crm.edit_companies")
    item = Company(**payload.model_dump(), created_by_user_id=user.user_id)
    session.add(item)
    session.flush()
    log_action(session, actor_user_id=user.user_id, action="crm.company.create", target_type="company", target_id=str(item.id), workspace_id=item.workspace_id, request_id=request_id)
    session.commit(); session.refresh(item); return item


def list_contacts(session: Session, workspace_id: UUID, user: UserContext, q: str | None = None) -> list[Contact]:
    _can(session, user, workspace_id, "crm.view_contacts")
    stmt = select(Contact).where(Contact.workspace_id == workspace_id)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where((Contact.name.ilike(like)) | (Contact.email.ilike(like)) | (Contact.phone.ilike(like)))
    return list(session.scalars(stmt.order_by(Contact.name.asc())))


def create_contact(session: Session, payload: ContactCreate, user: UserContext, request_id: str | None = None) -> Contact:
    _can(session, user, payload.workspace_id, "crm.edit_contacts")
    item = Contact(**payload.model_dump(), created_by_user_id=user.user_id)
    session.add(item); session.flush()
    log_action(session, actor_user_id=user.user_id, action="crm.contact.create", target_type="contact", target_id=str(item.id), workspace_id=item.workspace_id, request_id=request_id)
    session.commit(); session.refresh(item); return item


def list_deals(session: Session, workspace_id: UUID, user: UserContext, q: str | None = None) -> list[Deal]:
    _can(session, user, workspace_id, "crm.view_deals")
    stmt = select(Deal).where(Deal.workspace_id == workspace_id)
    if q:
        stmt = stmt.where(Deal.title.ilike(f"%{q.strip()}%"))
    return list(session.scalars(stmt.order_by(Deal.updated_at.desc())))


def create_deal(session: Session, payload: DealCreate, user: UserContext, request_id: str | None = None) -> Deal:
    _can(session, user, payload.workspace_id, "crm.edit_deals")
    item = Deal(**payload.model_dump(), created_by_user_id=user.user_id)
    session.add(item); session.flush()
    log_action(session, actor_user_id=user.user_id, action="crm.deal.create", target_type="deal", target_id=str(item.id), workspace_id=item.workspace_id, project_id=item.project_id, request_id=request_id)
    session.commit(); session.refresh(item); return item


def list_leads(session: Session, workspace_id: UUID, user: UserContext, q: str | None = None) -> list[Lead]:
    _can(session, user, workspace_id, "crm.view_leads")
    stmt = select(Lead).where(Lead.workspace_id == workspace_id)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where((Lead.name.ilike(like)) | (Lead.email.ilike(like)) | (Lead.phone.ilike(like)) | (Lead.interest.ilike(like)))
    return list(session.scalars(stmt.order_by(Lead.created_at.desc())))


def create_lead(session: Session, payload: LeadCreate, user: UserContext, request_id: str | None = None) -> Lead:
    _can(session, user, payload.workspace_id, "crm.edit_leads")
    item = Lead(**payload.model_dump(), created_by_user_id=user.user_id)
    session.add(item); session.flush()
    log_action(session, actor_user_id=user.user_id, action="crm.lead.create", target_type="lead", target_id=str(item.id), workspace_id=item.workspace_id, request_id=request_id)
    session.commit(); session.refresh(item); return item
