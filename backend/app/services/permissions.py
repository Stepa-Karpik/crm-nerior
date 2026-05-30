from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import WorkspaceRole
from app.models import AccessPolicy, Project, ProjectMember, Workspace, WorkspaceMember

ROLE_PERMISSIONS: dict[str, set[str]] = {
    WorkspaceRole.OWNER.value: {"*"},
    WorkspaceRole.ADMIN.value: {"workspace.view", "workspace.edit", "workspace.invite_members", "workspace.manage_roles", "workspace.manage_groups", "workspace.manage_permissions", "workspace.manage_integrations", "workspace.view_audit_log", "project.*", "kanban.*", "task.*", "document.*", "calendar.*", "crm.*"},
    WorkspaceRole.MANAGER.value: {"workspace.view", "project.view", "project.create", "project.edit", "project.manage_members", "kanban.*", "task.*", "document.view", "document.preview", "document.upload", "document.link_to_project", "document.ai_analyze", "calendar.view", "calendar.create_event", "calendar.edit_event", "crm.view_*", "crm.edit_*", "crm.convert_leads", "crm.view_amounts"},
    WorkspaceRole.MEMBER.value: {"workspace.view", "project.view", "kanban.view", "kanban.view_card", "kanban.move_card", "kanban.complete_card", "kanban.comment", "task.view", "task.complete", "task.comment", "document.view", "document.preview", "calendar.view", "crm.view_*"},
    WorkspaceRole.VIEWER.value: {"workspace.view", "project.view", "kanban.view", "kanban.view_card", "task.view", "document.view", "document.preview", "calendar.view", "crm.view_*"},
    WorkspaceRole.GUEST.value: {"workspace.view_limited", "project.view", "kanban.view_card", "task.view", "document.view", "document.preview", "calendar.view"},
}

PROJECT_ROLE_PERMISSIONS = {
    "project_owner": {"project.*", "kanban.*", "task.*", "document.*", "calendar.*", "crm.*"},
    "project_manager": {"project.view", "project.edit", "kanban.*", "task.*", "document.view", "document.preview", "document.upload", "calendar.view", "calendar.create_event", "calendar.edit_event", "crm.view_*", "crm.edit_*"},
    "executor": {"project.view", "kanban.view", "kanban.view_card", "kanban.complete_card", "kanban.comment", "task.view", "task.complete", "task.comment", "task.attach_file", "document.view", "document.preview", "calendar.view"},
    "viewer": {"project.view", "kanban.view", "kanban.view_card", "task.view", "document.view", "document.preview", "calendar.view"},
    "external_guest": {"project.view", "kanban.view_card", "task.view", "document.view", "document.preview", "calendar.view"},
}


@dataclass(frozen=True)
class PermissionResult:
    allowed: bool
    reason: str
    source: str


def _matches(grants: set[str], action: str) -> bool:
    if "*" in grants or action in grants:
        return True
    namespace = action.split(".", 1)[0]
    if f"{namespace}.*" in grants:
        return True
    if action.startswith("crm.view_") and "crm.view_*" in grants:
        return True
    if action.startswith("crm.edit_") and "crm.edit_*" in grants:
        return True
    return False


def workspace_member(session: Session, workspace_id: UUID, user_id: UUID) -> WorkspaceMember | None:
    return session.scalar(select(WorkspaceMember).where(WorkspaceMember.workspace_id == workspace_id, WorkspaceMember.user_id == user_id, WorkspaceMember.status == "active"))


def project_member(session: Session, project_id: UUID, user_id: UUID) -> ProjectMember | None:
    return session.scalar(select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id))


def check_permission(session: Session, *, user_id: UUID, action: str, target_type: str, target_id: UUID, workspace_id: UUID, project_id: UUID | None = None, is_platform_admin: bool = False) -> PermissionResult:
    if is_platform_admin:
        return PermissionResult(True, "platform admin", "platform_admin")

    workspace = session.get(Workspace, workspace_id)
    if workspace and workspace.owner_user_id == user_id:
        return PermissionResult(True, "workspace owner", "owner")

    policies = list(session.scalars(select(AccessPolicy).where(AccessPolicy.workspace_id == workspace_id, AccessPolicy.target_type == target_type, AccessPolicy.target_id == target_id, AccessPolicy.action == action)))
    for policy in policies:
        if policy.subject_type == "user" and policy.subject_id == str(user_id) and policy.rule == "deny":
            return PermissionResult(False, "explicit deny", "direct_deny")
    for policy in policies:
        if policy.subject_type == "user" and policy.subject_id == str(user_id) and policy.rule == "allow":
            return PermissionResult(True, "explicit allow", "direct_allow")

    if project_id:
        pm = project_member(session, project_id, user_id)
        if pm and _matches(PROJECT_ROLE_PERMISSIONS.get(pm.role_key, set()), action):
            return PermissionResult(True, "project role", "project_role")

    wm = workspace_member(session, workspace_id, user_id)
    if wm and _matches(ROLE_PERMISSIONS.get(wm.role_key, set()), action):
        return PermissionResult(True, "workspace role", "workspace_role")

    return PermissionResult(False, "no matching permission", "none")
