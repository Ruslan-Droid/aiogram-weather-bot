import logging

from aiogram import Bot
from aiogram.enums import BotCommandScopeType
from aiogram.types import BotCommandScopeChat, CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, ManagedRadio
from fluentogram import TranslatorHub, TranslatorRunner
from taskiq_redis import RedisScheduleSource

from src.bot.keyboards.menu_button import get_main_menu_commands
from src.infrastructure.database.models import UserModel, UserScheduleTask
from src.infrastructure.database.dao import UserRepository

from sqlalchemy.ext.asyncio import AsyncSession

from src.services.scheduler.tasks import update_send_daily_weather_task

logger = logging.getLogger(__name__)


async def set_radio_lang_default(_, dialog_manager: DialogManager):
    locales: list[str] = dialog_manager.middleware_data.get("bot_locales")
    user_row: UserModel = dialog_manager.middleware_data.get("user_row")
    item_id = str(locales.index(user_row.language_code) + 1)
    radio: ManagedRadio = dialog_manager.find("radio_lang")

    await radio.set_checked(item_id)


async def update_user_lang(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager,
):
    bot: Bot = dialog_manager.middleware_data.get("bot")
    translator_hub: TranslatorHub = dialog_manager.middleware_data.get("translator_hub")
    session: AsyncSession = dialog_manager.middleware_data.get("session")
    locales: list[str] = dialog_manager.middleware_data.get("bot_locales")
    radio_lang: ManagedRadio = dialog_manager.find("radio_lang")
    checked_locale = locales[int(radio_lang.get_checked()) - 1]
    i18n: TranslatorRunner = translator_hub.get_translator_by_locale(checked_locale)
    dialog_manager.middleware_data["i18n"] = i18n
    redis_source: RedisScheduleSource = dialog_manager.middleware_data.get("redis_source")

    user_repo: UserRepository = UserRepository(session)
    await user_repo.update_users_language(telegram_id=callback.from_user.id, language_code=checked_locale)

    user_row: UserModel = await user_repo.get_user_by_telegram_id(callback.from_user.id)

    dialog_manager.middleware_data["user_row"] = user_row
    await bot.set_my_commands(
        commands=get_main_menu_commands(i18n=i18n),
        scope=BotCommandScopeChat(
            type=BotCommandScopeType.CHAT, chat_id=callback.from_user.id
        ),
    )

    task_settings: UserScheduleTask = await user_repo.get_user_notification_settings(
        telegram_id=user_row.telegram_id)

    # update task with new city if notification enabled
    if task_settings.notifications_enabled:
        location = (user_row.latitude, user_row.longitude) if user_row.city is None else user_row.city

        await update_send_daily_weather_task(
            source=redis_source,
            time=task_settings.notification_time,
            location=location,
            language=user_row.language_code,
            chat_id=user_row.telegram_id,
            taskiq_task_id=task_settings.taskiq_task_id,
            user_repo=user_repo,
        )

    await callback.answer(text=i18n.lang.saved())
    await callback.message.delete()
    await dialog_manager.done()


async def cancel_set_lang(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager,
) -> None:
    await callback.message.delete()
    await dialog_manager.done()
