import json
import logging
from typing import Optional, Any
import redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache client with graceful degradation.

    All methods silently handle Redis unavailability so the service
    can operate without a running Redis instance (cache simply misses).
    """

    def __init__(self, url: str):
        self._url = url
        self._client: Optional[redis.Redis] = None
        self._available = False
        self._connect()

    def _connect(self) -> None:
        try:
            self._client = redis.from_url(self._url, decode_responses=True, socket_connect_timeout=2)
            self._client.ping()
            self._available = True
            logger.info("Redis connected at %s", self._url)
        except Exception as exc:
            self._available = False
            logger.warning("Redis unavailable, caching disabled: %s", exc)

    @property
    def available(self) -> bool:
        return self._available

    def get(self, key: str) -> Optional[Any]:
        if not self._available or self._client is None:
            return None
        try:
            raw = self._client.get(key)
            if raw is None:
                return None
            return json.loads(raw)
        except Exception as exc:
            logger.debug("Redis GET failed for key %s: %s", key, exc)
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        if not self._available or self._client is None:
            return False
        try:
            self._client.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception as exc:
            logger.debug("Redis SET failed for key %s: %s", key, exc)
            return False

    def delete(self, key: str) -> bool:
        if not self._available or self._client is None:
            return False
        try:
            self._client.delete(key)
            return True
        except Exception as exc:
            logger.debug("Redis DELETE failed for key %s: %s", key, exc)
            return False

    def delete_pattern(self, pattern: str) -> int:
        if not self._available or self._client is None:
            return 0
        try:
            keys = self._client.keys(pattern)
            if keys:
                return self._client.delete(*keys)
            return 0
        except Exception as exc:
            logger.debug("Redis DELETE PATTERN failed for %s: %s", pattern, exc)
            return 0

    def ping(self) -> bool:
        if self._client is None:
            return False
        try:
            self._client.ping()
            self._available = True
            return True
        except Exception:
            self._available = False
            return False


# Global singleton
redis_cache = RedisCache(url=settings.REDIS_URL)
