import asyncio
import logging
import redis

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import ChatAdministratorRights

from aiogram_dialog import setup_dialogs
from aiogram_dialog.api.entities import DIALOG_EVENT_NAME
from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState
from aiohttp import web
from fluentogram import TranslatorHub
from nats_broker.nats_connect import connect_to_nats
from src.bot.app_factory import create_aiohttp_app, on_startup

from src.bot.dialogs.flows import dialogs
from src.bot.handlers import routers, commands_router, user_status_router, groups_router
from src.bot.handlers.errors import on_unknown_intent, on_unknown_state
from src.bot.middlewares.database import DbSessionMiddleware
from src.bot.middlewares.get_user import GetUserMiddleware
from src.bot.middlewares.get_group import GetGroupMiddleware
from src.bot.middlewares.i18n import TranslatorRunnerMiddleware
from src.bot.middlewares.shadow_ban import ShadowBanMiddleware

from src.infrastructure.database.db import async_session_maker
from src.infrastructure.cache import get_redis_pool

from src.services.weather_api.weather_service import WeatherService
from src.services.open_street_map_api.city_service import CityService
from src.services.delay_service.start_consumer import start_delayed_consumer
from src.services.scheduler.taskiq_broker import broker, redis_source
from src.services.i18n.translator_hub import TranslatorHubFactory

from config.config import get_config

logger = logging.getLogger(__name__)


async def setup_bot_admin_rights(bot: Bot) -> None:
    logger.info("Setting default bot admin rights")
    bot_rights = ChatAdministratorRights(
        is_anonymous=False,
        can_manage_chat=True,
        can_delete_messages=True,
        can_manage_video_chats=False,
        can_restrict_members=False,
        can_promote_members=False,
        can_change_info=False,
        can_invite_users=False,
        can_post_stories=False,
        can_edit_stories=False,
        can_delete_stories=False,
    )
    await bot.set_my_default_administrator_rights(rights=bot_rights, for_channels=False)


async def main():
    config = get_config()

    nc, js = await connect_to_nats(servers=config.nats.servers)

    redis_client: redis.asyncio.Redis = await get_redis_pool(
        host=config.redis.host,
        port=config.redis.port,
        db=config.redis.database,
        username=config.redis.username,
        password=config.redis.password,
    )

    bot = Bot(token=config.bot.token,
              default=DefaultBotProperties(parse_mode=ParseMode(config.bot.parse_mode)))

    await setup_bot_admin_rights(bot=bot)

    storage = RedisStorage(
        redis=redis_client,
        key_builder=DefaultKeyBuilder(
            with_destiny=True,
        ),
    )

    dp = Dispatcher(storage=storage)

    cache_pool: redis.asyncio.Redis = redis_client

    translator_hub: TranslatorHub = TranslatorHubFactory(config=config).create()

    weather_service: WeatherService = WeatherService(
        api_key=config.weather.token,
        base_url=config.weather.base_url,
    )
    city_service: CityService = CityService(base_url=config.open_street_map.base_url)

    dp.workflow_data.update(
        bot_locales=sorted(config.i18n.locales),
        translator_hub=translator_hub,
        _cache_pool=cache_pool,
        weather_service=weather_service,
        city_service=city_service,
        redis_source=redis_source,
        js=js,
        delay_del_subject=config.nats.delayed_consumer_subject,
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

    logger.info("Setting up middlewares for private routers")
    private_middlewares = [
        DbSessionMiddleware(async_session_maker),
        GetUserMiddleware(),
        ShadowBanMiddleware(),
        TranslatorRunnerMiddleware(),
    ]

    logger.info("Including private chat middlewares")
    for middleware in private_middlewares:
        commands_router.message.middleware(middleware)
        commands_router.callback_query.middleware(middleware)
        user_status_router.my_chat_member.middleware(middleware)

        for dialog in dialogs:
            dialog.message.middleware(middleware)
            dialog.callback_query.middleware(middleware)

    logger.info("Including groups middlewares")
    groups_router.chat_member.middleware(DbSessionMiddleware(async_session_maker))
    groups_router.chat_member.middleware(GetUserMiddleware())
    groups_router.chat_member.middleware(GetGroupMiddleware())
    groups_router.chat_member.middleware(TranslatorRunnerMiddleware())

    groups_router.my_chat_member.middleware(DbSessionMiddleware(async_session_maker))
    groups_router.my_chat_member.middleware(GetUserMiddleware())
    groups_router.my_chat_member.middleware(GetGroupMiddleware())
    groups_router.my_chat_member.middleware(TranslatorRunnerMiddleware())

    logger.info("Including routers")
    dp.include_routers(*routers)

    logger.info("Including dialogs")
    dp.include_routers(*dialogs)

    logger.info("Including error middlewares")
    dp.errors.middleware(DbSessionMiddleware(async_session_maker))
    dp.errors.middleware(GetUserMiddleware())
    dp.errors.middleware(ShadowBanMiddleware())
    dp.errors.middleware(TranslatorRunnerMiddleware())

    logger.info("Setting up dialogs")
    bg_factory = setup_dialogs(dp)
    dp.workflow_data.update(bg_factory=bg_factory)

    logger.info("Including observers middlewares")
    dp.observers[DIALOG_EVENT_NAME].outer_middleware(DbSessionMiddleware(async_session_maker))
    dp.observers[DIALOG_EVENT_NAME].outer_middleware(GetUserMiddleware())
    dp.observers[DIALOG_EVENT_NAME].outer_middleware(ShadowBanMiddleware())
    dp.observers[DIALOG_EVENT_NAME].outer_middleware(TranslatorRunnerMiddleware())

    if not broker.is_worker_process:
        logger.info("Starting taskiq broker")
        await broker.startup()

    logger.info("Creating web app")
    app = create_aiohttp_app(dp=dp, bot=bot, config=config)

    delayed_consumer_task = None
    runner = None

    try:
        await on_startup(bot=bot, config=config, dp=dp)
        delayed_consumer_task = asyncio.create_task(
            start_delayed_consumer(
                nc=nc,
                js=js,
                bot=bot,
                subject=config.nats.delayed_consumer_subject,
                stream=config.nats.delayed_consumer_stream,
                durable_name=config.nats.delayed_consumer_durable_name,
            )
        )

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(
            runner,
            config.webhook.WEB_SERVER_HOST,
            config.webhook.WEB_SERVER_PORT
        )
        await site.start()
        logger.info("Webhook server started on %s: %s", config.webhook.WEB_SERVER_HOST, config.webhook.WEB_SERVER_PORT)
        logger.info("Webhook URL: %s%s", config.webhook.WEBHOOK_BASE_URL, config.webhook.WEBHOOK_PATH)

        await asyncio.Future()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.exception(e)
    finally:
        if delayed_consumer_task:
            delayed_consumer_task.cancel()
            logger.info("delayed_consumer_task cancelled")
        if runner:
            await runner.cleanup()
            logger.info("runner cleaned up")
        await bot.session.close()
        logger.info("Bot session closed")
        await nc.close()
        logger.info("Connection to NATS closed")
        await cache_pool.close()
        logger.info("Connection to Redis closed")
        if not broker.is_worker_process:
            logger.info("Connection to taskiq-broker closed")
            await broker.shutdown()
