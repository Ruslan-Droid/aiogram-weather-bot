from datetime import datetime, timedelta, timezone

from aiogram import Bot, Router
from aiogram.enums import BotCommandScopeType
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommandScopeChat, Message
from aiogram_dialog import DialogManager, StartMode
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.enums.roles import UserRole

# from src.bot.dialogs.flows.settings.states import SettingsSG
from src.bot.dialogs.flows.start.states import StartSG
from src.infrastructure.database.models import UserModel
from src.infrastructure.database.dao import UserRepository

commands_router = Router()


@commands_router.message(CommandStart())
async def process_start_command(
        message: Message,
        dialog_manager: DialogManager,
        bot: Bot,
        i18n: TranslatorRunner,
        session: AsyncSession,
        user_row: UserModel | None,
) -> None:
    if user_row is None:
        user_rep = UserRepository(session)
        await user_rep.create_new_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            language_code=message.from_user.language_code,
        )

    await dialog_manager.start(state=StartSG.start, mode=StartMode.RESET_STACK)
