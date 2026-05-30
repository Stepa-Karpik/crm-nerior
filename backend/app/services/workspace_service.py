from __future__ import annotations

from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ForbiddenError, NotFoundError
from app.models import Workspace, WorkspaceMember, WorkspaceGroup, WorkspaceGroupMember
from app.schemas.common import UserContext
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceMemberInvite
from app.services.audit import log_action
from app.services.permissions import check_permission


def list_workspaces(session: Session, user: UserContext) -> list[Workspace]:
    if user.is_platform_admin:
        return list(session.scalars(select(Workspace).order_by(Workspace.created_at.desc())))
    member_workspace_ids = select(WorkspaceMember.workspace_id).where(
        WorkspaceMember.user_id == user.user_id,
        WorkspaceMember.status == "active",
    )
    return list(
        session.scalars(
            select(Workspace)
            .where((Workspace.owner_user_id == user.user_id) | (Workspace.id.in_(member_workspace_ids)))
            .order_by(Workspace.created_at.desc())
        )
    )


def create_workspace(session: Session, payload: WorkspaceCreate, user: UserContext, request_id: str | None = None) -> Workspace:
    workspace = Workspace(
        owner_user_id=user.user_id,
        name=payload.name,
        description=payload.description,
        icon=payload.icon,
    )
    session.add(workspace)
    session.flush()
    session.add(
        WorkspaceMember(
            workspace_id=workspace.id,
            user_id=user.user_id,
            display_name=user.display_name or user.username,
            email=user.email,
            role_key="owner",
            status="active",
        )
    )
    log_action(session, actor_user_id=user.user_id, action="workspace.create", target_type="workspace", target_id=str(workspace.id), workspace_id=workspace.id, request_id=request_id)
    session.commit()
    session.refresh(workspace)
    return workspace


def get_workspace(session: Session, workspace_id: UUID, user: UserContext) -> Workspace:
    workspace = session.get(Workspace, workspace_id)
    if not workspace:
        raise NotFoundError("Workspace not found")
    result = check_permission(session, user_id=user.user_id, action="workspace.view", target_type="workspace", target_id=workspace.id, workspace_id=workspace.id, is_platform_admin=user.is_platform_admin)
    if not result.allowed:
        raise ForbiddenError("No access to workspace")
    return workspace


def update_workspace(session: Session, workspace_id: UUID, payload: WorkspaceUpdate, user: UserContext, request_id: str | None = None) -> Workspace:
    workspace = get_workspace(session, workspace_id, user)
    result = check_permission(session, user_id=user.user_id, action="workspace.edit", target_type="workspace", target_id=workspace.id, workspace_id=workspace.id, is_platform_admin=user.is_platform_admin)
    if not result.allowed:
        raise ForbiddenError("No permission to edit workspace")
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(workspace, key, value.value if hasattr(value, "value") else value)
    log_action(session, actor_user_id=user.user_id, action="workspace.update", target_type="workspace", target_id=str(workspace.id), workspace_id=workspace.id, metadata=updates, request_id=request_id)
    session.commit()
    session.refresh(workspace)
    return workspace


def invite_member(session: Session, workspace_id: UUID, payload: WorkspaceMemberInvite, user: UserContext, request_id: str | None = None) -> WorkspaceMember:
    workspace = get_workspace(session, workspace_id, user)
    result = check_permission(session, user_id=user.user_id, action="workspace.invite_members", target_type="workspace", target_id=workspace.id, workspace_id=workspace.id, is_platform_admin=user.is_platform_admin)
    if not result.allowed:
        raise ForbiddenError("No permission to invite members")
    member = session.scalar(select(WorkspaceMember).where(WorkspaceMember.workspace_id == workspace_id, WorkspaceMember.user_id == payload.user_id))
    if member:
        member.role_key = payload.role_key.value
        member.status = "active"
        member.display_name = payload.display_name
        member.email = payload.email
    else:
        member = WorkspaceMember(workspace_id=workspace_id, user_id=payload.user_id, display_name=payload.display_name, email=payload.email, role_key=payload.role_key.value, status="active", invited_by_user_id=user.user_id)
        session.add(member)
    log_action(session, actor_user_id=user.user_id, action="workspace.member.upsert", target_type="workspace_member", target_id=str(payload.user_id), workspace_id=workspace_id, request_id=request_id)
    session.commit()
    session.refresh(member)
    return member


def list_members(session: Session, workspace_id: UUID, user: UserContext) -> list[WorkspaceMember]:
    get_workspace(session, workspace_id, user)
    return list(session.scalars(select(WorkspaceMember).where(WorkspaceMember.workspace_id == workspace_id).order_by(WorkspaceMember.created_at.asc())))
