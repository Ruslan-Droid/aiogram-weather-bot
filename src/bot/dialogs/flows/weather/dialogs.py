from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format

from src.bot.dialogs.widgets.i18n import I18nFormat
from src.bot.dialogs.flows.weather.states import WeatherSG
from src.bot.dialogs.flows.weather.getters import getter_weather
from src.bot.dialogs.flows.weather.handlers import send_today_weather_on_click

weather_dialog = Dialog(
    Window(
        I18nFormat("main-weather-dialog"),
        Button(
            text=Format("weather_now"),
            id="weather_now",
            on_click=send_today_weather_on_click,
        ),
        getter=getter_weather,
        state=WeatherSG.weather_main_menu,
    )
)
