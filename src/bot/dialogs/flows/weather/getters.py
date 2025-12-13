from typing import Any

from aiogram_dialog import DialogManager
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.dao import UserRepository
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
            "title": group.title or f"Группа {group.group_telegram_id}",
            "group_telegram_id": group.group_telegram_id,
        })

    return {
        "group_settings_window": i18n.get("group-settings-window"),
        "back_button": i18n.get("back-button"),
        "groups_data": groups_data,
    }
