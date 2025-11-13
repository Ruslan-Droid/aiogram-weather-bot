import asyncio
import logging

import redis

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage

from aiogram_dialog import setup_dialogs
from aiogram_dialog.api.entities import DIALOG_EVENT_NAME
from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState
from fluentogram import TranslatorHub

from src.bot.dialogs.flows import dialogs
from src.bot.handlers import routers
from src.bot.handlers.errors import on_unknown_intent, on_unknown_state
from src.bot.i18n.translator_hub import create_translator_hub
from src.bot.middlewares.database import DbSessionMiddleware
from src.bot.middlewares.get_user import GetUserMiddleware
from src.bot.middlewares.i18n import TranslatorRunnerMiddleware
from src.bot.middlewares.shadow_ban import ShadowBanMiddleware

from src.infrastructure.database.db import async_session_maker
from src.infrastructure.cache import get_redis_pool

from src.services.weather_api.weather_service import WeatherService
from src.services.delay_service.start_consumer import start_delayed_consumer
from src.services.scheduler.taskiq_broker import broker, redis_source

from nats_broker.nats_connect import connect_to_nats

from config.config import get_config

logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting bot")

    config = get_config()

    nc, js = await connect_to_nats(servers=config.nats.servers)

    redis_client: redis.asyncio.Redis = await get_redis_pool(
        host=config.redis.host,
        port=config.redis.port,
        db=config.redis.database,
        username=config.redis.username,
        password=config.redis.password,
    )

    storage = RedisStorage(
        redis=redis_client,
        key_builder=DefaultKeyBuilder(
            with_destiny=True,
        ),
    )

    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode(config.bot.parse_mode)),
    )
    dp = Dispatcher(storage=storage)

    @dp.startup()
    async def setup_taskiq(bot: Bot, *_args, **_kwargs):
        if not broker.is_worker_process:
            try:
                logging.info("Setting up taskiq")
                await broker.startup()
                logging.info("Taskiq started successfully")
            except Exception as e:
                logging.error(f"Failed to start taskiq: {e}")
                raise  # Перебрасываем исключение, чтобы бот не стартовал

    @dp.shutdown()
    async def shutdown_taskiq(bot: Bot, *_args, **_kwargs):
        if not broker.is_worker_process:
            logging.info("Shutting down taskiq")
            await broker.shutdown()

    cache_pool: redis.asyncio.Redis = redis_client

    translator_hub: TranslatorHub = create_translator_hub()

    weather_service: WeatherService = WeatherService(
        api_key=config.weather.token,
        base_url=config.weather.base_url,
    )

    dp.workflow_data.update(
        bot_locales=sorted(config.i18n.locales),
        translator_hub=translator_hub,
        _cache_pool=cache_pool,
        weather_service=weather_service,
        redis_source=redis_source,
    )
    logger.info("Registering error handlers")
    dp.errors.register(
        on_unknown_intent,
        ExceptionTypeFilter(UnknownIntent),
    )
    dp.errors.register(
        on_unknown_state,
        ExceptionTypeFilter(UnknownState),
    )

    logger.info("Including routers")
    dp.include_routers(*routers)

    logger.info("Including dialogs")
    dp.include_routers(*dialogs)

    logger.info("Including middlewares")
    dp.update.middleware(DbSessionMiddleware(async_session_maker))
    dp.update.middleware(GetUserMiddleware())
    dp.update.middleware(ShadowBanMiddleware())
    dp.update.middleware(TranslatorRunnerMiddleware())

    logger.info("Including error middlewares")
    dp.errors.middleware(DbSessionMiddleware(async_session_maker))
    dp.errors.middleware(GetUserMiddleware())
    dp.errors.middleware(ShadowBanMiddleware())
    dp.errors.middleware(TranslatorRunnerMiddleware())

    logger.info("Setting up dialogs")
    bg_factory = setup_dialogs(dp)

    logger.info("Including observers middlewares")
    dp.observers[DIALOG_EVENT_NAME].outer_middleware(DbSessionMiddleware(async_session_maker))
    dp.observers[DIALOG_EVENT_NAME].outer_middleware(GetUserMiddleware())
    dp.observers[DIALOG_EVENT_NAME].outer_middleware(ShadowBanMiddleware())
    dp.observers[DIALOG_EVENT_NAME].outer_middleware(TranslatorRunnerMiddleware())

    # Launch polling and delayed message consumer
    try:
        await asyncio.gather(
            dp.start_polling(
                bot,
                js=js,
                delay_del_subject=config.nats.delayed_consumer_subject,
                bg_factory=bg_factory,
            ),
            start_delayed_consumer(
                nc=nc,
                js=js,
                bot=bot,
                subject=config.nats.delayed_consumer_subject,
                stream=config.nats.delayed_consumer_stream,
                durable_name=config.nats.delayed_consumer_durable_name,
            ),
        )
    except Exception as e:
        logger.exception(e)
    finally:
        await nc.close()
        logger.info("Connection to NATS closed")
        await cache_pool.close()
        logger.info("Connection to Redis closed")
