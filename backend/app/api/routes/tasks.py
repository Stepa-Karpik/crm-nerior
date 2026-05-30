from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, get_request_id
from app.schemas.common import UserContext
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate, WeeklyBoardRead
from app.services.task_service import create_task, list_tasks, update_task, weekly_board

router = APIRouter(prefix="/workspaces/{workspace_id}/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskRead])
def index(workspace_id: UUID, project_id: UUID | None = None, q: str | None = None, db: Session = Depends(get_db), user: UserContext = Depends(get_current_user)):
    return list_tasks(db, workspace_id, user, project_id=project_id, q=q)


@router.post("", response_model=TaskRead)
def create(workspace_id: UUID, payload: TaskCreate, db: Session = Depends(get_db), user: UserContext = Depends(get_current_user), request_id: str = Depends(get_request_id)):
    payload.workspace_id = workspace_id
    return create_task(db, payload, user, request_id)


@router.patch("/{task_id}", response_model=TaskRead)
def update(workspace_id: UUID, task_id: UUID, payload: TaskUpdate, db: Session = Depends(get_db), user: UserContext = Depends(get_current_user), request_id: str = Depends(get_request_id)):
    return update_task(db, workspace_id, task_id, payload, user, request_id)


@router.get("/weekly", response_model=WeeklyBoardRead)
def weekly(workspace_id: UUID, project_id: UUID | None = Query(default=None), db: Session = Depends(get_db), user: UserContext = Depends(get_current_user)):
    return weekly_board(db, workspace_id, user, project_id=project_id)
