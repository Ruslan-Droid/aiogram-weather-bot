start-hello =
    Привет, <b>{ $username }!</b>

    Отправь свои координаты для завершения регистрации и дальнейшего получения прогноза погоды.

    Для отправкии координат нажми на скрепку и поделись локацией.

    Либо нажми на кнопку ниже - <b>Отправить координаты</b>!

start-finish-registration =
    Координаты успешно установлены:

    широта = { $latitude },
    долгота = { $longitude }.

start-change-time-notification =
    Отправьте в чат время в которое вы хотите получать ежедневный прогноз погоды в формате "XX:XX".

    Пример:

    09:00

time-changed-successfully =
    Время изменено успешно:

    <b>{ $time }</b> ✅

start-change-city =
    Напишите ваш город.

    Пример:

    Москва

city-found-successfully =
    Ваш город успешно найден:  <b>{ $city_name }</b> ✅

    Полный адрес:
    { $city_info }

city-not-found =
    Ваш город не найден.

    Укажите корректное наименование.

keyboard-coords = Отправить координаты


error-input-registration = Отправьте координаты нажав на кнопку внизу или отправьте через локацию через скрепку.
error-input-time =
    Отправьте время в чат в формате:

    09:00

start-command-description = Перезапустить бота
lang-command-description = Настроить язык интерфейса
help-command-description = Посмотреть справку по работе бота

help-command = Пример.

back-button = ◀️ Назад
save-button = ✅ Сохранить

set-lang-menu =
    <b>Пожалуйста, выберите язык интерфейса бота</b>

    Выбран 🇷🇺 <b>Русский язык</b>

ru-lang = 🇷🇺 Русский
en-lang = 🇬🇧 Английский
lang-saved = ✅ Настройки языка успешно сохранены!

weather-now-button = ☁️ Погода сейчас ️️
weather-forecast-button = 📆 Прогноз погоды на сегодня
main-settings-button = ⚙️ Общие настройки бота
add-group-button = 👥 Добавить бота в группу
group-settings-button = 👥⚙️ Настроить бота в группе
language-settings-button = 🌎 Настроить язык
settings-change-time-notification-button = ⏰ Изменить время уведомлений
coords-settings-button = 🗺 Изменить координаты
change-city-button = 🏡 Отправить город
off-notification-button = 🟢  Рассылка погоды включена
on-notification-button = 🔴  Рассылка погоды отключена

notification-time-alert =
    Время ежедневной рассылки:

    { $time }

    Время можно изменить в общих настройках бота.

main-weather-dialog =
    WeatherBot⛅️ @KLG_Weather_Bot:

    Для получения прогноза погоды, нажми на кнопку ниже:

general-settings-weather-settings =
    Основные настройки WeatherBot⛅️:
    Язык = <b>{ $language_settings }</b>
    Время ежедневного прогноза = <b>{ $time_settings }</b>
    Координаты = <b>{ $coords_settings }</b>
    Город = <b>{ $city_settings }</b>

parsing-weather-time = Время
parsing-weather-temperature = Температура
parsing-weather-feels-like = Ощущается как
parsing-weather-current = Погода
parsing-weather-wind = Ветер

parsing-weather-forecast-day = Прогноз погоды на день

bot-added-as-admin =
    Для того чтобы включи и настроить время перейдите в основной чат с ботом.

    Настройки для группы доступны только <b>администратору</b> группы ❗️❗️


bot-added-not-as-admin = Чтобы бот мог отправлять ежедневную погоду добавьте ему права администратора.

bot-lost-admin-rights =
    Бот лишен прав администратора.

    Он больше не сможет отправлять погоду в чат.

bot-get-admin-rights =
    Бот получил права администратора.

    Теперь он сможет отправлять погоду в чат.

    Администратор группы может настроить бота в личных сообщениях с ботом.

bot-update-admin-list =
    Бот успешно обновил список текущих администраторов.

    Администратор может зайти в личные сообщения с ботом и настроить его для данной группы.

user-lost-admin-rights = { $name }, больше не сможет настраивать бота для этой группы.

user-lost-admin-rights = { $name }, теперь может настраивать бота для этой группы.


group-settings-window =
    Выберите группу которую хотите настроить.

    Настраивать и добавлять бота в группу может только администратор этой группы.