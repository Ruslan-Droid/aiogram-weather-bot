import logging

from typing import Any
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class RedisService:
    def __init__(self, redis_pool: Redis):
        self.redis_pool = redis_pool

    async def set_key(self, key: str, value: Any) -> None:
        try:
            await self.redis_pool.set(key, value)
            logger.debug("Set key %s", key)
        except Exception as e:
            logger.error("Failed to set key %s to %s", key, e)
            raise

    async def set_key_with_ttl(self, key: str, ttl: int, value: Any, ) -> None:
        try:
            await self.redis_pool.setex(key, ttl, value)
            logger.debug("Set key %s and ttl %s", key, ttl)
        except Exception as e:
            logger.error("Failed to set key %s to %s", key, e)
            raise

    async def get_key(self, key: str) -> Any:
        try:
            value = await self.redis_pool.get(key)
            if value is None:
                logger.debug("Value is empty for key: %s", key)
                return None
            logger.debug("Get value for key %s successful", key)
            return value
        except Exception as e:
            logger.error("Failed to get key %s", key)
            raise

    async def delete_key(self, key: str) -> None:
        try:
            await self.redis_pool.delete(key)
            logger.debug("Successful deleted key %s", key)
        except Exception as e:
            logger.error("Failed to delete key %s", key)
            raise
