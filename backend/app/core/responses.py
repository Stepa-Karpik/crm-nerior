from __future__ import annotations

from datetime import datetime, timezone
from fastapi import Request


def success_response(*, data=None, request: Request | None = None, pagination: dict | None = None):
    meta = {"server_time": datetime.now(timezone.utc).isoformat()}
    if request is not None:
        meta["request_id"] = getattr(request.state, "request_id", None)
    if pagination:
        meta["pagination"] = pagination
    return {"data": data, "meta": meta, "error": None}


def error_response(code: str, message: str, details: dict | None = None, request: Request | None = None):
    meta = {"server_time": datetime.now(timezone.utc).isoformat()}
    if request is not None:
        meta["request_id"] = getattr(request.state, "request_id", None)
    return {"data": None, "meta": meta, "error": {"code": code, "message": message, "details": details or {}}}
