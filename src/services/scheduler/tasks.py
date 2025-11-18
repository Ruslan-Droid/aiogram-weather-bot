from aiogram import Bot
from fluentogram import TranslatorRunner

from src.services.scheduler.taskiq_broker import broker
from src.services.weather_api.weather_service import WeatherService


@broker.task(task_name="simple_task")
async def simple_task():
    print("Simple task")


@broker.task(task_name="daily_weather_task")
async def send_daily_weather(
        weather_service: WeatherService,
        i18n: TranslatorRunner,
        location: str | tuple[float, float],
        language: str,
        bot: Bot,
        chat_id: int,
) -> None:
    today_weather_forcast: str = await weather_service.get_current_weather_forcast(
        i18n=i18n,
        location=location,
        language=language,
    )
    await bot.send_message(chat_id=chat_id, text=today_weather_forcast)
