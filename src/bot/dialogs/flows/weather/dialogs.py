from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Checkbox
from aiogram_dialog.widgets.text import Format

from src.bot.dialogs.widgets.i18n import I18nFormat
from src.bot.dialogs.flows.weather.states import WeatherSG
from src.bot.dialogs.flows.weather.getters import (
    getter_weather_main_menu,
    getter_weather_settings
)
from src.bot.dialogs.flows.weather.handlers import (
    send_today_weather_on_click,
    send_today_forecast_on_click,
    send_general_settings_on_click,
    go_to_main_menu_on_click,
    change_language_on_click,
    weather_notification_clicked,
)

weather_dialog = Dialog(
    # Main weather menu
    Window(
        I18nFormat("main-weather-dialog"),
        Button(
            text=Format("{weather_now}"),
            id="weather_now_button",
            on_click=send_today_weather_on_click,
        ),
        Button(
            text=Format("{weather_forecast}"),
            id="weather_forecast_button",
            on_click=send_today_forecast_on_click,
        ),
        Checkbox(
            checked_text=Format("{off_notification}"),
            unchecked_text=Format("{on_notification}"),
            id="weather_notification_checkbox",
            default=False,
            on_state_changed=weather_notification_clicked,
        ),
        Button(
            text=Format("{main_settings}"),
            id="main_settings_button",
            on_click=send_general_settings_on_click,
        ),
        getter=getter_weather_main_menu,
        state=WeatherSG.weather_main_menu,
    ),
    # General settings menu
    Window(
        I18nFormat("general-settings-weather-dialog"),
        Button(
            text=Format("{language_settings_button}"),
            id="language_settings_button",
            on_click=change_language_on_click,
        ),
        Button(
            text=Format("{back_button}"),
            id="settings_back_button",
            on_click=go_to_main_menu_on_click,
        ),
        getter=getter_weather_settings,
        state=WeatherSG.weather_general_settings,
    ),
)
