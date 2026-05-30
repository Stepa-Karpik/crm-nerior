from __future__ import annotations

from enum import StrEnum


class WorkspaceStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    SUSPENDED = "suspended"


class MemberStatus(StrEnum):
    ACTIVE = "active"
    INVITED = "invited"
    SUSPENDED = "suspended"
    REMOVED = "removed"


class WorkspaceRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"
    GUEST = "guest"


class ProjectRole(StrEnum):
    PROJECT_OWNER = "project_owner"
    PROJECT_MANAGER = "project_manager"
    EXECUTOR = "executor"
    VIEWER = "viewer"
    EXTERNAL_GUEST = "external_guest"


class ProjectStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TaskStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BURNED = "burned"
    ARCHIVED = "archived"


class Priority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Visibility(StrEnum):
    WORKSPACE = "workspace"
    PROJECT = "project"
    RESTRICTED = "restricted"
    PRIVATE = "private"
    EXTERNAL = "external"


class Rule(StrEnum):
    ALLOW = "allow"
    DENY = "deny"


class SubjectType(StrEnum):
    USER = "user"
    GROUP = "group"
    WORKSPACE_ROLE = "workspace_role"
    PROJECT_ROLE = "project_role"
    PUBLIC_WORKSPACE = "public_workspace"
