start-hello =
    Привет, <b>{ $username }!</b>

    Отправь свои координаты или свой город для завершения регистрации и дальнейшего получения прогноза погоды.

    Для отправкии координат нажми на скрепку и поделись локацией.

    Либо нажми на кнопку ниже - <b>Отправить координаты</b>!

start-finish-registration =
    Координаты успешно установлены:

    широта = { $latitude },
    долгота = { $longitude }.

city-finish-registration =
    Город успешно установлен: { $city }

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
add-group-button = 👥 Добавить бота в группу админом
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

    🌎 Язык = <b>{ $language_settings }</b>
    ⏰ Время ежедневного прогноза = <b>{ $time_settings }</b>
    🗺 Координаты = <b>{ $coords_settings }</b>
    🏡 Город = <b>{ $city_settings }</b>

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

user-get-admin-rights = { $name }, теперь может настраивать бота для этой группы.


group-settings-window =
    Выберите группу которую хотите настроить.

    Настраивать и добавлять бота в группу может только администратор этой группы.

no-groups = Нет групп

group-current-settings =
    Основные настройки <b>{ $title }</b>:

    🌎 Язык для группы: <b>{ $language }</b>

    Можно настроить до 2-х рахных ежедневных рассылок погоды в группу.

task1-button = Ежедневная погода №1 🎯

task2-button = Ежедневная погода №2 🎯

edit-language-for-groups-message = 🌎 Настроить язык для группы

location-is-none = не установлена

group-task-settings-window =
    Настройки <b>задачи №{ $task_number }</b>:
    ⏰ Время: <b>{ $notification_time }</b>
    🏡 Город: <b>{ $city }</b>
    🗺 Координаты: <b>{ $coords }</b>
    🔔 Уведомления: <b>{ $notifications_enabled }</b>

notifications-off = 🚫 Рассылка отключена
notifications-on = ✅ Рассылка включены

language-group-window =  <b>Пожалуйста, выберите язык сообщений бота в группе</b>
choose-language = Выбери язык!

group-not-found = Группа не найдена!

chosen-group =  Выбрана группа { $group_name }

notifications-on-for-group-task = Уведомления для задачи { $task_number } включены на { $notification_time }

notifications-off-for-group-task = Уведомления для задачи { $task_number } выключены

choose-city-or-coords = Чтобы включить уведомления добавьте город или координаты!

button-with-bot-link = 🤖 Перейти в бота