import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from config.config import AppConfig

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot, dp, config: AppConfig) -> None:
    me = await bot.get_me()
    logger.warning("starting bot %s", me.username)

    wh_info = await bot.get_webhook_info()
    url = f"{config.webhook.WEBHOOK_BASE_URL}{config.webhook.WEBHOOK_PATH}"

    if wh_info.url: #!= url:
        logger.info("Webhook config changed. Reconfiguring from %s to %s", wh_info.url, url)
        if wh_info.url:
            await bot.delete_webhook(drop_pending_updates=False)

        await bot.set_webhook(
            url=url,
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=False
        )
        logger.info("Successfully set webhook %s", wh_info)
    else:
        logger.info("Webhook already set correctly: %s", wh_info)


def create_aiohttp_app(
        dp: Dispatcher,
        bot: Bot,
        config: AppConfig,
) -> web.Application:
    app = web.Application()

    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_handler.register(app, path=config.webhook.WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    return app
