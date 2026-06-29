from fastapi import APIRouter

from app.api.v1.routes.invoices import router as invoices_router
from app.api.v1.routes.plans import router as plans_router
from app.api.v1.routes.subscriptions import router as subscriptions_router
from app.api.v1.routes.usage import router as usage_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(plans_router)
api_v1_router.include_router(subscriptions_router)
api_v1_router.include_router(usage_router)
api_v1_router.include_router(invoices_router)
