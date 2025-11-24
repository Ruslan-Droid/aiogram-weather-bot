from aiogram import Bot
from fluentogram import TranslatorHub, TranslatorRunner
from taskiq import TaskiqDepends, TaskiqState

from src.services.scheduler.taskiq_broker import broker, config
from src.services.weather_api.weather_service import WeatherService
from src.services.i18n.translator_hub import TranslatorHubFactory


@broker.task(task_name="daily_weather_task")
async def send_daily_weather(
        location: str | tuple[float, float],
        language: str,
        chat_id: int,
        state: TaskiqState = TaskiqDepends(),
) -> None:
    hub: TranslatorHub = TranslatorHubFactory(config).create()
    i18n: TranslatorRunner = hub.get_translator_by_locale(language)
    weather_service: WeatherService = state.weather_service
    bot: Bot = state.bot

    today_weather_forcast: str = await weather_service.get_current_weather_forcast(
        i18n=i18n,
        location=location,
        language=language,
    )
    await bot.send_message(chat_id=chat_id, text=today_weather_forcast)
