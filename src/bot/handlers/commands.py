from aiogram import Bot, Router, F
from aiogram.enums import BotCommandScopeType
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommandScopeChat, ReplyKeyboardRemove
from aiogram_dialog import DialogManager, StartMode
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.enums.roles import UserRole
from src.bot.states.states import StartSG
from src.bot.dialogs.flows.settings.states import SettingsSG
from src.infrastructure.database.models import UserModel
from src.infrastructure.database.dao import UserRepository
from src.bot.keyboards.coords_kb import request_coords_kb
from src.bot.keyboards.menu_button import get_main_menu_commands
from src.bot.filters.dialog_filters import DialogStateGroupFilter, DialogStateFilter

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
    # add new user in table
    if user_row is None:
        user_rep = UserRepository(session)
        user_row = await user_rep.create_new_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            language_code=message.from_user.language_code,
        )
    await dialog_manager.reset_stack()

    await message.answer(
        text=i18n.get("start-hello", username=user_row.username),
        reply_markup=request_coords_kb(i18n=i18n))

    await bot.set_my_commands(
        commands=get_main_menu_commands(i18n=i18n),
        scope=BotCommandScopeChat(
            type=BotCommandScopeType.CHAT, chat_id=message.from_user.id
        ),
    )

    await state.set_state(StartSG.start)


@commands_router.message(StateFilter(StartSG.start), F.location)
async def location_handler(
        message: Message,
        state: FSMContext,
        i18n: TranslatorRunner,
        session: AsyncSession,
) -> None:
    user_rep = UserRepository(session)
    await user_rep.update_coordinates(
        telegram_id=message.from_user.id,
        longitude=message.location.longitude,
        latitude=message.location.latitude
    )
    await state.set_state()
    await message.answer(
        text=i18n.get(
            "start-finish-registration",
            latitude=message.location.latitude,
            longitude=message.location.longitude,
        ),
        reply_markup=ReplyKeyboardRemove()
    )


@commands_router.message(StateFilter(StartSG.start))
async def wrong_location_handler(
        message: Message,
        state: FSMContext,
        i18n: TranslatorRunner,
) -> None:
    await message.answer(text=i18n.get("wrong-location"))


@commands_router.message(Command("help"))
async def command_help_handler(
        message: Message,
        i18n: TranslatorRunner
) -> None:
    await message.answer(text=i18n.get("help-command"))


@commands_router.message(
    ~DialogStateGroupFilter(state_group=SettingsSG),
    Command("lang")
)
async def process_lang_command_sg(
        message: Message,
        dialog_manager: DialogManager,
        i18n: TranslatorRunner
) -> None:
    await dialog_manager.start(state=SettingsSG.lang)


@commands_router.message(
    DialogStateGroupFilter(state_group=SettingsSG),
    ~DialogStateFilter(state=SettingsSG.lang),
    Command("lang"),
)
async def process_lang_command(
        message: Message,
        dialog_manager: DialogManager,
        i18n: TranslatorRunner
) -> None:
    await dialog_manager.switch_to(state=SettingsSG.lang)
