import json
import logging
from typing import Any, Optional

import redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """
    Redis cache wrapper with graceful degradation.
    If Redis is unavailable, all operations are no-ops and return None/False.
    """

    def __init__(self) -> None:
        self._client: Optional[redis.Redis] = None
        self._available: bool = False
        self._connect()

    def _connect(self) -> None:
        try:
            self._client = redis.Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            self._available = True
        except Exception as exc:
            logger.warning(f"Redis connection failed during init: {exc}")
            self._available = False

    def ping(self) -> bool:
        """Check if Redis is reachable. Raises on failure (for lifespan health check)."""
        if self._client is None:
            raise RuntimeError("Redis client not initialized")
        result = self._client.ping()
        self._available = True
        return result

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Store a value in Redis. Value is JSON-serialised.
        Returns True on success, False if Redis is unavailable.
        """
        if not self._available or self._client is None:
            return False
        try:
            serialised = json.dumps(value)
            if ttl:
                self._client.setex(key, ttl, serialised)
            else:
                self._client.set(key, serialised)
            return True
        except Exception as exc:
            logger.warning(f"Redis SET failed for key '{key}': {exc}")
            self._available = False
            return False

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from Redis. Returns the deserialised object or None.
        """
        if not self._available or self._client is None:
            return None
        try:
            raw = self._client.get(key)
            if raw is None:
                return None
            return json.loads(raw)
        except Exception as exc:
            logger.warning(f"Redis GET failed for key '{key}': {exc}")
            self._available = False
            return None

    def delete(self, key: str) -> bool:
        """
        Delete a key from Redis. Returns True on success.
        """
        if not self._available or self._client is None:
            return False
        try:
            self._client.delete(key)
            return True
        except Exception as exc:
            logger.warning(f"Redis DELETE failed for key '{key}': {exc}")
            self._available = False
            return False

    def exists(self, key: str) -> bool:
        """
        Check whether a key exists in Redis.
        """
        if not self._available or self._client is None:
            return False
        try:
            return bool(self._client.exists(key))
        except Exception as exc:
            logger.warning(f"Redis EXISTS failed for key '{key}': {exc}")
            self._available = False
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a glob pattern. Returns the count deleted.
        """
        if not self._available or self._client is None:
            return 0
        try:
            keys = self._client.keys(pattern)
            if not keys:
                return 0
            return self._client.delete(*keys)
        except Exception as exc:
            logger.warning(f"Redis DELETE_PATTERN failed for pattern '{pattern}': {exc}")
            self._available = False
            return 0


# Global singleton
redis_cache = RedisCache()
