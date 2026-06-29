from fastapi import Header, HTTPException, status
from jose import jwt, JWTError
from typing import Optional
from app.core.config import settings


def get_current_user(
    authorization: Optional[str] = Header(None),
    x_internal_key: Optional[str] = Header(None, alias="x-internal-key"),
    x_tenant_id: Optional[str] = Header(None, alias="x-tenant-id"),
) -> dict:
    """
    Validate JWT bearer token or internal service-to-service key.
    Returns a dict with user_id, tenant_id, role, and claims.
    """
    # Internal service-to-service calls
    if x_internal_key and x_internal_key == settings.INTERNAL_API_KEY:
        return {"user_id": "internal", "tenant_id": x_tenant_id, "role": "internal"}

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization[7:]
    try:
        if settings.JWT_ALGORITHM == "RS256" and settings.JWT_PUBLIC_KEY:
            payload = jwt.decode(
                token,
                settings.JWT_PUBLIC_KEY,
                algorithms=["RS256"],
                audience=settings.JWT_AUDIENCE,
                issuer=settings.JWT_ISSUER,
            )
        else:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        user_id = payload.get("sub") or payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        return {
            "user_id": user_id,
            "tenant_id": payload.get("tenant_id") or x_tenant_id,
            "role": payload.get("role", "user"),
            "claims": payload,
        }
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )
