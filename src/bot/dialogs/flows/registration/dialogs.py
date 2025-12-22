from aiogram.enums import ContentType

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory
from aiogram_dialog.widgets.kbd import RequestLocation, Button, Row
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.media import StaticMedia

from src.bot.dialogs.flows.registration.keyboards import SEND_CITY_BUTTON
from src.bot.dialogs.flows.registration.states import StartRegistrationSG
from src.bot.dialogs.widgets.i18n import I18nFormat
from src.bot.dialogs.flows.registration.getters import getter_username, getter_registration_current_city
from src.bot.dialogs.flows.registration.handlers import location_handler, wrong_location_handler, \
    go_back_to_send_coords, city_handler_registration, wrong_city_handler_registration, registration_deny_city_on_click, \
    registration_save_city_on_click

from pathlib import Path

registration_dialog = Dialog(
    # send coordinates
    Window(
        Format("{user_name}"),
        StaticMedia(
            path=Path("src", "bot", "dialogs", "flows", "registration", "media", "new.mp4"),
            type=ContentType.ANIMATION,
        ),
        RequestLocation(I18nFormat("keyboard-coords")),
        SEND_CITY_BUTTON,
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
    ),
    # send city for registration
    Window(
        I18nFormat("start-change-city"),
        # ◀️ back button
        Button(
            text=I18nFormat("back-button"),
            id="coords_registration_back_button",
            on_click=go_back_to_send_coords,
        ),
        MessageInput(
            func=city_handler_registration,
            content_types=ContentType.TEXT
        ),
        MessageInput(
            func=wrong_city_handler_registration,
            content_types=ContentType.ANY
        ),
        state=StartRegistrationSG.send_city_registration,
    ),
    # save city registration
    Window(
        Format("{current_city}"),
        Row(
            # ◀️ back button
            Button(
                text=Format("{back_button}"),
                id="city_back_button",
                on_click=registration_deny_city_on_click,
            ),
            # ✅ Save button
            Button(
                text=Format("{save_button}"),
                id="city_save_button",
                on_click=registration_save_city_on_click,
            ),
        ),
        getter=getter_registration_current_city,
        state=StartRegistrationSG.save_city_registration,
    )
)
