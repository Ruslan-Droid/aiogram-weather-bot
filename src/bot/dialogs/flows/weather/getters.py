from aiogram_dialog import DialogManager
from fluentogram import TranslatorRunner


async def getter_weather_main_menu(
        dialog_manager: DialogManager,
        i18n: TranslatorRunner,
        **kwargs):
    return {
        "weather_now": i18n.get("weather-now-button"),
        "weather_forecast": i18n.get("weather-forecast-button"),
        "main_settings": i18n.get("main-settings-button"),
    }


async def getter_weather_settings(
        dialog_manager: DialogManager,
        i18n: TranslatorRunner,
        **kwargs):
    return {
        "back_button" : i18n.get("back-button"),
        "language_settings_button": i18n.get("language_settings_button"),

    }