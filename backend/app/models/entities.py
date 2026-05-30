from __future__ import annotations

import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.core.db import Base
from app.core.types import GUID


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(GUID(), primary_key=True, default=uuid.uuid4)


JsonType = JSON().with_variant(JSONB, "postgresql")


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[uuid.UUID] = uuid_pk()
    owner_user_id: Mapped[str] = mapped_column(String(128), index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    icon: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)
    default_timezone: Mapped[str] = mapped_column(String(64), default="Europe/Moscow")
    planner_calendar_id: Mapped[str | None] = mapped_column(String(128))
    documents_scope_id: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    members: Mapped[list[WorkspaceMember]] = relationship(back_populates="workspace", cascade="all, delete-orphan")


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"
    __table_args__ = (UniqueConstraint("workspace_id", "user_id", name="uq_workspace_member"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    workspace_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("workspaces.id"), index=True)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    display_name: Mapped[str | None] = mapped_column(String(160))
    email: Mapped[str | None] = mapped_column(String(255))
    role_key: Mapped[str] = mapped_column(String(48), default="member")
    status: Mapped[str] = mapped_column(String(32), default="active")
    invited_by_user_id: Mapped[str | None] = mapped_column(String(128))
    joined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    workspace: Mapped[Workspace] = relationship(back_populates="members")


class WorkspaceGroup(Base):
    __tablename__ = "workspace_groups"

    id: Mapped[uuid.UUID] = uuid_pk()
    workspace_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("workspaces.id"), index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    created_by_user_id: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class WorkspaceGroupMember(Base):
    __tablename__ = "workspace_group_members"
    __table_args__ = (UniqueConstraint("workspace_group_id", "user_id", name="uq_workspace_group_member"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    workspace_group_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("workspace_groups.id"), index=True)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = uuid_pk()
    workspace_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("workspaces.id"), index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="active")
    visibility: Mapped[str] = mapped_column(String(32), default="project")
    manager_user_id: Mapped[str | None] = mapped_column(String(128), index=True)
    planner_calendar_id: Mapped[str | None] = mapped_column(String(128))
    documents_scope_id: Mapped[str | None] = mapped_column(String(128))
    created_by_user_id: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class ProjectMember(Base):
    __tablename__ = "project_members"
    __table_args__ = (UniqueConstraint("project_id", "user_id", name="uq_project_member"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("projects.id"), index=True)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    role_key: Mapped[str] = mapped_column(String(48), default="executor")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class AccessPolicy(Base):
    __tablename__ = "access_policies"

    id: Mapped[uuid.UUID] = uuid_pk()
    workspace_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("workspaces.id"), index=True)
    subject_type: Mapped[str] = mapped_column(String(48), index=True)
    subject_id: Mapped[str | None] = mapped_column(String(128), index=True)
    target_type: Mapped[str] = mapped_column(String(64), index=True)
    target_id: Mapped[uuid.UUID] = mapped_column(GUID(), index=True)
    action: Mapped[str] = mapped_column(String(80), index=True)
    rule: Mapped[str] = mapped_column(String(16), default="allow")
    source: Mapped[str] = mapped_column(String(24), default="direct")
    created_by_user_id: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = uuid_pk()
    workspace_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("workspaces.id"), index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    legal_name: Mapped[str | None] = mapped_column(String(220))
    tax_id: Mapped[str | None] = mapped_column(String(64))
    address: Mapped[str | None] = mapped_column(Text)
    website: Mapped[str | None] = mapped_column(String(255))
    created_by_user_id: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[uuid.UUID] = uuid_pk()
    workspace_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("workspaces.id"), index=True)
    company_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("companies.id"), index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    position: Mapped[str | None] = mapped_column(String(160))
    phone: Mapped[str | None] = mapped_column(String(80))
    email: Mapped[str | None] = mapped_column(String(255))
    telegram: Mapped[str | None] = mapped_column(String(120))
    created_by_user_id: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[uuid.UUID] = uuid_pk()
    workspace_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("workspaces.id"), index=True)
    project_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("projects.id"), index=True)
    company_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("companies.id"), index=True)
    contact_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("contacts.id"), index=True)
    title: Mapped[str] = mapped_column(String(220), nullable=False)
    amount: Mapped[float | None] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(12), default="RUB")
    probability: Mapped[int] = mapped_column(Integer, default=50)
    stage: Mapped[str] = mapped_column(String(80), default="new_request")
    deadline_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    responsible_user_id: Mapped[str | None] = mapped_column(String(128), index=True)
    created_by_user_id: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = uuid_pk()
    workspace_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("workspaces.id"), index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(80))
    email: Mapped[str | None] = mapped_column(String(255))
    telegram: Mapped[str | None] = mapped_column(String(120))
    source: Mapped[str | None] = mapped_column(String(120))
    interest: Mapped[str | None] = mapped_column(Text)
    comment: Mapped[str | None] = mapped_column(Text)
    responsible_user_id: Mapped[str | None] = mapped_column(String(128), index=True)
    status: Mapped[str] = mapped_column(String(64), default="new")
    created_by_user_id: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class CrmTask(Base):
    __tablename__ = "crm_tasks"

    id: Mapped[uuid.UUID] = uuid_pk()
    workspace_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("workspaces.id"), index=True)
    project_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("projects.id"), index=True)
    deal_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("deals.id"), index=True)
    company_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("companies.id"), index=True)
    contact_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("contacts.id"), index=True)
    title: Mapped[str] = mapped_column(String(220), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(24), default="medium", index=True)
    status: Mapped[str] = mapped_column(String(32), default="not_started", index=True)
    assignee_user_id: Mapped[str | None] = mapped_column(String(128), index=True)
    deadline_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    planner_event_id: Mapped[str | None] = mapped_column(String(128), index=True)
    planner_sync_status: Mapped[str] = mapped_column(String(32), default="pending")
    burned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sort_order: Mapped[float] = mapped_column(Numeric(12, 4), default=0)
    created_by_user_id: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class KanbanBoard(Base):
    __tablename__ = "kanban_boards"

    id: Mapped[uuid.UUID] = uuid_pk()
    workspace_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("workspaces.id"), index=True)
    project_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    view_type: Mapped[str] = mapped_column(String(32), default="weekly")
    created_by_user_id: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class KanbanCard(Base):
    __tablename__ = "kanban_cards"

    id: Mapped[uuid.UUID] = uuid_pk()
    board_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("kanban_boards.id"), index=True)
    task_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("crm_tasks.id"), index=True)
    deal_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("deals.id"), index=True)
    column_key: Mapped[str] = mapped_column(String(80), index=True)
    sort_order: Mapped[float] = mapped_column(Numeric(12, 4), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class EntityLink(Base):
    __tablename__ = "entity_links"

    id: Mapped[uuid.UUID] = uuid_pk()
    workspace_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("workspaces.id"), index=True)
    source_type: Mapped[str] = mapped_column(String(80), index=True)
    source_id: Mapped[uuid.UUID] = mapped_column(GUID(), index=True)
    target_service: Mapped[str] = mapped_column(String(40), index=True)
    target_type: Mapped[str] = mapped_column(String(80), index=True)
    target_id: Mapped[str] = mapped_column(String(160), index=True)
    relation_type: Mapped[str] = mapped_column(String(80), default="related")
    created_by_user_id: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class PlannerIntegrationSettings(Base):
    __tablename__ = "planner_integration_settings"
    __table_args__ = (UniqueConstraint("user_id", name="uq_planner_crm_settings_user"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    crm_routes_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    crm_deadline_notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    crm_deadline_notice_hours: Mapped[int] = mapped_column(Integer, default=24)
    crm_deadline_notice_start_time: Mapped[str] = mapped_column(String(8), default="09:00")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = uuid_pk()
    workspace_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), index=True)
    project_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), index=True)
    actor_user_id: Mapped[str | None] = mapped_column(String(128), index=True)
    action: Mapped[str] = mapped_column(String(120), index=True)
    target_type: Mapped[str] = mapped_column(String(80), index=True)
    target_id: Mapped[str] = mapped_column(String(160), index=True)
    metadata_json: Mapped[dict | None] = mapped_column(JsonType)
    request_id: Mapped[str | None] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, index=True)
