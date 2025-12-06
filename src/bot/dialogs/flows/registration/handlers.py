import logging

from aiogram_dialog.widgets.input import MessageInput
from aiogram.types import Message
from aiogram_dialog.api.protocols.manager import DialogManager
from aiogram_dialog.api.entities import ShowMode, Stack

from src.bot.dialogs.flows.weather.states import WeatherSG
from src.infrastructure.database.dao import UserRepository
from src.infrastructure.database.models import UserModel, DailyUserTaskModel
from src.services.scheduler.tasks import update_send_daily_weather_task

from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession
from taskiq_redis import RedisScheduleSource

logger = logging.getLogger(__name__)


async def location_handler(
        message: Message,
        widget: MessageInput,
        dialog_manager: DialogManager) -> None:
    session: AsyncSession = dialog_manager.middleware_data.get('session')
    i18n: TranslatorRunner = dialog_manager.middleware_data.get("i18n")
    redis_source: RedisScheduleSource = dialog_manager.middleware_data.get("redis_source")
    user: UserModel = dialog_manager.middleware_data.get("user_row")

    user_rep: UserRepository = UserRepository(session)
    task_settings: DailyUserTaskModel = await user_rep.get_user_notification_settings(telegram_id=user.telegram_id)

    await user_rep.update_users_coordinates(
        telegram_id=message.from_user.id,
        longitude=message.location.longitude,
        latitude=message.location.latitude)

    # update task with new coords if notification enabled
    if task_settings.notifications_enabled:
        await update_send_daily_weather_task(
            source=redis_source,
            time=task_settings.notification_time,
            location=(message.location.latitude, message.location.longitude),
            language=user.language_code,
            chat_id=user.telegram_id,
            taskiq_task_id=task_settings.taskiq_task_id,
            user_repo=user_rep,
        )

    await message.answer(text=i18n.get(
        "start-finish-registration",
        latitude=message.location.latitude,
        longitude=message.location.longitude),
        message_effect_id="5046509860389126442", )

    # When we first launch the bot, we don't have a dialog with the main window. When we access the dialog again,
    # we already have an existing dialog. To avoid creating one each time, we check how many dialogs there are.
    # If there's more than one, we simply close the extra one with the coordinates dialog.
    current_stack: Stack = dialog_manager.current_stack()
    if len(current_stack.intents) > 1:
        await dialog_manager.done()
    else:
        await dialog_manager.done()
        await dialog_manager.start(WeatherSG.weather_main_menu)


async def wrong_location_handler(message: Message,
                                 widget: MessageInput,
                                 dialog_manager: DialogManager) -> None:
    i18n: TranslatorRunner = dialog_manager.middleware_data.get("i18n")

    dialog_manager.show_mode = ShowMode.NO_UPDATE
    await message.answer(text=i18n.get("error-input-registration"))
