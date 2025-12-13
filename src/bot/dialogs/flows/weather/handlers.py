import logging

from aiogram.types import CallbackQuery, Message
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, ManagedCheckbox, Select
from aiogram_dialog.api.protocols.manager import DialogManager
from aiogram_dialog.api.entities.modes import ShowMode

from src.bot.dialogs.flows.weather.states import WeatherSG
from src.bot.dialogs.flows.language_settings.states import SettingsSG

from src.infrastructure.database.dao import UserRepository, GroupChatRepository
from src.infrastructure.database.models import UserModel, DailyUserTaskModel, GroupModel
from src.services.open_street_map_api.city_service import CityService

from src.services.weather_api.weather_service import WeatherService
from src.services.delay_service.publisher import delay_message_deletion
from src.services.scheduler.tasks import send_daily_weather, update_send_daily_weather_task

from fluentogram import TranslatorRunner
from taskiq import ScheduledTask
from taskiq_redis import RedisScheduleSource
from redis.asyncio import Redis
from nats.js.client import JetStreamContext
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

delay = 60 * 60  # delet message after 1 hour


async def send_today_weather_on_click(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager) -> None:
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

        location = (user.latitude, user.longitude) if user.city is None else user.city

        current_weather = await weather.get_current_weather(
            location=location,
            language=user.language_code,
            i18n=i18n
        )
        await redis_pool.setex(
            name=f"currentweather:{user.language_code}:{user.telegram_id}",
            value=current_weather,
            time=60 * 60)  # Cache for 1 hour

    # send in broker message to delet after delay
    msg: Message = await callback.message.answer(text=current_weather, message_effect_id="5159385139981059251")
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
    redis_pool: Redis = dialog_manager.middleware_data.get("_cache_pool")
    i18n: TranslatorRunner = dialog_manager.middleware_data.get("i18n")
    user: UserModel = dialog_manager.middleware_data.get("user_row")
    weather: WeatherService = dialog_manager.middleware_data.get("weather_service")
    js: JetStreamContext = dialog_manager.middleware_data.get("js")
    delay_del_subject: str = dialog_manager.middleware_data.get("delay_del_subject")

    today_forecast = await redis_pool.get(name=f"forecastweather:{user.language_code}:{user.telegram_id}")

    if today_forecast is None:
        logger.info("Cache is empty for user %s", user.telegram_id)
        location = (user.latitude, user.longitude) if user.city is None else user.city

        today_forecast = await weather.get_current_weather_forcast(
            location=location,
            language=user.language_code,
            i18n=i18n
        )
        await redis_pool.setex(
            name=f"forecastweather:{user.language_code}:{user.telegram_id}",
            value=today_forecast,
            time=60 * 60)  # Cache for 1 hour

    msg: Message = await callback.message.answer(text=today_forecast, message_effect_id="5159385139981059251")
    await delay_message_deletion(
        js=js,
        chat_id=msg.chat.id,
        message_id=msg.message_id,
        subject=delay_del_subject,
        delay=delay,
    )
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND


async def go_to_general_settings_on_click(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager) -> None:
    await dialog_manager.switch_to(state=WeatherSG.weather_general_settings)


async def go_to_group_settings_on_click(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager) -> None:
    await dialog_manager.switch_to(state=WeatherSG.weather_group_settings)


async def go_to_main_menu_on_click(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager) -> None:
    await dialog_manager.switch_to(state=WeatherSG.weather_main_menu)


# changing language button
async def change_language_on_click(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager) -> None:
    await dialog_manager.start(state=SettingsSG.lang)


# changing time button and handlers
async def change_notification_time_on_click(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager) -> None:
    await dialog_manager.switch_to(state=WeatherSG.weather_changing_time)


async def time_handler(
        message: Message,
        widget: MessageInput,
        dialog_manager: DialogManager) -> None:
    session: AsyncSession = dialog_manager.middleware_data.get("session")
    user: UserModel = dialog_manager.middleware_data.get("user_row")
    i18n: TranslatorRunner = dialog_manager.middleware_data.get("i18n")
    redis_source: RedisScheduleSource = dialog_manager.middleware_data.get("redis_source")

    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND

    time = message.text

    if len(time) == 5 and time[2] == ":":
        hours, minutes = map(int, time.split(":"))
        if 0 <= hours <= 23 and 0 <= minutes <= 59:
            user_repo: UserRepository = UserRepository(session)
            await user_repo.update_daly_notification_time(telegram_id=user.telegram_id, notification_time=time)

            task_settings: DailyUserTaskModel = user.daily_task

            # update task with new time if notification enabled
            if task_settings.notifications_enabled:
                location = (user.latitude, user.longitude) if user.city is None else user.city

                await update_send_daily_weather_task(
                    source=redis_source,
                    time=time,
                    location=location,
                    language=user.language_code,
                    chat_id=user.telegram_id,
                    taskiq_task_id=task_settings.taskiq_task_id,
                    user_repo=user_repo,
                )

            await message.answer(text=i18n.get("time-changed-successfully", time=time),
                                 message_effect_id="5046509860389126442")
            await dialog_manager.switch_to(state=WeatherSG.weather_general_settings)
    else:
        await message.delete()


async def wrong_time_handler(
        message: Message,
        widget: MessageInput,
        dialog_manager: DialogManager) -> None:
    i18n: TranslatorRunner = dialog_manager.middleware_data.get("i18n")

    dialog_manager.show_mode = ShowMode.NO_UPDATE
    await message.delete()
    await message.answer(text=i18n.get("error-input-time"))


