from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi.testclient import TestClient

from app.core.db import Base, engine
from app.main import app

client = TestClient(app)
HEADERS = {"x-user-id": "00000000-0000-0000-0000-000000000001", "x-username": "karpik", "x-display-name": "karpik"}


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_workspace_project_task_weekly_flow():
    workspace = client.post("/api/v1/workspaces", json={"name": "Nerior Workspace"}, headers=HEADERS).json()
    workspace_id = workspace["id"]

    project = client.post(f"/api/v1/workspaces/{workspace_id}/projects", json={"name": "CRM launch"}, headers=HEADERS).json()
    project_id = project["id"]

    task = client.post(
        f"/api/v1/workspaces/{workspace_id}/tasks",
        json={
            "workspace_id": workspace_id,
            "project_id": project_id,
            "title": "Подготовить договор",
            "description": "Согласовать с клиентом",
            "priority": "high",
            "deadline_at": "2026-06-01T12:00:00+03:00",
        },
        headers=HEADERS,
    ).json()

    assert UUID(task["id"])
    assert task["planner_sync_status"] == "synced"
    assert task["fire_color"] == "red-orange"

    board = client.get(f"/api/v1/workspaces/{workspace_id}/tasks/weekly", headers=HEADERS).json()
    assert "columns" in board
    assert any(item["title"] == "Подготовить договор" for items in board["columns"].values() for item in items)


def test_non_member_cannot_read_workspace():
    workspace = client.post("/api/v1/workspaces", json={"name": "Private"}, headers=HEADERS).json()
    other = {"x-user-id": "00000000-0000-0000-0000-000000000099", "x-username": "guest"}
    response = client.get(f"/api/v1/workspaces/{workspace['id']}", headers=other)
    assert response.status_code == 403
