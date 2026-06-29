from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "tenant-app-config-service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql://postgres:postgres123@localhost:5432/tenant_app_config"
    REDIS_URL: str = "redis://localhost:6379/0"
    JWT_ALGORITHM: str = "RS256"
    JWT_PUBLIC_KEY: str = ""
    JWT_ISSUER: str = "clan-identity"
    JWT_AUDIENCE: str = "api-gateway"
    SECRET_KEY: str = "dev-secret-key"
    INTERNAL_API_KEY: str = "dev-internal-key"

    model_config = {"env_file": ".env", "case_sensitive": True, "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
