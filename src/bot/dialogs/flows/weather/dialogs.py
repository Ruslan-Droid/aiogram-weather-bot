from pathlib import Path

from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Checkbox, RequestLocation, Row, Url, ScrollingGroup, Select, Radio
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Format, Const
from sqlalchemy.orm.base import state_str

from src.bot.dialogs.flows.registration.handlers import location_handler, wrong_location_handler
from src.bot.dialogs.flows.weather.keyboards import (
    MAIN_SETTINGS_BUTTON, TASK_SETTINGS_BUTTON,
)
from src.bot.dialogs.widgets.i18n import I18nFormat
from src.bot.dialogs.flows.weather.states import WeatherSG
from src.bot.dialogs.flows.weather.getters import (
    getter_weather_main_menu,
    getter_weather_settings,
    getter_weather_time_settings,
    getter_weather_city_settings,
    getter_weather_changing_city,
    getter_weather_group_settings,
    getter_edit_group_settings,
    getter_group_task_settings,
    getter_edit_group_language, getter_edit_group_timezone, getter_timezone_changing,
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
    weather_notification_clicked,
    go_to_group_settings_on_click,
    group_click_handler,
    go_to_group_task1_settings_on_click,
    go_to_group_task2_settings_on_click,
    group_task_change_time_on_click,
    group_settings_change_language_on_click,
    group_task_toggle_notifications_on_click,
    go_back_to_group_settings,
    group_task_time_handler,
    go_back_to_group_task_settings,
    group_task_change_city_on_click,
    group_task_change_coords_on_click,
    group_task_city_handler,
    group_task_coords_handler,
    group_settings_save_language_on_click, save_group_task_city_on_click, group_settings_change_time_zone_on_click,
    group_task_city_for_timezone_handler, save_group_timezone_on_click,
)

