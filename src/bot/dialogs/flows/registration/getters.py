from aiogram_dialog import DialogManager
from fluentogram import TranslatorRunner
from aiogram.types import User


async def getter_username(
        dialog_manager: DialogManager,
        i18n: TranslatorRunner,
        event_from_user: User,
        **kwargs
) -> dict[str, str]:
    username = event_from_user.full_name or event_from_user.username or i18n.stranger()
    return {"user_name": i18n.start.hello(username=username)}


async def getter_registration_current_city(
        dialog_manager: DialogManager,
        i18n: TranslatorRunner,
        **kwargs,
) -> dict[str, str]:
    city_name = dialog_manager.dialog_data["city_name"]
    city_info = dialog_manager.dialog_data["city_info"]
    return {
        "back_button": i18n.get("back-button"),
        "save_button": i18n.get("save-button"),
        "current_city": i18n.get("city-found-successfully", city_name=city_name, city_info=city_info),
    }
