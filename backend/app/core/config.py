from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    project_name: str = "Nerior CRM"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./crm.db"
    identity_cookie_domain: str = ".nerior.ru"
    auth_login_url: str = "https://auth.nerior.ru/login"
    identity_internal_url: str = "http://127.0.0.1:8100/api/v1"
    allow_dev_auth: bool = True
    planner_internal_url: str = "http://127.0.0.1:8000/api/v1"
    documents_internal_url: str = "http://127.0.0.1:8200/api/v1"
    internal_api_key: str = ""
    cors_origins: list[str] = ["https://crm.nerior.ru", "https://planner.nerior.ru", "https://documents.nerior.ru", "https://admin.nerior.ru", "http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
