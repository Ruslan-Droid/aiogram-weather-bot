import logging

from aiogram_dialog.widgets.input import MessageInput
from aiogram.types import Message, CallbackQuery
from aiogram_dialog.api.protocols.manager import DialogManager
from aiogram_dialog.api.entities import ShowMode, Stack
from aiogram_dialog.widgets.kbd import Button

from src.bot.dialogs.flows.registration.states import StartRegistrationSG
from src.bot.dialogs.flows.weather.states import WeatherSG
from src.infrastructure.database.dao import UserRepository
from src.infrastructure.database.models import UserModel, DailyUserTaskModel
from src.services.open_street_map_api.city_service import CityService
from src.services.scheduler.tasks import update_send_daily_weather_task

from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession
from taskiq_redis import RedisScheduleSource

from src.services.weather_api.weather_service import WeatherService

logger = logging.getLogger(__name__)


async def location_handler(
        message: Message,
        widget: MessageInput,
        dialog_manager: DialogManager) -> None:
    session: AsyncSession = dialog_manager.middleware_data.get('session')
    i18n: TranslatorRunner = dialog_manager.middleware_data.get("i18n")
    redis_source: RedisScheduleSource = dialog_manager.middleware_data.get("redis_source")
    user: UserModel = dialog_manager.middleware_data.get("user_row")
    weather_service: WeatherService = dialog_manager.middleware_data.get("weather_service")

    user_repo: UserRepository = UserRepository(session)
    task_settings: DailyUserTaskModel = user.daily_task

    longitude = message.location.longitude
    latitude = message.location.latitude

    await user_repo.update_users_coordinates(
        telegram_id=message.from_user.id,
        longitude=longitude,
        latitude=latitude)

    tz_region = await weather_service.get_current_time_zone(location=(latitude, longitude))

    await user_repo.update_user_tz_region(
        telegram_id=message.from_user.id,
        tz_region=tz_region
    )

    # update task with new coords if notification enabled
    if task_settings.notifications_enabled:
        await update_send_daily_weather_task(
            source=redis_source,
            tz_region=tz_region,
            time=task_settings.notification_time,
            location=(latitude, longitude),
            language=user.language_code,
            telegram_chat_id=user.telegram_id,
            taskiq_task_id=task_settings.taskiq_task_id,
            session=session,
        )

    await message.answer(text=i18n.get(
        "start-finish-registration",
        latitude=latitude,
        longitude=longitude),
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


# 🏡 city handler
async def city_handler_registration(
        message: Message,
        widget: MessageInput,
        dialog_manager: DialogManager
) -> None:
    i18n: TranslatorRunner = dialog_manager.middleware_data.get("i18n")
    city_service: CityService = dialog_manager.middleware_data.get("city_service")

    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND

    city = message.text

    checked_city = await city_service.check_city(city)

    if checked_city:
        city_info, city_name = checked_city
        dialog_manager.dialog_data["city_name"] = city_name
        dialog_manager.dialog_data["city_info"] = city_info

        await dialog_manager.switch_to(state=StartRegistrationSG.save_city_registration)
    else:
        await message.delete()
        await message.answer(text=i18n.get("city-not-found"))


# 🏡 wrong city handler
async def wrong_city_handler_registration(
        message: Message,
        widget: MessageInput,
        dialog_manager: DialogManager
) -> None:
    i18n: TranslatorRunner = dialog_manager.middleware_data.get("i18n")

    dialog_manager.show_mode = ShowMode.NO_UPDATE
    await message.delete()
    await message.answer(text=i18n.get("city-not-found"))


# 🏡 save chosen city ✅
async def registration_save_city_on_click(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager
) -> None:
    session: AsyncSession = dialog_manager.middleware_data.get("session")
    user: UserModel = dialog_manager.middleware_data.get("user_row")
    i18n: TranslatorRunner = dialog_manager.middleware_data.get("i18n")
    redis_source: RedisScheduleSource = dialog_manager.middleware_data.get("redis_source")
    weather_service: WeatherService = dialog_manager.middleware_data.get("weather_service")

    user_repo: UserRepository = UserRepository(session)

    city_name = dialog_manager.dialog_data["city_name"]

    await user_repo.update_user_city(telegram_id=user.telegram_id, city=city_name)
    tz_region = await weather_service.get_current_time_zone(location=city_name)
    await user_repo.update_user_tz_region(telegram_id=user.telegram_id, tz_region=tz_region)

    task_settings: DailyUserTaskModel = user.daily_task
    # update task with new city if notification enabled
    if task_settings.notifications_enabled:
        await update_send_daily_weather_task(
            source=redis_source,
            tz_region=tz_region,
            time=task_settings.notification_time,
            location=city_name,
            language=user.language_code,
            telegram_chat_id=user.telegram_id,
            taskiq_task_id=task_settings.taskiq_task_id,
            session=session,
        )

    await callback.message.answer(text=i18n.get(
        "city-finish-registration",
        city=city_name,
        message_effect_id="5046509860389126442"))

    dialog_manager.dialog_data.clear()
    await dialog_manager.done()
    await dialog_manager.start(WeatherSG.weather_main_menu)


# 🏡 deny chosen city ❌
async def registration_deny_city_on_click(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager
) -> None:
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(StartRegistrationSG.send_city_registration)


async def go_back_to_send_coords(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager
) -> None:
    await dialog_manager.switch_to(StartRegistrationSG.start_registration)
