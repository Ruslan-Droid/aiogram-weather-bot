import logging

from typing import Any
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


async def set_key(redis_pool: Redis, key: str, value: Any) -> None:
    try:
        await redis_pool.set(key, value)
        logger.info("Set key %s to %s", key, value)
    except Exception as e:
        logger.error("Failed to set key %s to %s", key, e)
        raise


async def set_key_with_ttl(redis_pool: Redis, key: str, ttl: int, value: Any, ) -> None:
    try:
        await redis_pool.setex(key, ttl, value)
        logger.info("Set key %s to %s and ttl %s", key, value, ttl)
    except Exception as e:
        logger.error("Failed to set key %s to %s", key, e)
        raise


async def get_key(redis_pool: Redis, key: str) -> Any:
    try:
        value = await redis_pool.get(key)
        if value is None:
            logger.error("Value is empty for key: %s", key)
            raise
    except Exception as e:
        logger.error("Failed to get key %s", key)
        raise


async def delete_key(redis_pool: Redis, key: str) -> None:
    try:
        await redis_pool.delete(key)
        logger.info("Successful deleted key %s", key)
    except Exception as e:
        logger.error("Failed to delete key %s", key)
        raise
