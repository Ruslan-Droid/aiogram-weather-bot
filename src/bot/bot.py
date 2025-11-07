import asyncio
import logging

import redis

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_dialog import setup_dialogs
from aiogram_dialog.api.entities import DIALOG_EVENT_NAME
from fluentogram import TranslatorHub

from src.bot.dialogs.flows import dialogs
from src.bot.handlers import routers
from src.bot.i18n.translator_hub import create_translator_hub
from src.bot.middlewares.database import DbSessionMiddleware
from src.bot.middlewares.get_user import GetUserMiddleware
from src.bot.middlewares.i18n import TranslatorRunnerMiddleware
from src.bot.middlewares.shadow_ban import ShadowBanMiddleware

from src.infrastructure.database.db import async_session_maker
from src.infrastructure.cache import get_redis_pool

from src.services.weather_api.weather_service import WeatherService

from config.config import get_config

logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting bot")

    config = get_config()

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
                bg_factory=bg_factory,
            )
        )
    except Exception as e:
        logger.exception(e)
    finally:
        await cache_pool.close()
        logger.info("Connection to Redis closed")
