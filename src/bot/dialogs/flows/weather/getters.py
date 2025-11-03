from aiogram_dialog import DialogManager
from fluentogram import TranslatorRunner


async def getter_weather(dialog_manager: DialogManager, i18n: TranslatorRunner, **kwargs):
    i18n: TranslatorRunner = dialog_manager.middleware_data.get("translator_hub")

    return {
        "weather_now": i18n.get("weather-now-button"),
    }
