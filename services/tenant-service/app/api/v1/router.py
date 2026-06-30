from fastapi import APIRouter

from app.api.v1.routes import tenants, tenant_settings, tenant_domains, feature_flags
from app.api.v1.routes.sync import router as sync_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(tenants.router)
api_v1_router.include_router(tenant_settings.router)
api_v1_router.include_router(tenant_domains.router)
api_v1_router.include_router(feature_flags.router)
api_v1_router.include_router(sync_router)
