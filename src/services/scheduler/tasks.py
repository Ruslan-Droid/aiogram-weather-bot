import logging

from aiogram import Bot
from fluentogram import TranslatorHub, TranslatorRunner
from taskiq import TaskiqDepends, TaskiqState, ScheduledTask
from taskiq_redis import RedisScheduleSource

from src.infrastructure.database.dao import UserRepository, GroupTaskRepository
from src.services.scheduler.taskiq_broker import broker, config
from src.services.weather_api.weather_service import WeatherService
from src.services.i18n.translator_hub import TranslatorHubFactory

logger = logging.getLogger(__name__)


@broker.task(task_name="daily_weather_task")
async def send_daily_weather(
        location: str | tuple[float, float],
        language: str,
        telegram_chat_id: int,
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
    await bot.send_message(chat_id=telegram_chat_id, text=today_weather_forcast)


async def update_send_daily_weather_task(
        source: RedisScheduleSource,
        time: str,
        tz_region: str,
        location: str | tuple[float, float],
        language: str,
        telegram_chat_id: int,
        taskiq_task_id: str,
        user_repo: UserRepository,
) -> None:
    # delete old task
    await source.delete_schedule(taskiq_task_id)
    logger.debug("Schedule task %s from taskiq successful deleted", taskiq_task_id)
    # create new task
    task: ScheduledTask = await send_daily_weather.schedule_by_cron(
        source=source,
        # cron=f"{time.split(":")[0]} {time.split(":")[1]} * * *",
        # cron_offset=tz_region,
        cron="*/2 * * * *",
        location=location,
        language=language,
        telegram_chat_id=telegram_chat_id,
    )
    new_task_id = task.schedule_id
    await user_repo.update_taskiq_task_id(
        telegram_id=telegram_chat_id,
        taskiq_task_id=new_task_id,
    )
    logger.debug("Schedule task %s successful added", new_task_id)


async def update_send_daily_weather_task_for_group(
        source: RedisScheduleSource,
        time: str,
        tz_region: str,
        location: str | tuple[float, float],
        language: str,
        telegram_chat_id: int,
        group_id: int,
        group_task_number: int,
        taskiq_task_id: str,
        group_repo: GroupTaskRepository,
) -> None:
    # delete old task
    await source.delete_schedule(taskiq_task_id)
    logger.debug("Schedule task %s from taskiq successful deleted", taskiq_task_id)
    # create new task
    task: ScheduledTask = await send_daily_weather.schedule_by_cron(
        source=source,
        # cron=f"{time.split(":")[0]} {time.split(":")[1]} * * *",
        # cron_offset=tz_region,
        cron="*/2 * * * *",
        location=location,
        language=language,
        telegram_chat_id=telegram_chat_id,
    )
    new_task_id = task.schedule_id
    await group_repo.update_taskiq_task_id(
        group_id=group_id,
        task_number=group_task_number,
        taskiq_task_id=new_task_id,
    )
    logger.debug("Schedule task %s successful added", new_task_id)
