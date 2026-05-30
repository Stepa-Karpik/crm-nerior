from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.errors import ForbiddenError
from app.models import AuditLog, CrmTask, Project, Workspace
from app.schemas.common import AuditRead, UserContext

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(user: UserContext) -> None:
    if not user.is_platform_admin:
        raise ForbiddenError("Platform admin required")


@router.get("/overview")
def overview(db: Session = Depends(get_db), user: UserContext = Depends(get_current_user)):
    require_admin(user)
    return {
        "workspaces": db.scalar(select(func.count(Workspace.id))) or 0,
        "projects": db.scalar(select(func.count(Project.id))) or 0,
        "tasks": db.scalar(select(func.count(CrmTask.id))) or 0,
        "open_tasks": db.scalar(select(func.count(CrmTask.id)).where(CrmTask.status != "done")) or 0,
    }


@router.get("/workspaces")
def workspaces(q: str | None = None, db: Session = Depends(get_db), user: UserContext = Depends(get_current_user)):
    require_admin(user)
    stmt = select(Workspace)
    if q:
        stmt = stmt.where(Workspace.name.ilike(f"%{q.strip()}%"))
    return list(db.scalars(stmt.order_by(Workspace.created_at.desc()).limit(100)))


@router.get("/audit", response_model=list[AuditRead])
def audit(workspace_id: UUID | None = None, db: Session = Depends(get_db), user: UserContext = Depends(get_current_user)):
    require_admin(user)
    stmt = select(AuditLog)
    if workspace_id:
        stmt = stmt.where(AuditLog.workspace_id == workspace_id)
    return list(db.scalars(stmt.order_by(AuditLog.created_at.desc()).limit(200)))
