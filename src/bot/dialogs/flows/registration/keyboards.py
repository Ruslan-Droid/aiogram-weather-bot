from aiogram_dialog.widgets.kbd import SwitchTo

from src.bot.dialogs.flows.registration.states import StartRegistrationSG
from src.bot.dialogs.widgets.i18n import I18nFormat

SEND_CITY_BUTTON = SwitchTo(
    text=I18nFormat("change-city-button"),
    id="reply_back_button_from_group_task",
    state=StartRegistrationSG.send_city_registration,
)
