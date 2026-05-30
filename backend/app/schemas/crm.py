from __future__ import annotations

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from app.schemas.common import OrmModel


class CompanyCreate(BaseModel):
    workspace_id: UUID
    name: str = Field(min_length=1, max_length=180)
    legal_name: str | None = None
    tax_id: str | None = None
    address: str | None = None
    website: str | None = None


class CompanyRead(OrmModel):
    id: UUID
    workspace_id: UUID
    name: str
    legal_name: str | None
    tax_id: str | None
    address: str | None
    website: str | None
    created_at: datetime
    updated_at: datetime


class ContactCreate(BaseModel):
    workspace_id: UUID
    company_id: UUID | None = None
    name: str = Field(min_length=1, max_length=180)
    position: str | None = None
    phone: str | None = None
    email: str | None = None
    telegram: str | None = None


class ContactRead(OrmModel):
    id: UUID
    workspace_id: UUID
    company_id: UUID | None
    name: str
    position: str | None
    phone: str | None
    email: str | None
    telegram: str | None
    created_at: datetime
    updated_at: datetime


class DealCreate(BaseModel):
    workspace_id: UUID
    project_id: UUID | None = None
    company_id: UUID | None = None
    contact_id: UUID | None = None
    title: str = Field(min_length=1, max_length=220)
    amount: float | None = None
    currency: str = "RUB"
    probability: int = Field(default=50, ge=0, le=100)
    stage: str = "new_request"
    deadline_at: datetime | None = None
    responsible_user_id: str | None = None


class DealRead(OrmModel):
    id: UUID
    workspace_id: UUID
    project_id: UUID | None
    company_id: UUID | None
    contact_id: UUID | None
    title: str
    amount: float | None
    currency: str
    probability: int
    stage: str
    deadline_at: datetime | None
    responsible_user_id: str | None
    created_at: datetime
    updated_at: datetime


class LeadCreate(BaseModel):
    workspace_id: UUID
    name: str = Field(min_length=1, max_length=180)
    phone: str | None = None
    email: str | None = None
    telegram: str | None = None
    source: str | None = None
    interest: str | None = None
    comment: str | None = None
    responsible_user_id: str | None = None
    status: str = "new"


class LeadRead(OrmModel):
    id: UUID
    workspace_id: UUID
    name: str
    phone: str | None
    email: str | None
    telegram: str | None
    source: str | None
    interest: str | None
    comment: str | None
    responsible_user_id: str | None
    status: str
    created_at: datetime
    updated_at: datetime
