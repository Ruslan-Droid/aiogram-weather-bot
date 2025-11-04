import logging

from redis.asyncio import ConnectionPool, Redis

logger = logging.getLogger(__name__)


async def get_redis_pool(
        db: int,
        host: str,
        port: int,
        username: str,
        password: str,
) -> Redis:
    redis_pool: Redis = Redis(
        connection_pool=ConnectionPool(
            host=host, port=port, db=db, username=username, password=password
        ),
        decode_responses=True
    )

    version = await redis_pool.info("server")
    logger.info("Connected to Redis, %s", version["redis_version"])

    return redis_pool
