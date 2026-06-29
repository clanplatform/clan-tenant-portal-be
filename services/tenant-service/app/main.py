import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.infrastructure.database.session import check_db_connection, create_tables
from app.infrastructure.redis_cache.redis_cache import redis_cache
from app.api.v1.router import api_v1_router

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        create_tables()
        logger.info("Database tables ready")
    except Exception as e:
        logger.error(f"DB init error: {e}")

    try:
        redis_cache.ping()
        logger.info("Redis connected")
    except Exception as e:
        logger.warning(f"Redis unavailable (non-fatal): {e}")

    yield

    # Shutdown
    logger.info("Shutting down tenant-service")


app = FastAPI(
    title="Tenant Service",
    description="Multi-tenant SaaS platform — Tenant management microservice",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router)


@app.get("/health", tags=["health"])
async def health_check():
    db_ok = check_db_connection()
    return {
        "status": "healthy" if db_ok else "degraded",
        "service": "tenant-service",
        "version": settings.APP_VERSION,
        "database": "healthy" if db_ok else "unhealthy",
    }
