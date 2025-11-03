from datetime import datetime, timedelta, timezone

from aiogram import Bot, Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.enums.roles import UserRole

from src.bot.dialogs.flows.start_registration.states import StartSG
from src.infrastructure.database.models import UserModel
from src.infrastructure.database.dao import UserRepository
from src.bot.keyboards.coords_kb import request_coords_kb

commands_router = Router()


@commands_router.message(CommandStart())
async def process_start_command(
        message: Message,
        dialog_manager: DialogManager,
        bot: Bot,
        state: FSMContext,
        i18n: TranslatorRunner,
        session: AsyncSession,
        user_row: UserModel | None,
) -> None:
    # add new user in table
    if user_row is None:
        user_rep = UserRepository(session)
        await user_rep.create_new_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            language_code=message.from_user.language_code,
        )
    username = message.from_user.username
    await dialog_manager.reset_stack()
    await message.answer(text=i18n.get("start-hello", username=username), reply_markup=request_coords_kb(i18n=i18n))
    await state.set_state(StartSG.start)


@commands_router.message(StateFilter(StartSG.start), F.location)
async def get_location(
        message: Message,
        dialog_manager: DialogManager,
        bot: Bot,
        i18n: TranslatorRunner,
        session: AsyncSession,
        user_row: UserModel | None,
) -> None:
    print(message.text)
