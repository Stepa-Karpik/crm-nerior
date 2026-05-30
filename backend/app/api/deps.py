from __future__ import annotations

from uuid import UUID, uuid4
from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.schemas.common import UserContext


def get_db(session: Session = Depends(get_session)) -> Session:
    return session


def get_current_user(
    x_user_id: str | None = Header(default=None),
    x_username: str | None = Header(default=None),
    x_display_name: str | None = Header(default=None),
    x_user_email: str | None = Header(default=None),
    x_platform_admin: str | None = Header(default=None),
) -> UserContext:
    user_id = UUID(x_user_id) if x_user_id else UUID("00000000-0000-0000-0000-000000000001")
    return UserContext(user_id=user_id, username=x_username or "karpik", display_name=x_display_name or x_username or "karpik", email=x_user_email, is_platform_admin=x_platform_admin == "1")


def get_request_id(x_request_id: str | None = Header(default=None)) -> str:
    return x_request_id or str(uuid4())
