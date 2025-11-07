import logging

from aiogram_dialog.widgets.kbd import Button
from aiogram.types import CallbackQuery
from aiogram_dialog.api.protocols.manager import DialogManager

from src.services.weather_api.weather_service import WeatherService
from src.infrastructure.database.models import UserModel

logger = logging.getLogger(__name__)


async def send_today_weather_on_click(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager) -> None:
    user: UserModel = dialog_manager.middleware_data.get("user_row")
    weather: WeatherService = dialog_manager.middleware_data.get("weather_service")

    weather_dict = await weather.get_current_weather(location=(user.latitude, user.longitude),
                                                     language=user.language_code)
    await callback.message.answer(text=weather_dict["location"]["name"])
