from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, get_request_id
from app.schemas.common import UserContext
from app.schemas.workspace import WorkspaceCreate, WorkspaceMemberInvite, WorkspaceMemberRead, WorkspaceRead, WorkspaceUpdate
from app.services.workspace_service import create_workspace, invite_member, list_members, list_workspaces, update_workspace, get_workspace

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("", response_model=list[WorkspaceRead])
def index(db: Session = Depends(get_db), user: UserContext = Depends(get_current_user)):
    return list_workspaces(db, user)


@router.post("", response_model=WorkspaceRead)
def create(payload: WorkspaceCreate, request: Request, db: Session = Depends(get_db), user: UserContext = Depends(get_current_user), request_id: str = Depends(get_request_id)):
    return create_workspace(db, payload, user, request_id)


@router.get("/{workspace_id}", response_model=WorkspaceRead)
def show(workspace_id: UUID, db: Session = Depends(get_db), user: UserContext = Depends(get_current_user)):
    return get_workspace(db, workspace_id, user)


@router.patch("/{workspace_id}", response_model=WorkspaceRead)
def update(workspace_id: UUID, payload: WorkspaceUpdate, db: Session = Depends(get_db), user: UserContext = Depends(get_current_user), request_id: str = Depends(get_request_id)):
    return update_workspace(db, workspace_id, payload, user, request_id)


@router.get("/{workspace_id}/members", response_model=list[WorkspaceMemberRead])
def members(workspace_id: UUID, db: Session = Depends(get_db), user: UserContext = Depends(get_current_user)):
    return list_members(db, workspace_id, user)


@router.post("/{workspace_id}/members", response_model=WorkspaceMemberRead)
def invite(workspace_id: UUID, payload: WorkspaceMemberInvite, db: Session = Depends(get_db), user: UserContext = Depends(get_current_user), request_id: str = Depends(get_request_id)):
    return invite_member(db, workspace_id, payload, user, request_id)
