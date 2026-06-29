import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.infrastructure.database.session import create_tables
from app.infrastructure.redis_cache.redis_cache import redis_cache

# Import all models so SQLAlchemy registers them with Base.metadata
import app.subscription_plans.models.subscription_plan  # noqa: F401
import app.tenant_subscriptions.models.tenant_subscription  # noqa: F401
import app.usage_records.models.usage_record  # noqa: F401
import app.invoices.models.invoice  # noqa: F401

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting tenant-billing-service...")

    try:
        create_tables()
        logger.info("Database tables created / verified")
    except Exception as e:
        logger.error(f"DB init error: {e}")

    try:
        redis_cache.ping()
        logger.info("Redis connection verified")
    except Exception as e:
        logger.warning(f"Redis unavailable: {e}")

    yield

    logger.info("Shutting down tenant-billing-service...")


app = FastAPI(
    title="Tenant Billing Service",
    version="1.0.0",
    description="Multi-tenant SaaS billing microservice managing plans, subscriptions, usage, and invoices",
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


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "tenant-billing-service",
        "version": "1.0.0",
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "service": "tenant-billing-service",
        "version": "1.0.0",
        "docs": "/docs",
    }
