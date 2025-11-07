from aiogram_dialog import DialogManager
from fluentogram import TranslatorRunner
from aiogram.types import User


async def getter_username(
        dialog_manager: DialogManager,
        i18n: TranslatorRunner,
        event_from_user: User,
        **kwargs) -> dict[str, str]:
    username = event_from_user.full_name or event_from_user.username or i18n.stranger()
    return {"user_name": i18n.start.hello(username=username)}
