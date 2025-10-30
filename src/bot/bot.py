import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
# from aiogram.filters import ExceptionTypeFilter
from aiogram_dialog import setup_dialogs
from aiogram_dialog.api.entities import DIALOG_EVENT_NAME
# from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState
from fluentogram import TranslatorHub

from src.bot.dialogs.flows import dialogs
from src.bot.handlers import routers
from src.bot.i18n.translator_hub import create_translator_hub
from src.bot.middlewares.database import DbSessionMiddleware
from src.bot.middlewares.get_user import GetUserMiddleware
from src.bot.middlewares.i18n import TranslatorRunnerMiddleware
from src.bot.middlewares.shadow_ban import ShadowBanMiddleware

from src.infrastructure.database.db import async_session_maker

from config.config import get_config

logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting bot")

    config = get_config()

    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode(config.bot.parse_mode)),
    )
    dp = Dispatcher()

    translator_hub: TranslatorHub = create_translator_hub()

    dp.workflow_data.update(
        bot_locales=sorted(config.i18n.locales),
        translator_hub=translator_hub,
    )

    # logger.info("Registering error handlers")
    # dp.errors.register(
    #     on_unknown_intent,
    #     ExceptionTypeFilter(UnknownIntent),
    # )
    # dp.errors.register(
    #     on_unknown_state,
    #     ExceptionTypeFilter(UnknownState),
    # )
    #
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
    # finally:
    #     if dp.workflow_data.get("_cache_pool"):
    #         await cache_pool.close()
    #         logger.info("Connection to Redis closed")
