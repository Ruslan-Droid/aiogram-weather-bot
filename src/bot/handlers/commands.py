from aiogram import Bot, Router
from aiogram.enums import BotCommandScopeType
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommandScopeChat
from aiogram_dialog import DialogManager, StartMode
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.enums.roles import UserRole
from src.bot.dialogs.flows.language_settings.states import SettingsSG
from src.infrastructure.database.models import UserModel
from src.infrastructure.database.dao import UserRepository
from src.bot.keyboards.menu_button import get_main_menu_commands
from src.bot.dialogs.flows.registration.states import StartRegistrationSG

commands_router = Router()


@commands_router.message(CommandStart())
async def command_start_handler(
        message: Message,
        dialog_manager: DialogManager,
        bot: Bot,
        state: FSMContext,
        i18n: TranslatorRunner,
        session: AsyncSession,
        user_row: UserModel | None,
) -> None:
    if user_row is None:
        user_rep = UserRepository(session)
        user_row = await user_rep.create_new_user(
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
    await dialog_manager.start(state=StartRegistrationSG.start_registration, mode=StartMode.RESET_STACK)


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
        i18n: TranslatorRunner
) -> None:
    await dialog_manager.start(state=SettingsSG.lang)
