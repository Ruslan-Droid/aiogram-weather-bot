import logging

from taskiq import TaskiqEvents, TaskiqScheduler, TaskiqState
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_nats import NatsBroker
from taskiq_redis import RedisAsyncResultBackend, RedisScheduleSource

from config.config import get_config

config = get_config()

redis_url = f"redis://{config.redis.username}:{config.redis.password}@{config.redis.host}:{config.redis.port}/{config.redis.db}"

broker = NatsBroker(servers=config.nats.servers, queue="taskiq_tasks").with_result_backend(
    RedisAsyncResultBackend(redis_url=redis_url))

redis_source = RedisScheduleSource(
    url=redis_url
)

scheduler = TaskiqScheduler(broker, [redis_source, LabelScheduleSource(broker)])


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup(state: TaskiqState) -> None:
    logging.basicConfig(level=config.logs.level_name, format=config.logs.format)
    logger = logging.getLogger(__name__)
    logger.info("Starting scheduler...")

    state.logger = logger


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def shutdown(state: TaskiqState) -> None:
    state.logger.info("Scheduler stopped")
