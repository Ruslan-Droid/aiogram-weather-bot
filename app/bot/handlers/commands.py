from datetime import datetime, timedelta, timezone

from aiogram import Bot, Router
from aiogram.enums import BotCommandScopeType
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommandScopeChat, Message
from aiogram_dialog import DialogManager, StartMode
from fluentogram import TranslatorRunner

from app.bot.enums.roles import UserRole
from app.bot.filters.dialog_filters import DialogStateFilter, DialogStateGroupFilter
from app.bot.keyboards.links_kb import get_links_kb
from app.bot.dialogs.flows.settings.states import SettingsSG
from app.bot.dialogs.flows.start.states import StartSG
from app.bot.keyboards.menu_button import get_main_menu_commands
from app.infrastructure.database.db import DB
from app.infrastructure.database.models.user import UserModel

commands_router = Router()


@commands_router.message(CommandStart())
async def process_start_command(
        message: Message,
        dialog_manager: DialogManager,
        bot: Bot,
        i18n: TranslatorRunner,
        db: DB,
        user_row: UserModel | None,
) -> None:
    if user_row is None:
        await db.users.add(
            user_id=message.from_user.id,
            language=message.from_user.language_code,
            role=UserRole.USER,
        )
    await bot.set_my_commands(
        commands=get_main_menu_commands(i18n=i18n),
        scope=BotCommandScopeChat(
            type=BotCommandScopeType.CHAT, chat_id=message.from_user.id
        ),
    )
    await dialog_manager.start(state=StartSG.start, mode=StartMode.RESET_STACK)




@commands_router.message(
    ~DialogStateGroupFilter(state_group=SettingsSG), Command("lang")
)
async def process_lang_command_sg(
        message: Message, dialog_manager: DialogManager, i18n: TranslatorRunner
) -> None:
    await dialog_manager.start(state=SettingsSG.lang)


@commands_router.message(
    DialogStateGroupFilter(state_group=SettingsSG),
    ~DialogStateFilter(state=SettingsSG.lang),
    Command("lang"),
)
async def process_lang_command(
        message: Message, dialog_manager: DialogManager, i18n: TranslatorRunner
) -> None:
    await dialog_manager.switch_to(state=SettingsSG.lang)


@commands_router.message(Command("help"))
async def process_help_command(
        message: Message, dialog_manager: DialogManager, i18n: TranslatorRunner
) -> None:
    await message.answer(text=i18n.help.command(), reply_markup=get_links_kb(i18n=i18n))
