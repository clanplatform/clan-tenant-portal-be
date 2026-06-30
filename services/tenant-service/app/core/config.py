from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "tenant-service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql://postgres:postgres123@localhost:5432/tenant_service"
    REDIS_URL: str = "redis://localhost:6379/0"
    JWT_ALGORITHM: str = "RS256"
    JWT_PUBLIC_KEY: str = ""
    JWKS_URI: str = ""
    JWT_ISSUER: str = "clan-identity"
    JWT_AUDIENCE: str = "api-gateway"
    SECRET_KEY: str = "dev-secret-key"  # fallback HS256 for dev
    INTERNAL_API_KEY: str = "dev-internal-key"
    CORS_ORIGINS: str = "*"

    # Admin-service (platform-domain-be) — inbound sync target
    ADMIN_SERVICE_URL: str = "http://admin-service:8000"

    model_config = {"env_file": ".env", "case_sensitive": True, "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