# changing coords button
async def change_coords_on_click(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager) -> None:
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.start(state=WeatherSG.weather_changing_coords)


# changing city button and handlers
async def change_city_on_click(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager) -> None:
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await callback.message.delete()
    await dialog_manager.switch_to(state=WeatherSG.weather_changing_city)


async def city_handler(
        message: Message,
        widget: MessageInput,
        dialog_manager: DialogManager) -> None:
    i18n: TranslatorRunner = dialog_manager.middleware_data.get("i18n")
    city_service: CityService = dialog_manager.middleware_data.get("city_service")

    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND

    city = message.text.strip().lower()
    checked_city = await city_service.check_city(city)

    if checked_city:
        city_info, city_name = checked_city
        dialog_manager.dialog_data["city_name"] = city_name
        dialog_manager.dialog_data["city_info"] = city_info

        await dialog_manager.switch_to(state=WeatherSG.weather_save_city)
    else:
        await message.delete()
        await message.answer(text=i18n.get("city-not-found"))


async def wrong_city_handler(
        message: Message,
        widget: MessageInput,
        dialog_manager: DialogManager) -> None:
    i18n: TranslatorRunner = dialog_manager.middleware_data.get("i18n")

    dialog_manager.show_mode = ShowMode.NO_UPDATE
    await message.delete()
    await message.answer(text=i18n.get("city-not-found"))


async def save_city_on_click(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager) -> None:
    session: AsyncSession = dialog_manager.middleware_data.get("session")
    user: UserModel = dialog_manager.middleware_data.get("user_row")
    redis_source: RedisScheduleSource = dialog_manager.middleware_data.get("redis_source")

    user_repo: UserRepository = UserRepository(session)

    city_name = dialog_manager.dialog_data["city_name"]

    await user_repo.update_user_city(telegram_id=user.telegram_id, city=city_name)

    task_settings: DailyUserTaskModel = user.daily_task

    # update task with new city if notification enabled
    if task_settings.notifications_enabled:
        await update_send_daily_weather_task(
            source=redis_source,
            time=task_settings.notification_time,
            location=city_name,
            language=user.language_code,
            chat_id=user.telegram_id,
            taskiq_task_id=task_settings.taskiq_task_id,
            user_repo=user_repo,
        )

    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(WeatherSG.weather_general_settings)


async def deny_city_on_click(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager) -> None:
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(WeatherSG.weather_changing_city)


async def deny_choosing_group_on_click(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager) -> None:
    await dialog_manager.switch_to(WeatherSG.weather_main_menu)


async def weather_notification_clicked(
        callback: CallbackQuery,
        checkbox: ManagedCheckbox,
        dialog_manager: DialogManager) -> None:
    session: AsyncSession = dialog_manager.middleware_data.get("session")
    user: UserModel = dialog_manager.middleware_data.get("user_row")
    redis_source: RedisScheduleSource = dialog_manager.middleware_data.get("redis_source")
    user_repo: UserRepository = UserRepository(session)
    i18n: TranslatorRunner = dialog_manager.middleware_data.get("i18n")

    user_notification_settings: DailyUserTaskModel = user.daily_task

    if not user_notification_settings.notifications_enabled:

        location = (user.latitude, user.longitude) if user.city is None else user.city

        task: ScheduledTask = await send_daily_weather.schedule_by_cron(
            source=redis_source,
            # cron=f"{user.user_schedule_task.notification_time.split(":")[0]} {user.user_schedule_task.notification_time.split(":")[1]} * * *",
            cron="*/1 * * * *",
            location=location,
            language=user.language_code,
            chat_id=callback.message.chat.id,
        )
        task_id = task.schedule_id
        logger.debug("Schedule task for user %s successful added in taskiq", user.telegram_id)
        await user_repo.enable_notification_settings_and_add_task_id(
            telegram_id=user.telegram_id,
            task_id=task_id,
        )
        await callback.answer(
            text=i18n.get("notification-time-alert",
                          time=user_notification_settings.notification_time),
            show_alert=True
        )

    else:
        await callback.answer(text=i18n.get("on-notification-button"),
                              show_alert=True)
        await redis_source.delete_schedule(user.daily_task.taskiq_task_id)
        await user_repo.disable_notification_settings_and_remove_task_id(
            telegram_id=user.telegram_id)


async def group_click_handler(
        callback: CallbackQuery,
        widget: Select,  # Теперь это Select виджет
        dialog_manager: DialogManager,
        item_id: str,  # group_telegram_id из item_id_getter
):
    """Обработчик выбора группы через Select виджет"""
    # Получаем выбранную группу
    session: AsyncSession = dialog_manager.middleware_data.get("session")
    group_repo: GroupChatRepository = GroupChatRepository(session)

    # Находим группу по group_telegram_id
    group: GroupModel = await group_repo.get_group_by_chat_id(telegram_chat_id=int(item_id))

    if not group:
        await callback.answer("Группа не найдена", show_alert=True)
        return

    # Сохраняем ID выбранной группы

    dialog_manager.dialog_data["selected_group_settings"] = {
        "id": group.id,
        "telegram_id": group.group_telegram_id
        "title": group.title,
        "group_language": group.language_code,
    }

    # Показываем уведомление
    await callback.answer(f"Выбрана группа: {group.title or group.group_telegram_id}")

    await dialog_manager.switch_to(WeatherSG.weather_edit_group)