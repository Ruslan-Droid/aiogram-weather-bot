start-hello =
    Hello, <b>{ $username }!</b>

    Send your coordinates or your city to complete registration and receive weather forecasts.

    To send your coordinates, click the paperclip and share the location.

    Or click the button below - <b>Send coordinates</b>!

start-finish-registration =
    Coordinates successfully set:

    latitude = { $latitude },
    longitude = { $longitude }.

city-finish-registration =
    City successfully set: { $city }


start-change-time-notification =
    Send in the chat the time at which you want to receive the daily weather forecast in the format "XX:XX".

    Example:

    09:00

time-changed-successfully =
    Time changed successfully:

    <b>{ $time }</b> ✅

start-change-city =
    Write your city.

    Example:

    London

city-found-successfully =
    Your city was successfully found:  <b>{ $city_name }</b> ✅

    Full address:
    { $city_info }

city-not-found =
    Your city was not found.

    Please enter a valid name.

keyboard-coords = Send coords


error-input-registration = Send coordinates by clicking the button below or send them via the location using a paperclip.
error-input-time =
    Send time to chat in the format:

    09:00

start-command-description = Restart the bot
lang-command-description = Configure the interface language
help-command-description = View the help for the bot

help-command =
    The following commands are available in the bot:

    /start - restart the bot
    /lang - change language
    /help - information about bpt

    If the dialog box disappears, type any message to the bot, and the dialog box will reappear.

    For support inquiries: @DarkGrayCaesar
    Project on Github: https://github.com/Ruslan-Droid/aiogram-weather-bot

support-button = Support
github-button =  Project on github


back-button = ◀️ Back
save-button = ✅ Save

set-lang-menu =
    <b>Please select the language of the bot interface</b>

    The 🇬🇧 <b>English</b> language is selected

ru-lang = 🇷🇺 Russian
en-lang = 🇬🇧 English
lang-saved = ✅ The language settings have been saved successfully!

weather-now-button = ☁️ Weather now
weather-forecast-button = 📆 Weather forecast for today
main-settings-button = ⚙️ General bot settings
add-group-button = 👥 Add bot to a group as admin
group-settings-button = 👥⚙️ Bot settings in a group
language-settings-button = 🌎 Change language
settings-change-time-notification-button = ⏰ Change notification time
coords-settings-button = 🗺 Change coords
change-city-button = 🏡 Send city
off-notification-button = 🟢 Weather alerts are enabled.
on-notification-button = 🔴 Weather alerts are disabled.

notification-time-alert =
    Daily notification time:

    { $time }

    The time can be changed in general bot settings.

main-weather-dialog =
    WeatherBot⛅️ @KLG_Weather_Bot.

    To get the weather forecast, click the button below:

general-settings-weather-settings =
    General WeatherBot⛅️ settings:

    🌎 Language: <b>{ $language_settings }</b>
    ⏰ Notification time: <b>{ $time_settings }</b>
    🗺 Coords: <b>{ $coords_settings }</b>
    🏡 City: <b>{ $city_settings }</b>

parsing-weather-time = Time
parsing-weather-temperature = Temperature
parsing-weather-feels-like = Feels like
parsing-weather-current = Weather
parsing-weather-wind = Wind

parsing-weather-forecast-day = Weather forecast for the day

bot-added-as-admin =
    To enable it and set the time, go to the main chat with the bot.

    Group settings are only available to the group <b>administrator</b> ❗️❗️

bot-added-not-as-admin = To allow the bot to send daily weather, add administrator rights to it.

bot-lost-admin-rights =
    The bot has been stripped of its administrator rights.

    It will no longer be able to send weather information to the chat.

bot-get-admin-rights =
    The bot has been granted administrator rights.

    It can now send weather information to the chat.

    The group administrator can configure the bot via private messages.

bot-update-admin-list =
    The bot has successfully updated the list of current administrators.

    The administrator can private message the bot and configure it for this group.

user-lost-admin-rights = { $name }, will no longer be able to configure the bot for this group.

user-get-admin-rights = { $name }, can now configure a bot for this group.


group-settings-window =
    Select the group you want to configure.

    Only the group administrator can configure and add a bot to a group.

no-groups = No groups

group-current-settings =
    Main settings <b>{ $title }</b>:
    🌎  Language for group:  <b>{ $language }</b>
    ⌚️  Timezone for group:  <b>{ $timezone }</b>

    You can set up to 2 daily weather alerts to a group.

task1-button = Daily weather №1 🎯

task2-button = Daily weather №2 🎯

edit-language-for-groups-message = 🌎 Change language for а group

edit-tz-region-button = ⌚️ Set up a time zone for a group

location-is-none = is empty

timezone-found = The time zone for the entered city: <b>{ $timezone }</b>
timezone-saved = Timezone saved successfully: { $timezone }

group-task-settings-window =
    <b>Task №{ $task_number }</b> settings:
    ⏰ Time: <b>{ $notification_time }</b>
    🏡 City: <b>{ $city }</b>
    🗺 Coords: <b>{ $coords }</b>
    🔔 Notifications: <b>{ $notifications_enabled }</b>

notifications-off = 🚫 Daily forecast off
notifications-on = ✅ Daily forecast on

language-group-window =  <b>Please select a language for bot messages in the group</b>
choose-language = Choose language!

group-not-found = Group not found!

chosen-group =  The { $group_name } group is selected

notifications-on-for-group-task = Notifications for task { $task_number } are enabled at { $notification_time }

notifications-off-for-group-task = Notifications for task { $task_number } are disabled\

choose-city-or-coords = To enable notifications, add a city or coordinates!

button-with-bot-link = 🤖 Go to bot