weather_dialog = Dialog(
    # ☁️ Main weather menu
    Window(
        I18nFormat("main-weather-dialog"),
        # ☁️ weather now
        Button(
            text=Format("{weather_now}"),
            id="weather_now_button",
            on_click=send_today_weather_on_click,
        ),
        # 📆 weather forecast
        Button(
            text=Format("{weather_forecast}"),
            id="weather_forecast_button",
            on_click=send_today_forecast_on_click,
        ),
        # 🔴 weather notification checkbox
        Checkbox(
            checked_text=Format("{off_notification}"),
            unchecked_text=Format("{on_notification}"),
            id="weather_notification_checkbox",
            default=False,
            on_state_changed=weather_notification_clicked,
        ),
        # ⚙️ general settings button
        Button(
            text=Format("{main_settings}"),
            id="main_settings_button",
            on_click=go_to_general_settings_on_click,
        ),
        # 👥 button to add bot in group
        Url(
            text=Format("{add_group_button}"),
            url=Const("https://t.me/KLG_Weather_Bot?startgroup=newgroups&admin=manage_chat+delete_messages"),
            id="add_group_button",
        ),
        # 👥⚙️ button for group settings
        Button(
            text=Format("{group_settings}"),
            id="group_settings_button",
            on_click=go_to_group_settings_on_click,
        ),
        getter=getter_weather_main_menu,
        state=WeatherSG.weather_main_menu,
    ),
    # ☁️ Main weather menu -> ⚙️ General settings menu
    Window(
        Format("{general_settings_weather_settings}"),
        # 🌎 language settings button
        Button(
            text=Format("{language_settings_button}"),
            id="language_settings_button",
            on_click=change_language_on_click,
        ),
        # ⏰ change time notification button
        Button(
            text=Format("{settings_change_time_notification_button}"),
            id="settings_change_time_notification_button",
            on_click=change_notification_time_on_click,
        ),
        # 🗺 change coords button
        Button(
            text=Format("{coords_settings_button}"),
            id="settings_change_coords_button",
            on_click=change_coords_on_click,
        ),
        # 🏡 change city button
        Button(
            text=Format("{change_city_button}"),
            id="change_city_button",
            on_click=change_city_on_click,
        ),
        # ◀️ back button
        Button(
            text=Format("{back_button}"),
            id="settings_back_button",
            on_click=go_to_main_menu_on_click,
        ),
        getter=getter_weather_settings,
        state=WeatherSG.weather_general_settings,
    ),
    # ☁️ Main weather menu -> ⚙️ General settings menu ->  ⏰ change time
    Window(I18nFormat("start-change-time-notification"),
           # ◀️ back button
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
    # ☁️ Main weather menu -> ⚙️ General settings menu -> 🗺 change coords
    Window(
        StaticMedia(
            path=Path("src", "bot", "dialogs", "flows", "registration", "media", "new.mp4"),
            type=ContentType.ANIMATION,
        ),
        RequestLocation(I18nFormat("keyboard-coords")),
        # ◀️ back button
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
    # ☁️ Main weather menu -> ⚙️ General settings menu -> 🏡 change city
    Window(
        I18nFormat("start-change-city"),
        # ◀️ back button
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
    # ☁️ Main weather menu -> ⚙️ General settings menu -> 🏡 change city -> ✅ save chosen city
    Window(
        Format("{current_city}"),
        Row(
            # ◀️ back button
            Button(
                text=Format("{back_button}"),
                id="city_back_button",
                on_click=deny_city_on_click,
            ),
            # ✅ Save button
            Button(
                text=Format("{save_button}"),
                id="city_save_button",
                on_click=save_city_on_click,
            ),
        ),
        getter=getter_weather_changing_city,
        state=WeatherSG.weather_save_city,
    ),
    # ☁️ Main weather menu -> 👥⚙️ Groups settings menu
    Window(
        Format("{group_settings_window}"),
        # 👥 buttons with groups titles
        ScrollingGroup(
            Select(
                text=Format("{item[title]}"),
                id="s_groups",
                item_id_getter=lambda x: x["group_telegram_id"],
                items="groups_data",
                on_click=group_click_handler
            ),
            id="group_scroll",
            width=1,
            height=5,
        ),
        # ◀️ back button
        Button(
            text=Format("{back_button}"),
            id="group_settings_back_button",
            on_click=go_to_main_menu_on_click),
        getter=getter_weather_group_settings,
        state=WeatherSG.weather_groups_list_to_edit,

    ),
    # ☁️ Main weather menu -> 👥⚙️ Groups settings menu -> 👥 edit chosen group
    Window(
        Format("{group_current_settings}"),
        # 🌎 edit language for group button
        Button(
            text=Format("{edit_language_for_groups_message}"),
            id="edit_language_for_groups_message_button",
            on_click=group_settings_change_language_on_click,
        ),
        # ⌚️ edit time zone for group button
        Button(
            text=Format("{edit_tz_region_button}"),
            id="edit_group_tz_region_button",
            on_click=group_settings_change_time_zone_on_click,
        ),
        # 🎯 task №1 button
        Button(
            text=Format("{task1_button}"),
            id="group_task_1_button",
            on_click=go_to_group_task1_settings_on_click,
        ),
        # 🎯 task №2 button
        Button(
            text=Format("{task2_button}"),
            id="group_task_2_button",
            on_click=go_to_group_task2_settings_on_click,
        ),
        # ◀️ back button
        Button(
            text=Format("{back_button}"),
            id="group_settings_back_button",
            on_click=go_to_group_settings_on_click),
        getter=getter_edit_group_settings,
        state=WeatherSG.weather_edit_group,
    ),
    # ☁️ Main weather menu -> 👥⚙️ Groups settings menu -> 👥 edit chosen group -> 🌎 edit language
    Window(
        Format("{language_group_window}"),
        ScrollingGroup(
            Radio(
                checked_text=Format("🔘 {item[0]}"),
                unchecked_text=Format("⚪️ {item[0]}"),
                id="radio_lang_group",
                item_id_getter=lambda x: x[1],
                items="lang_group_buttons",
            ),
            id="lang_group_scroll",
            width=1,
            height=5,
            hide_on_single_page=True,
        ),
        Row(
            Button(
                text=Format("{back_button}"),
                id="set_group_lang_back_button_click",
                on_click=go_back_to_group_settings,
            ),
            Button(
                text=Format("{save_button}"),
                id="save_group_lang_button_click",
                on_click=group_settings_save_language_on_click,
            ),
        ),
        getter=getter_edit_group_language,
        state=WeatherSG.weather_edit_group_language,
    ),
    # ☁️ Main weather menu -> 👥⚙️ Groups settings menu -> 👥 edit chosen group -> ⌚️ change time zone
    Window(
        I18nFormat("start-change-city"),
        Button(
            text=Format("{back_button}"),
            id="group_task_back_button",
            on_click=go_back_to_group_settings,
        ),
        MessageInput(
            func=group_task_city_for_timezone_handler,
            content_types=ContentType.TEXT
        ),
        MessageInput(
            func=wrong_city_handler,
            content_types=ContentType.ANY
        ),
        state=WeatherSG.weather_edit_group_timezone,
        getter=getter_edit_group_timezone,

    ),
    # ☁️ Main weather menu -> 👥⚙️ Groups settings menu -> 👥 edit chosen group -> ⌚️ save time zone
    Window(
        Format("{current_timezone}"),
        Row(
            # ◀️ back button
            Button(
                text=Format("{back_button}"),
                id="group_timezone_back_button",
                on_click=group_settings_change_time_zone_on_click,
            ),
            # ✅ Save button
            Button(
                text=Format("{save_button}"),
                id="group_timezone_save_button",
                on_click=save_group_timezone_on_click,
            ),
        ),
        getter=getter_timezone_changing,
        state=WeatherSG.weather_edit_group_save_timezone,
    ),
    # ☁️ Main weather menu -> 👥⚙️ Groups settings menu -> 👥 edit chosen group -> 🎯 edit chosen task for group
    Window(
        Format("{group_task_settings_window}"),
        Button(
            text=Format("{change_time_button}"),
            id="group_task_change_time_button",
            on_click=group_task_change_time_on_click,
        ),
        Button(
            text=Format("{change_city_button}"),
            id="change_city_button",
            on_click=group_task_change_city_on_click,
        ),
        Button(
            text=Format("{change_coords_button}"),
            id="change_coords_button",
            on_click=group_task_change_coords_on_click,
        ),
        Button(
            text=Format("{toggle_notifications_button}"),
            id="group_task_toggle_notifications_button",
            on_click=group_task_toggle_notifications_on_click,
        ),
        Button(
            text=Format("{back_button}"),
            id="group_task_back_button",
            on_click=go_back_to_group_settings,
        ),
        getter=getter_group_task_settings,
        state=WeatherSG.weather_group_task_settings,
    ),

    # ☁️ Main weather menu -> 👥⚙️ Groups settings menu -> 👥 edit chosen group -> 🎯 edit chosen task for group -> ⏰ edit time
    Window(
        I18nFormat("start-change-time-notification"),
        Button(
            text=Format("{back_button}"),
            id="group_task_back_button",
            on_click=go_back_to_group_task_settings,
        ),
        MessageInput(
            func=group_task_time_handler,
            content_types=ContentType.TEXT,
        ),
        MessageInput(
            func=wrong_time_handler,
            content_types=ContentType.ANY
        ),
        getter=getter_weather_time_settings,
        state=WeatherSG.weather_group_task_changing_time,
    ),

    # ☁️ Main weather menu -> 👥⚙️ Groups settings menu -> 👥 edit chosen group -> 🎯 edit chosen task for group -> 🏡 edit city
    Window(
        I18nFormat("start-change-city"),
        Button(
            text=Format("{back_button}"),
            id="group_task_back_button",
            on_click=go_back_to_group_task_settings,
        ),
        MessageInput(
            func=group_task_city_handler,
            content_types=ContentType.TEXT
        ),
        MessageInput(
            func=wrong_city_handler,
            content_types=ContentType.ANY
        ),
        getter=getter_weather_city_settings,
        state=WeatherSG.weather_group_task_changing_city,
    ),
    # ☁️ Main weather menu -> 👥⚙️ Groups settings menu -> 👥 edit chosen group -> 🎯 edit chosen task for group -> 🏡 edit city -> ✅ save chosen city
    Window(
        Format("{current_city}"),
        Row(
            # ◀️ back button
            Button(
                text=Format("{back_button}"),
                id="group_city_back_button",
                on_click=group_task_change_city_on_click,
            ),
            # ✅ Save button
            Button(
                text=Format("{save_button}"),
                id="group_city_save_button",
                on_click=save_group_task_city_on_click,
            ),
        ),
        getter=getter_weather_changing_city,
        state=WeatherSG.weather_group_task_save_city,
    ),
    # ☁️ Main weather menu -> 👥⚙️ Groups settings menu -> 👥 edit chosen group -> 🎯 edit chosen task for group -> 🗺 edit coords
    Window(
        StaticMedia(
            path=Path("src", "bot", "dialogs", "flows", "registration", "media", "new.mp4"),
            type=ContentType.ANIMATION,
        ),
        RequestLocation(I18nFormat("keyboard-coords")),
        TASK_SETTINGS_BUTTON,
        MessageInput(
            func=group_task_coords_handler,
            content_types=ContentType.LOCATION
        ),
        MessageInput(
            func=wrong_location_handler,
            content_types=ContentType.ANY
        ),
        markup_factory=ReplyKeyboardFactory(resize_keyboard=True),
        state=WeatherSG.weather_group_task_changing_coords,
    ),
    name="weather_main_dialog",
)
