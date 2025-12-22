from typing import Any

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import ManagedRadio
from fluentogram import TranslatorRunner, TranslatorHub
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.dialogs.flows.language_settings.keyboards import get_lang_buttons
from src.infrastructure.database.dao import UserRepository, GroupTaskRepository
from src.infrastructure.database.models import UserModel


async def getter_weather_main_menu(
        dialog_manager: DialogManager,
        i18n: TranslatorRunner,
        **kwargs) -> dict[str, Any]:
    return {
        "weather_now": i18n.get("weather-now-button"),
        "weather_forecast": i18n.get("weather-forecast-button"),
        "main_settings": i18n.get("main-settings-button"),
        "off_notification": i18n.get("off-notification-button"),
        "on_notification": i18n.get("on-notification-button"),
        "add_group_button": i18n.get("add-group-button"),
        "group_settings": i18n.get("group-settings-button"),
    }


async def getter_weather_settings(
        dialog_manager: DialogManager,
        i18n: TranslatorRunner,
        session: AsyncSession,
        user_row: UserModel,
        **kwargs) -> dict[str, Any]:
    user_repo: UserRepository = UserRepository(session)

    user_settings = await user_repo.get_all_user_settings(telegram_id=user_row.telegram_id)
    if user_settings.get("city") is None:
        user_settings["city"] = "empty"

    return {
        "general_settings_weather_settings": i18n.get("general-settings-weather-settings",
                                                      language_settings=user_settings.get("language_code"),
                                                      time_settings=user_settings.get("notification_time"),
                                                      coords_settings=user_settings.get("coords"),
                                                      city_settings=user_settings.get("city"),
                                                      ),
        "back_button": i18n.get("back-button"),
        "language_settings_button": i18n.get("language-settings-button"),
        "coords_settings_button": i18n.get("coords-settings-button"),
        "settings_change_time_notification_button": i18n.get("settings-change-time-notification-button"),
        "change_city_button": i18n.get("change-city-button"),
    }


async def getter_weather_time_settings(
        dialog_manager: DialogManager,
        i18n: TranslatorRunner,
        **kwargs) -> dict[str, Any]:
    return {
        "back_button": i18n.get("back-button"),
    }


async def getter_weather_city_settings(
        dialog_manager: DialogManager,
        i18n: TranslatorRunner,
        **kwargs) -> dict[str, Any]:
    return {
        "back_button": i18n.get("back-button"),
    }


async def getter_weather_changing_city(
        dialog_manager: DialogManager,
        i18n: TranslatorRunner,
        **kwargs) -> dict[str, Any]:
    city_name = dialog_manager.dialog_data["city_name"]
    city_info = dialog_manager.dialog_data["city_info"]
    return {
        "back_button": i18n.get("back-button"),
        "save_button": i18n.get("save-button"),
        "current_city": i18n.get("city-found-successfully", city_name=city_name, city_info=city_info),
    }


async def getter_weather_group_settings(
        dialog_manager: DialogManager,
        i18n: TranslatorRunner,
        user_row: UserModel,
        session: AsyncSession,
        **kwargs) -> dict[str, Any]:
    user_repo = UserRepository(session)
    groups = await user_repo.get_active_admin_groups_by_telegram_id(telegram_id=user_row.telegram_id)

    groups_data = []
    for group in groups:
        groups_data.append({
            "id": str(group.id),
            "title": f"👨‍👩‍👦‍👦 {group.title}" or f"Group {group.group_telegram_id}",
            "group_telegram_id": group.group_telegram_id,
        })

    return {
        "group_settings_window": i18n.get("group-settings-window"),
        "back_button": i18n.get("back-button"),
        "groups_data": groups_data,
        "groups_count": len(groups_data)
    }


async def getter_edit_group_settings(
        dialog_manager: DialogManager,
        i18n: TranslatorRunner,
        session: AsyncSession,
        **kwargs) -> dict[str, Any]:
    settings = dialog_manager.dialog_data["selected_group_settings"]
    language = "Русский" if settings["group_language"] == "ru" else "English"

    return {
        "group_current_settings": i18n.get("group-current-settings", title=settings["title"],
                                           language=language),
        "edit_language_for_groups_message": i18n.get("edit-language-for-groups-message"),
        "task1_button": i18n.get("task1-button"),
        "task2_button": i18n.get("task2-button"),
        "back_button": i18n.get("back-button"),

    }


async def getter_edit_group_language(
        dialog_manager: DialogManager,
        i18n: TranslatorRunner,
        **kwargs
) -> dict[str, Any]:
    locales = dialog_manager.middleware_data.get("bot_locales")

    return {
        "language_group_window": i18n.get("language-group-window"),
        "lang_group_buttons": get_lang_buttons(locales=locales, i18n=i18n),
        "back_button": i18n.get("back-button"),
        "save_button": i18n.get("save-button"),
    }


async def getter_group_task_settings(
        dialog_manager: DialogManager,
        i18n: TranslatorRunner,
        session: AsyncSession,
        user_row: UserModel,
        **kwargs) -> dict[str, Any]:

    group_id = dialog_manager.dialog_data["selected_group_settings"]["id"]
    task_number = dialog_manager.dialog_data["selected_task_number"]

    # get task from DB
    group_task_repo = GroupTaskRepository(session)
    task = await group_task_repo.get_group_task(group_id, task_number, user_row)

    city = task.city if task.city else "Empty"
    coords = f"{task.latitude}, {task.longitude}" if (task.latitude and task.longitude) else "Empty"
    notifications_enabled = i18n.get("notifications-on") if task.notifications_enabled else i18n.get(
        "notifications-off")

    return {
        "group_task_settings_window": i18n.get(
            "group-task-settings-window",
            task_number=task_number,
            notification_time=task.notification_time,
            city=city,
            coords=coords,
            notifications_enabled=notifications_enabled,
        ),

        "back_button": i18n.get("back-button"),
        "change_time_button": i18n.get("settings-change-time-notification-button"),
        "change_city_button": i18n.get("change-city-button"),
        "change_coords_button": i18n.get("coords-settings-button"),
        "toggle_notifications_button": notifications_enabled
    }
