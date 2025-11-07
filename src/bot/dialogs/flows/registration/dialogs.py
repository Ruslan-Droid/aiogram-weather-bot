from aiogram.enums import ContentType

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory
from aiogram_dialog.widgets.kbd import RequestLocation
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.media import StaticMedia

from src.bot.dialogs.flows.registration.states import StartRegistrationSG
from src.bot.dialogs.widgets.i18n import I18nFormat
from src.bot.dialogs.flows.registration.getters import getter_username
from src.bot.dialogs.flows.registration.handlers import location_handler, wrong_location_handler

from pathlib import Path

registration_dialog = Dialog(
    Window(
        Format("{user_name}"),
        StaticMedia(
            path=Path("src", "bot", "dialogs", "flows", "registration", "media", "new.mp4"),
            type=ContentType.ANIMATION,
        ),
        RequestLocation(I18nFormat("keyboard-coords")),
        MessageInput(
            func=location_handler,
            content_types=ContentType.LOCATION
        ),
        MessageInput(
            func=wrong_location_handler,
            content_types=ContentType.ANY
        ),
        markup_factory=ReplyKeyboardFactory(
            resize_keyboard=True),
        getter=getter_username,
        state=StartRegistrationSG.start_registration,
    )
)
