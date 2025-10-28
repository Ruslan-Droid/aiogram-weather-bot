from redis.asyncio import Redis
from config.config import get_config

config = get_config()

redis_connection = Redis(
    host=config.redis.host,
    port=config.redis.port,
    db=config.redis.database,
    username=config.redis.username,
    password=config.redis.password
)
