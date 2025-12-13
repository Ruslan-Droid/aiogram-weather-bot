from pathlib import Path

from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Checkbox, RequestLocation, Row, Url
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Format, Const

from src.bot.dialogs.flows.registration.handlers import location_handler, wrong_location_handler
from src.bot.dialogs.flows.weather.keyboards import (
    MAIN_SETTINGS_BUTTON,
)
from src.bot.dialogs.widgets.i18n import I18nFormat
from src.bot.dialogs.flows.weather.states import WeatherSG
from src.bot.dialogs.flows.weather.getters import (
    getter_weather_main_menu,
    getter_weather_settings,
    getter_weather_time_settings,
    getter_weather_city_settings,
    getter_weather_changing_city, getter_weather_group_settings,
)
from src.bot.dialogs.flows.weather.handlers import (
    send_today_weather_on_click,
    send_today_forecast_on_click,
    go_to_general_settings_on_click,
    go_to_main_menu_on_click,
    change_language_on_click,
    change_notification_time_on_click,
    time_handler,
    wrong_time_handler,
    change_coords_on_click,
    change_city_on_click,
    city_handler,
    wrong_city_handler,
    save_city_on_click,
    deny_city_on_click,
    weather_notification_clicked, go_to_group_settings_on_click, deny_choosing_group_on_click, group_click_handler,
)
from src.bot.dialogs.widgets.scroll_widget import DynamicScrollingGroup

weather_dialog = Dialog(
    # Main weather menu
    Window(
        I18nFormat("main-weather-dialog"),
        # weather now
        Button(
            text=Format("{weather_now}"),
            id="weather_now_button",
            on_click=send_today_weather_on_click,
        ),
        # weather forecast
        Button(
            text=Format("{weather_forecast}"),
            id="weather_forecast_button",
            on_click=send_today_forecast_on_click,
        ),
        # weather notification checkbox
        Checkbox(
            checked_text=Format("{off_notification}"),
            unchecked_text=Format("{on_notification}"),
            id="weather_notification_checkbox",
            default=False,
            on_state_changed=weather_notification_clicked,
        ),
        # general settings button
        Button(
            text=Format("{main_settings}"),
            id="main_settings_button",
            on_click=go_to_general_settings_on_click,
        ),
        # button to add bot in group
        Url(
            text=Format("{add_group_button}"),
            url=Const("https://t.me/KLG_Weather_Bot?startgroup=newgroups&admin=manage_chat+delete_messages"),
            id="add_group_button",
        ),
        # button for group settings
        Button(
            text=Format("{group_settings}"),
            id="group_settings_button",
            on_click=go_to_group_settings_on_click,
        ),
        getter=getter_weather_main_menu,
        state=WeatherSG.weather_main_menu,
    ),
    # General settings menu
    Window(
        Format("{general_settings_weather_settings}"),
        # language settings button
        Button(
            text=Format("{language_settings_button}"),
            id="language_settings_button",
            on_click=change_language_on_click,
        ),
        # change time notification button
        Button(
            text=Format("{settings_change_time_notification_button}"),
            id="settings_change_time_notification_button",
            on_click=change_notification_time_on_click,
        ),
        # change coords button
        Button(
            text=Format("{coords_settings_button}"),
            id="settings_change_coords_button",
            on_click=change_coords_on_click,
        ),
        # change city button
        Button(
            text=Format("{change_city_button}"),
            id="change_city_button",
            on_click=change_city_on_click,
        ),
        # back button
        Button(
            text=Format("{back_button}"),
            id="settings_back_button",
            on_click=go_to_main_menu_on_click,
        ),
        getter=getter_weather_settings,
        state=WeatherSG.weather_general_settings,
    ),
    # From General settings to changing time
    Window(I18nFormat("start-change-time-notification"),
           Button(
               text=Format("{back_button}"),
               id="settings_back_button",
               on_click=go_to_general_settings_on_click,
           ),
           MessageInput(
               func=time_handler,
               content_types=ContentType.TEXT,
           ),
           MessageInput(
               func=wrong_time_handler,
               content_types=ContentType.ANY
           ),
           getter=getter_weather_time_settings,
           state=WeatherSG.weather_changing_time,
           ),
    # From General settings to changing coords
    Window(
        StaticMedia(
            path=Path("src", "bot", "dialogs", "flows", "registration", "media", "new.mp4"),
            type=ContentType.ANIMATION,
        ),
        RequestLocation(I18nFormat("keyboard-coords")),
        MAIN_SETTINGS_BUTTON,
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
        state=WeatherSG.weather_changing_coords,
    ),
    # from general settings to changing city
    Window(
        I18nFormat("start-change-city"),
        Button(
            text=Format("{back_button}"),
            id="settings_back_button",
            on_click=go_to_general_settings_on_click,
        ),
        MessageInput(
            func=city_handler,
            content_types=ContentType.TEXT
        ),
        MessageInput(
            func=wrong_city_handler,
            content_types=ContentType.ANY
        ),
        state=WeatherSG.weather_changing_city,
        getter=getter_weather_city_settings,
    ),
    # from changing city to save or deny changes
    Window(
        Format("{current_city}"),
        Row(
            Button(
                text=Format("{back_button}"),
                id="city_back_button",
                on_click=deny_city_on_click,
            ),
            Button(
                text=Format("{save_button}"),
                id="city_save_button",
                on_click=save_city_on_click,
            ),
        ),
        getter=getter_weather_changing_city,
        state=WeatherSG.weather_save_city,
    ),
    # Group settings menu
    Window(
        Format("{group_settings_window}"),
        DynamicScrollingGroup.create(
            groups_data=Format({"groups_data"}),
            on_click_handler=group_click_handler,
        ),
        Button(
            text=Format("{back_button}"),
            id="group_settings_back_button",
            on_click=deny_choosing_group_on_click),
        getter=getter_weather_group_settings,
        state=WeatherSG.weather_group_settings,

    ),
    name="weather_main_dialog",
)
