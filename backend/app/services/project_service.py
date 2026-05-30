from __future__ import annotations

from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ForbiddenError, NotFoundError
from app.models import Project, ProjectMember
from app.schemas.common import UserContext
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectMemberUpsert
from app.services.audit import log_action
from app.services.permissions import check_permission
from app.services.planner_client import PlannerClient
from app.services.workspace_service import get_workspace


def list_projects(session: Session, workspace_id: UUID, user: UserContext) -> list[Project]:
    get_workspace(session, workspace_id, user)
    return list(session.scalars(select(Project).where(Project.workspace_id == workspace_id).order_by(Project.created_at.desc())))


def get_project(session: Session, workspace_id: UUID, project_id: UUID, user: UserContext) -> Project:
    project = session.get(Project, project_id)
    if not project or project.workspace_id != workspace_id:
        raise NotFoundError("Project not found")
    result = check_permission(session, user_id=user.user_id, action="project.view", target_type="project", target_id=project.id, workspace_id=workspace_id, project_id=project.id, is_platform_admin=user.is_platform_admin)
    if not result.allowed:
        raise ForbiddenError("No access to project")
    return project


def create_project(session: Session, workspace_id: UUID, payload: ProjectCreate, user: UserContext, request_id: str | None = None) -> Project:
    workspace = get_workspace(session, workspace_id, user)
    result = check_permission(session, user_id=user.user_id, action="project.create", target_type="workspace", target_id=workspace.id, workspace_id=workspace.id, is_platform_admin=user.is_platform_admin)
    if not result.allowed:
        raise ForbiddenError("No permission to create project")
    client = PlannerClient()
    calendar_id = client.create_calendar(name=f"CRM · {payload.name}", owner_user_id=user.user_id, scope="project")
    project = Project(workspace_id=workspace_id, name=payload.name, description=payload.description, manager_user_id=payload.manager_user_id, visibility=payload.visibility.value, created_by_user_id=user.user_id, planner_calendar_id=calendar_id)
    session.add(project)
    session.flush()
    session.add(ProjectMember(project_id=project.id, user_id=user.user_id, role_key="project_owner"))
    if payload.manager_user_id and payload.manager_user_id != user.user_id:
        session.add(ProjectMember(project_id=project.id, user_id=payload.manager_user_id, role_key="project_manager"))
    log_action(session, actor_user_id=user.user_id, action="project.create", target_type="project", target_id=str(project.id), workspace_id=workspace_id, project_id=project.id, request_id=request_id)
    session.commit()
    session.refresh(project)
    return project


def update_project(session: Session, workspace_id: UUID, project_id: UUID, payload: ProjectUpdate, user: UserContext, request_id: str | None = None) -> Project:
    project = get_project(session, workspace_id, project_id, user)
    result = check_permission(session, user_id=user.user_id, action="project.edit", target_type="project", target_id=project.id, workspace_id=workspace_id, project_id=project.id, is_platform_admin=user.is_platform_admin)
    if not result.allowed:
        raise ForbiddenError("No permission to edit project")
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(project, key, value.value if hasattr(value, "value") else value)
    log_action(session, actor_user_id=user.user_id, action="project.update", target_type="project", target_id=str(project.id), workspace_id=workspace_id, project_id=project.id, metadata=updates, request_id=request_id)
    session.commit()
    session.refresh(project)
    return project


def upsert_project_member(session: Session, workspace_id: UUID, project_id: UUID, payload: ProjectMemberUpsert, user: UserContext, request_id: str | None = None) -> ProjectMember:
    project = get_project(session, workspace_id, project_id, user)
    result = check_permission(session, user_id=user.user_id, action="project.manage_members", target_type="project", target_id=project.id, workspace_id=workspace_id, project_id=project.id, is_platform_admin=user.is_platform_admin)
    if not result.allowed:
        raise ForbiddenError("No permission to manage project members")
    member = session.scalar(select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == payload.user_id))
    if member:
        member.role_key = payload.role_key.value
    else:
        member = ProjectMember(project_id=project_id, user_id=payload.user_id, role_key=payload.role_key.value)
        session.add(member)
    log_action(session, actor_user_id=user.user_id, action="project.member.upsert", target_type="project_member", target_id=str(payload.user_id), workspace_id=workspace_id, project_id=project_id, request_id=request_id)
    session.commit()
    session.refresh(member)
    return member
