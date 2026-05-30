from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ForbiddenError, NotFoundError
from app.models import CrmTask, Project, Company
from app.schemas.common import UserContext
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate, WeeklyBoardRead
from app.services.audit import log_action
from app.services.fire_indicator import fire_color, fire_stage
from app.services.permissions import check_permission
from app.services.planner_client import PlannerClient, PlannerEventPayload
from app.services.week_board import day_key, is_burned, week_range_moscow
from app.services.workspace_service import get_workspace


def _task_to_read(task: CrmTask, now: datetime | None = None) -> TaskRead:
    now = now or datetime.now(timezone.utc)
    data = TaskRead.model_validate(task)
    data.fire_stage = fire_stage(task.deadline_at, now=now)
    data.fire_color = fire_color(task.priority)
    data.day_key = day_key(task.deadline_at, now=now)
    data.is_burned = is_burned(task.deadline_at, task.status, now=now)
    return data


def list_tasks(session: Session, workspace_id: UUID, user: UserContext, *, project_id: UUID | None = None, q: str | None = None) -> list[TaskRead]:
    get_workspace(session, workspace_id, user)
    stmt = select(CrmTask).where(CrmTask.workspace_id == workspace_id)
    if project_id:
        stmt = stmt.where(CrmTask.project_id == project_id)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where((CrmTask.title.ilike(like)) | (CrmTask.description.ilike(like)))
    stmt = stmt.order_by(CrmTask.deadline_at.asc().nulls_last(), CrmTask.created_at.desc())
    return [_task_to_read(task) for task in session.scalars(stmt)]


def get_task(session: Session, workspace_id: UUID, task_id: UUID, user: UserContext) -> CrmTask:
    task = session.get(CrmTask, task_id)
    if not task or task.workspace_id != workspace_id:
        raise NotFoundError("Task not found")
    result = check_permission(session, user_id=user.user_id, action="task.view", target_type="task", target_id=task.id, workspace_id=workspace_id, project_id=task.project_id, is_platform_admin=user.is_platform_admin)
    if not result.allowed:
        raise ForbiddenError("No access to task")
    return task


def _sync_planner(session: Session, task: CrmTask) -> None:
    if not task.deadline_at:
        return
    project = session.get(Project, task.project_id) if task.project_id else None
    company = session.get(Company, task.company_id) if task.company_id else None
    payload = PlannerEventPayload(
        title=task.title,
        description=task.description,
        deadline_at=task.deadline_at,
        calendar_id=project.planner_calendar_id if project else None,
        location=company.address if company else None,
        workspace_id=task.workspace_id,
        project_id=task.project_id,
        crm_task_id=task.id,
    )
    event_id, status = PlannerClient().create_or_update_task_event(payload, task.planner_event_id)
    task.planner_event_id = event_id
    task.planner_sync_status = status


def create_task(session: Session, payload: TaskCreate, user: UserContext, request_id: str | None = None) -> TaskRead:
    get_workspace(session, payload.workspace_id, user)
    result = check_permission(session, user_id=user.user_id, action="task.create", target_type="workspace", target_id=payload.workspace_id, workspace_id=payload.workspace_id, project_id=payload.project_id, is_platform_admin=user.is_platform_admin)
    if not result.allowed:
        raise ForbiddenError("No permission to create task")
    data = payload.model_dump()
    data["priority"] = payload.priority.value
    task = CrmTask(**data, created_by_user_id=user.user_id)
    session.add(task)
    session.flush()
    _sync_planner(session, task)
    log_action(session, actor_user_id=user.user_id, action="task.create", target_type="task", target_id=str(task.id), workspace_id=task.workspace_id, project_id=task.project_id, request_id=request_id)
    session.commit()
    session.refresh(task)
    return _task_to_read(task)


def update_task(session: Session, workspace_id: UUID, task_id: UUID, payload: TaskUpdate, user: UserContext, request_id: str | None = None) -> TaskRead:
    task = get_task(session, workspace_id, task_id, user)
    action = "task.complete" if payload.status and payload.status.value == "done" else "task.edit"
    result = check_permission(session, user_id=user.user_id, action=action, target_type="task", target_id=task.id, workspace_id=workspace_id, project_id=task.project_id, is_platform_admin=user.is_platform_admin)
    if not result.allowed:
        raise ForbiddenError("No permission to update task")
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(task, key, value.value if hasattr(value, "value") else value)
    if task.status == "done" and task.planner_event_id:
        PlannerClient().mark_task_done(task.planner_event_id)
    _sync_planner(session, task)
    log_action(session, actor_user_id=user.user_id, action="task.update", target_type="task", target_id=str(task.id), workspace_id=workspace_id, project_id=task.project_id, metadata=updates, request_id=request_id)
    session.commit()
    session.refresh(task)
    return _task_to_read(task)


def weekly_board(session: Session, workspace_id: UUID, user: UserContext, *, project_id: UUID | None = None, now: datetime | None = None) -> WeeklyBoardRead:
    get_workspace(session, workspace_id, user)
    now = now or datetime.now(timezone.utc)
    week_range = week_range_moscow(now)
    start, end = week_range.start, week_range.end
    stmt = select(CrmTask).where(CrmTask.workspace_id == workspace_id)
    if project_id:
        stmt = stmt.where(CrmTask.project_id == project_id)
    tasks = list(session.scalars(stmt.order_by(CrmTask.sort_order.asc(), CrmTask.created_at.asc())))
    columns: dict[str, list[TaskRead]] = {"burned": [], "monday": [], "tuesday": [], "wednesday": [], "thursday": [], "friday": [], "saturday": [], "sunday": [], "future": [], "backlog": []}
    for task in tasks:
        read = _task_to_read(task, now)
        columns.setdefault(read.day_key, []).append(read)
    return WeeklyBoardRead(week_start=start, week_end=end, columns=columns)
