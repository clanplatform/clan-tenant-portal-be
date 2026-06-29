import json
import logging
from typing import Any, Optional

import redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    def __init__(self) -> None:
        self._client: Optional[redis.Redis] = None
        self._available: bool = False
        self._connect()

    def _connect(self) -> None:
        try:
            self._client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            self._client.ping()
            self._available = True
            logger.info("Redis connected successfully")
        except Exception as e:
            self._available = False
            logger.warning(f"Redis unavailable — cache disabled: {e}")

    def ping(self) -> bool:
        if not self._client:
            raise ConnectionError("Redis client not initialized")
        self._client.ping()
        return True

    def get(self, key: str) -> Optional[Any]:
        if not self._available or not self._client:
            return None
        try:
            value = self._client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception as e:
            logger.warning(f"Redis GET error for key '{key}': {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        if not self._available or not self._client:
            return False
        try:
            serialized = json.dumps(value, default=str)
            self._client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.warning(f"Redis SET error for key '{key}': {e}")
            return False

    def delete(self, key: str) -> bool:
        if not self._available or not self._client:
            return False
        try:
            self._client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Redis DELETE error for key '{key}': {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        if not self._available or not self._client:
            return 0
        try:
            keys = self._client.keys(pattern)
            if keys:
                return self._client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Redis DELETE PATTERN error for '{pattern}': {e}")
            return 0

    @property
    def is_available(self) -> bool:
        return self._available


redis_cache = RedisCache()
