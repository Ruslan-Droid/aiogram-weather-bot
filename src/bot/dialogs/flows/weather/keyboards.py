from aiogram_dialog.widgets.kbd import Start

from src.bot.dialogs.widgets.i18n import I18nFormat
from src.bot.dialogs.flows.weather.states import WeatherSG

MAIN_SETTINGS_BUTTON = Start(
    text=I18nFormat("back-button"),
    id="reply_back_button",
    state=WeatherSG.weather_general_settings,
)
