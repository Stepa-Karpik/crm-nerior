from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import admin, crm, integrations, projects, tasks, workspaces

api_router = APIRouter()
api_router.include_router(workspaces.router)
api_router.include_router(projects.router)
api_router.include_router(tasks.router)
api_router.include_router(crm.router)
api_router.include_router(integrations.router)
api_router.include_router(admin.router)
