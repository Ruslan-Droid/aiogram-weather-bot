from aiogram_dialog.widgets.kbd import Cancel, SwitchTo

from src.bot.dialogs.flows.weather.states import WeatherSG
from src.bot.dialogs.widgets.i18n import I18nFormat

MAIN_SETTINGS_BUTTON = Cancel(
    text=I18nFormat("back-button"),
    id="reply_back_button",
)

TASK_SETTINGS_BUTTON = SwitchTo(
    text=I18nFormat("back-button"),
    id="reply_back_button_from_group_task",
    state=WeatherSG.weather_group_task_settings,
)
