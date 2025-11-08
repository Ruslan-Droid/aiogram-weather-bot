import logging

from aiogram_dialog.widgets.kbd import Button
from aiogram.types import CallbackQuery
from aiogram_dialog.api.protocols.manager import DialogManager
from aiogram_dialog.api.entities.modes import ShowMode

from src.bot.dialogs.flows.weather.states import WeatherSG
from src.bot.dialogs.flows.language_settings.states import SettingsSG
from src.services.weather_api.weather_service import WeatherService

from src.infrastructure.database.models import UserModel
from src.infrastructure.cache import RedisService

from fluentogram import TranslatorRunner
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


async def send_today_weather_on_click(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager) -> None:
    # get cache to use it
    redis_pool: Redis = dialog_manager.middleware_data.get("_cache_pool")
    redis_service: RedisService = RedisService(redis_pool=redis_pool)

    i18n: TranslatorRunner = dialog_manager.middleware_data.get("i18n")
    user: UserModel = dialog_manager.middleware_data.get("user_row")
    weather: WeatherService = dialog_manager.middleware_data.get("weather_service")

    current_weather = await redis_service.get_key(key=f"currentweather:{user.language_code}:{user.telegram_id}")

    if current_weather is None:
        logger.info("Cache is empty for user %s", user.telegram_id)

        current_weather = await weather.get_current_weather(
            location=(user.latitude, user.longitude),
            language=user.language_code,
            i18n=i18n
        )
        await redis_service.set_key_with_ttl(
            key=f"currentweather:{user.language_code}:{user.telegram_id}",
            value=current_weather,
            ttl=60 * 60)  # Cache for 1 hour

    await callback.message.answer(text=current_weather)
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND


async def send_today_forecast_on_click(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager) -> None:
    # get cache to use it
    redis_pool: Redis = dialog_manager.middleware_data.get("_cache_pool")
    redis_service: RedisService = RedisService(redis_pool=redis_pool)

    i18n: TranslatorRunner = dialog_manager.middleware_data.get("i18n")
    user: UserModel = dialog_manager.middleware_data.get("user_row")
    weather: WeatherService = dialog_manager.middleware_data.get("weather_service")

    today_forecast = await redis_service.get_key(key=f"forecastweather:{user.language_code}:{user.telegram_id}")

    if today_forecast is None:
        logger.info("Cache is empty for user %s", user.telegram_id)

        today_forecast = await weather.get_current_weather_forcast(
            location=(user.latitude, user.longitude),
            language=user.language_code,
            i18n=i18n
        )
        await redis_service.set_key_with_ttl(
            key=f"forecastweather:{user.language_code}:{user.telegram_id}",
            value=today_forecast,
            ttl=60 * 60)  # Cache for 1 hour

    await callback.message.answer(text=today_forecast)
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
