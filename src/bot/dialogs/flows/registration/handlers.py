import logging

from aiogram_dialog.widgets.input import MessageInput
from aiogram.types import Message
from aiogram_dialog.api.protocols.manager import DialogManager
from aiogram_dialog.api.entities import ShowMode

from src.bot.dialogs.flows.weather.states import WeatherSG
from src.infrastructure.database.dao import UserRepository
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def location_handler(
        message: Message,
        widget: MessageInput,
        dialog_manager: DialogManager) -> None:
    session: AsyncSession = dialog_manager.middleware_data.get('session')
    i18n: TranslatorRunner = dialog_manager.middleware_data.get("i18n")
    user_rep: UserRepository = UserRepository(session)

    await user_rep.update_users_coordinates(
        telegram_id=message.from_user.id,
        longitude=message.location.longitude,
        latitude=message.location.latitude)

    await message.answer(text=i18n.get(
        "start-finish-registration",
        latitude=message.location.latitude,
        longitude=message.location.longitude))

    await dialog_manager.start(WeatherSG.weather_main_menu)


async def wrong_location_handler(message: Message,
                                 widget: MessageInput,
                                 dialog_manager: DialogManager) -> None:
    i18n: TranslatorRunner = dialog_manager.middleware_data.get("i18n")

    dialog_manager.show_mode = ShowMode.NO_UPDATE
    await message.answer(text=i18n.get("error-input-registration"))
