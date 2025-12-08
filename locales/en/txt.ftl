start-hello =
    Hello, <b>{ $username }!</b>

    Send your coordinates to complete registration and receive weather forecasts.

    To send your coordinates, click the paperclip and share the location.

    Or click the button below - <b>Send coordinates</b>!

start-finish-registration =
    Coordinates successfully set:

    latitude = { $latitude },
    longitude = { $longitude }.

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
    Your city was successfully found and changed:  <b>{ $city_name }</b> ✅

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

help-commad = Example.

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
add-group-button = 👥 Add bot to a group
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
    Language: <b>{ $language_settings }</b>
    Notification time: <b>{ $time_settings }</b>
    Coords: <b>{ $coords_settings }</b>
    City: <b>{ $city_settings }</b>

parsing-weather-time = Time
parsing-weather-temperature = Temperature
parsing-weather-feels-like = Feels like
parsing-weather-current = Weather
parsing-weather-wind = Wind

parsing-weather-forecast-day = Weather forecast for the day

bot-added-as-admin =
    The bot has been added to the group as an administrator.

    It will now be able to send daily weather reports.

    To enable it and set the time, go to the main chat with the bot.

bot-added-not-as-admin = To allow the bot to send daily weather, add administrator rights to it.