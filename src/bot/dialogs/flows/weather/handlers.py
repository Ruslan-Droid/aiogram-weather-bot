import logging

from aiogram_dialog.widgets.kbd import Button
from aiogram.types import CallbackQuery, Message
from aiogram_dialog.api.protocols.manager import DialogManager
from aiogram_dialog.api.entities.modes import ShowMode

from src.bot.dialogs.flows.weather.states import WeatherSG
from src.bot.dialogs.flows.language_settings.states import SettingsSG
from src.services.weather_api.weather_service import WeatherService
from src.services.delay_service.publisher import delay_message_deletion

from src.infrastructure.database.models import UserModel

from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from nats.js.client import JetStreamContext

logger = logging.getLogger(__name__)


async def send_today_weather_on_click(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager) -> None:
    delay = 60 * 60  # delet message after 1 hour

    redis_pool: Redis = dialog_manager.middleware_data.get("_cache_pool")
    i18n: TranslatorRunner = dialog_manager.middleware_data.get("i18n")
    user: UserModel = dialog_manager.middleware_data.get("user_row")
    weather: WeatherService = dialog_manager.middleware_data.get("weather_service")
    js: JetStreamContext = dialog_manager.middleware_data.get("js")
    delay_del_subject: str = dialog_manager.middleware_data.get("delay_del_subject")

    # get current weather from cache
    current_weather = await redis_pool.get(name=f"currentweather:{user.language_code}:{user.telegram_id}")

    if current_weather is None:
        logger.info("Cache is empty for user %s", user.telegram_id)

        current_weather = await weather.get_current_weather(
            location=(user.latitude, user.longitude),
            language=user.language_code,
            i18n=i18n
        )
        await redis_pool.setex(
            name=f"currentweather:{user.language_code}:{user.telegram_id}",
            value=current_weather,
            time=60 * 60)  # Cache for 1 hour

    # send in broker message to delet after delay
    msg: Message = await callback.message.answer(text=current_weather)
    await delay_message_deletion(
        js=js,
        chat_id=msg.chat.id,
        message_id=msg.message_id,
        subject=delay_del_subject,
        delay=delay,
    )

    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND


async def send_today_forecast_on_click(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager) -> None:
    delay = 60 * 60  # delet message after 1 hour

    redis_pool: Redis = dialog_manager.middleware_data.get("_cache_pool")
    i18n: TranslatorRunner = dialog_manager.middleware_data.get("i18n")
    user: UserModel = dialog_manager.middleware_data.get("user_row")
    weather: WeatherService = dialog_manager.middleware_data.get("weather_service")
    js: JetStreamContext = dialog_manager.middleware_data.get("js")
    delay_del_subject: str = dialog_manager.middleware_data.get("delay_del_subject")

    today_forecast = await redis_pool.get(name=f"forecastweather:{user.language_code}:{user.telegram_id}")

    if today_forecast is None:
        logger.info("Cache is empty for user %s", user.telegram_id)

        today_forecast = await weather.get_current_weather_forcast(
            location=(user.latitude, user.longitude),
            language=user.language_code,
            i18n=i18n
        )
        await redis_pool.setex(
            name=f"forecastweather:{user.language_code}:{user.telegram_id}",
            value=today_forecast,
            time=60 * 60)  # Cache for 1 hour

    msg: Message = await callback.message.answer(text=today_forecast)
    await delay_message_deletion(
        js=js,
        chat_id=msg.chat.id,
        message_id=msg.message_id,
        subject=delay_del_subject,
        delay=delay,
    )
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND


async def send_general_settings_on_click(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager) -> None:
    await dialog_manager.switch_to(state=WeatherSG.weather_general_settings)


async def go_to_main_menu_on_click(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager) -> None:
    await dialog_manager.switch_to(state=WeatherSG.weather_main_menu)


async def change_language_on_click(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager) -> None:
    await dialog_manager.start(state=SettingsSG.lang)
