from fastapi import APIRouter
from app.api.v1.routes import app_config, integrations, api_keys, webhooks

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(app_config.router)
api_v1_router.include_router(integrations.router)
api_v1_router.include_router(api_keys.router)
api_v1_router.include_router(webhooks.router)
