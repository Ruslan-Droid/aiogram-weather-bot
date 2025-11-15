from aiogram import Bot, Router
from aiogram.enums import BotCommandScopeType
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BotCommandScopeChat

from aiogram_dialog import DialogManager, StartMode
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.dialogs.flows.language_settings.states import SettingsSG
from src.bot.dialogs.flows.registration.states import StartRegistrationSG
from src.bot.dialogs.flows.weather.states import WeatherSG
from src.infrastructure.database.models import UserModel
from src.infrastructure.database.dao import UserRepository
from src.bot.keyboards.menu_button import get_main_menu_commands

from src.services.scheduler.tasks import test, test_with_arguments
from taskiq_redis import RedisScheduleSource

commands_router = Router()


@commands_router.message(CommandStart())
async def command_start_handler(
        message: Message,
        dialog_manager: DialogManager,
        bot: Bot,
        i18n: TranslatorRunner,
        session: AsyncSession,
        user_row: UserModel | None,
) -> None:
    if user_row is None:
        user_rep: UserRepository = UserRepository(session)
        user_row: UserModel = await user_rep.create_new_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            language_code=message.from_user.language_code,
        )

    await bot.set_my_commands(
        commands=get_main_menu_commands(i18n=i18n),
        scope=BotCommandScopeChat(
            type=BotCommandScopeType.CHAT, chat_id=message.from_user.id
        ),
    )

    if user_row.latitude is None or user_row.longitude is None or user_row.city is None:
        await dialog_manager.start(state=StartRegistrationSG.start_registration, mode=StartMode.RESET_STACK)
    else:
        await dialog_manager.start(state=WeatherSG.weather_main_menu, mode=StartMode.RESET_STACK)


@commands_router.message(Command("help"))
async def command_help_handler(
        message: Message,
        i18n: TranslatorRunner
) -> None:
    await message.answer(text=i18n.get("help-command"))


@commands_router.message(Command("lang"))
async def process_lang_command_sg(
        message: Message,
        dialog_manager: DialogManager,
) -> None:
    await dialog_manager.start(state=SettingsSG.lang)


@commands_router.message(Command("test"))
async def test_command_handler(
        message: Message,
) -> None:
    await test.kiq()
    await message.answer(text="Простая задача отправлена")


@commands_router.message(Command("test2"))
async def test2_command_handler(
        message: Message,
) -> None:
    await test_with_arguments.kiq(10)
    await message.answer(text="Простая задача отправлена с аргументом")

