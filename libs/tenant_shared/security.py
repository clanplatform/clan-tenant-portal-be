from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        secret_key: str,
        algorithm: str = "HS256",
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=1))
        to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
        return jwt.encode(to_encode, secret_key, algorithm=algorithm)

    @staticmethod
    def decode_access_token(
        token: str,
        secret_key: str,
        algorithm: str = "HS256",
        audience: Optional[str] = None,
        issuer: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        try:
            options = {}
            kwargs: Dict[str, Any] = {"algorithms": [algorithm]}
            if audience:
                kwargs["audience"] = audience
            if issuer:
                kwargs["issuer"] = issuer
            return jwt.decode(token, secret_key, **kwargs)
        except JWTError:
            return None
