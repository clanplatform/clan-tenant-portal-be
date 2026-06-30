"""
HTTP client for platform-domain-be / admin-service.

Call sync_to_admin() after every successful Tenant CREATE, UPDATE, or status change.
Failures are always swallowed — a sync error must never roll back the caller.
Use asyncio.create_task(sync_to_admin(...)) for true fire-and-forget.
"""
import logging
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


async def sync_to_admin(
    *,
    portal_tenant_id: str,
    admin_tenant_id: Optional[str] = None,
    name: str,
    slug: str,
    contact_email: Optional[str] = None,
    contact_phone: Optional[str] = None,
    status: str = "active",
    subscription_plan: Optional[str] = None,
) -> None:
    """
    Push tenant data to platform-domain-be so its Tenant record stays in sync.
    Called after Tenant CREATE, UPDATE, and status changes. Fire-and-forget.
    Callers: asyncio.create_task(sync_to_admin(...))
    """
    try:
        async with httpx.AsyncClient(timeout=3.0) as http:
            resp = await http.post(
                f"{settings.ADMIN_SERVICE_URL}/api/v1/sync/tenants",
                headers={"x-internal-key": settings.INTERNAL_API_KEY},
                json={
                    "portal_tenant_id":  portal_tenant_id,
                    "admin_tenant_id":   admin_tenant_id,
                    "name":              name,
                    "slug":              slug,
                    "contact_email":     contact_email,
                    "contact_phone":     contact_phone,
                    "status":            status,
                    "subscription_plan": subscription_plan,
                },
            )
            if resp.status_code not in (200, 201):
                logger.warning(
                    "[admin-sync] unexpected status %s for portal tenant %s",
                    resp.status_code,
                    portal_tenant_id,
                )
    except Exception as exc:
        logger.error("[admin-sync] sync_to_admin failed for %s: %s", portal_tenant_id, exc)
