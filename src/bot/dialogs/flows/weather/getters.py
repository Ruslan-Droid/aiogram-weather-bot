from aiogram_dialog import DialogManager
from fluentogram import TranslatorRunner


async def getter_weather(
        dialog_manager: DialogManager,
        i18n: TranslatorRunner,
        **kwargs):

    return {
        "weather_now": i18n.get("weather-now-button"),
    }
