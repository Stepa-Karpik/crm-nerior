from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, get_request_id
from app.schemas.common import UserContext
from app.schemas.project import ProjectCreate, ProjectMemberRead, ProjectMemberUpsert, ProjectRead, ProjectUpdate
from app.services.project_service import create_project, get_project, list_projects, update_project, upsert_project_member

router = APIRouter(prefix="/workspaces/{workspace_id}/projects", tags=["projects"])


@router.get("", response_model=list[ProjectRead])
def index(workspace_id: UUID, db: Session = Depends(get_db), user: UserContext = Depends(get_current_user)):
    return list_projects(db, workspace_id, user)


@router.post("", response_model=ProjectRead)
def create(workspace_id: UUID, payload: ProjectCreate, db: Session = Depends(get_db), user: UserContext = Depends(get_current_user), request_id: str = Depends(get_request_id)):
    return create_project(db, workspace_id, payload, user, request_id)


@router.get("/{project_id}", response_model=ProjectRead)
def show(workspace_id: UUID, project_id: UUID, db: Session = Depends(get_db), user: UserContext = Depends(get_current_user)):
    return get_project(db, workspace_id, project_id, user)


@router.patch("/{project_id}", response_model=ProjectRead)
def update(workspace_id: UUID, project_id: UUID, payload: ProjectUpdate, db: Session = Depends(get_db), user: UserContext = Depends(get_current_user), request_id: str = Depends(get_request_id)):
    return update_project(db, workspace_id, project_id, payload, user, request_id)


@router.post("/{project_id}/members", response_model=ProjectMemberRead)
def upsert_member(workspace_id: UUID, project_id: UUID, payload: ProjectMemberUpsert, db: Session = Depends(get_db), user: UserContext = Depends(get_current_user), request_id: str = Depends(get_request_id)):
    return upsert_project_member(db, workspace_id, project_id, payload, user, request_id)
