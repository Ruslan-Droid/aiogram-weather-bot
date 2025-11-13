from taskiq import TaskiqDepends
from aiogram import Bot
from aiogram.types import Message

from fluentogram import TranslatorRunner

from src.services.scheduler.taskiq_broker import broker
from src.services.weather_api.weather_service import WeatherService


@broker.task()
async def send_scheduled_weather_forecast(
        i18n: TranslatorRunner,
        weather_service: WeatherService,
        location: str | tuple[float, float],
        language: str,
        chat_id: int,
        bot: Bot = TaskiqDepends(),
) -> None:
    weather_forecast = await weather_service.get_current_weather_forcast(i18n=i18n,
                                                                         location=location,
                                                                         language=language)
    await bot.send_message(
        chat_id=chat.id,
        text=weather_forecast,
    )
