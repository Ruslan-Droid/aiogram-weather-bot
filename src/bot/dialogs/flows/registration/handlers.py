import logging

from aiogram_dialog.widgets.input import MessageInput
from aiogram.types import Message
from aiogram_dialog.api.protocols.manager import DialogManager
from aiogram_dialog.api.entities import ShowMode

from src.bot.dialogs.flows.weather.states import WeatherSG
from src.infrastructure.database.dao import UserRepository
from src.infrastructure.database.models import UserModel, UserScheduleTask
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
    task_settings: UserScheduleTask = await user_rep.get_user_notification_settings(telegram_id=user.telegram_id)

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

    await dialog_manager.done()
    await dialog_manager.start(WeatherSG.weather_main_menu)


async def wrong_location_handler(message: Message,
                                 widget: MessageInput,
                                 dialog_manager: DialogManager) -> None:
    i18n: TranslatorRunner = dialog_manager.middleware_data.get("i18n")

    dialog_manager.show_mode = ShowMode.NO_UPDATE
    await message.answer(text=i18n.get("error-input-registration"))
