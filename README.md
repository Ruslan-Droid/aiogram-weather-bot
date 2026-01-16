# Aiogram 3 Weather Bot
<img src="https://github.com/Ruslan-Droid/aiogram-weather-bot/actions/workflows/deploy.yml/badge.svg?branch=master" /> <img src="https://img.shields.io/github/v/release/Ruslan-Droid/aiogram-weather-bot?sort=semver&label=stable" />


https://t.me/KLG_Weather_Bot

This is a weather bot written in python using the `aiogram` framework

## About the bot

### Used technology

* Python 3.13.5;
* aiogram 3.x (Asynchronous Telegram Bot framework);
* aiogram_dialog (GUI framework for telegram bot);
* dynaconf (Configuration Management for Python);
* taskiq (Async Distributed Task Manager);
* fluentogram (Internationalization tool in the Fluent paradigm);
* Docker and Docker Compose (containerization);
* PostgreSQL (database);
* SQLAlchemy (ORM for SQL database);
* NATS (queue and delay tasks);
* Redis (FSM storage, cache, taskiq result backend);
* Alembic (database migrations with raw SQL).
  
### Used services
* https://www.weatherapi.com/ - API to get weather
* https://www.openstreetmap.org/ - API for checking the availability of a city

### Structure

```
📁 aiogram-weather-bot/
├── 📁 .github
│   └── 📁 workflows
│       ├── deploy.yml
│       └── rollback.yml
├── 📁 config
│   ├── config.py
│   └── settings.toml
├── 📁 locales
│   ├── 📁 en
│   │   └── txt.ftl
│   └── 📁 ru
│       └── txt.ftl
├── 📁 migration
│   ├── env.py
│   ├── script.py.mako
│   └── 📁 versions
├── 📁 nats_broker
│   ├── nats_connect.py
│   ├── 📁 config
│   │   └── server.conf
│   └── 📁 migrations
│       └── create_stream.py
├── 📁 src
│   ├── 📁 bot
│   │   ├── app_factory.py
│   │   ├── bot.py
│   │   ├── __init__.py
│   │   ├── 📁 dialogs
│   │   │   ├── 📁 flows
│   │   │   │   ├── __init__.py
│   │   │   │   ├── 📁 language_settings
│   │   │   │   │   ├── dialogs.py
│   │   │   │   │   ├── getters.py
│   │   │   │   │   ├── handlers.py
│   │   │   │   │   ├── keyboards.py
│   │   │   │   │   └── states.py
│   │   │   │   ├── 📁 registration
│   │   │   │   │   ├── dialogs.py
│   │   │   │   │   ├── getters.py
│   │   │   │   │   ├── handlers.py
│   │   │   │   │   ├── keyboards.py
│   │   │   │   │   ├── states.py
│   │   │   │   │   └── 📁 media
│   │   │   │   │       └── new.mp4
│   │   │   │   └── 📁 weather
│   │   │   │       ├── dialogs.py
│   │   │   │       ├── getters.py
│   │   │   │       ├── handlers.py
│   │   │   │       ├── keyboards.py
│   │   │   │       └── states.py
│   │   │   └── 📁 widgets
│   │   │       └── i18n.py
│   │   ├── 📁 enums
│   │   │   ├── actions.py
│   │   │   └── group_data.py
│   │   ├── 📁 filters
│   │   │   └── chat_type_filters.py
│   │   ├── 📁 handlers
│   │   │   ├── commands.py
│   │   │   ├── errors.py
│   │   │   ├── groups.py
│   │   │   ├── user_statuses.py
│   │   │   └── __init__.py
│   │   ├── 📁 keyboards
│   │   │   ├── inline_keyboards.py
│   │   │   └── menu_button.py
│   │   ├── 📁 middlewares
│   │   │   ├── database.py
│   │   │   ├── get_group.py
│   │   │   ├── get_user.py
│   │   │   ├── i18n.py
│   │   │   └── shadow_ban.py
│   │   ├── 📁 services
│   │   │   ├── group_admin_service.py
│   │   │   └── time_checker.py
│   │   └── 📁 states
│   │       └── states.py
│   ├── 📁 infrastructure
│   │   ├── 📁 cache
│   │   │   ├── connect_to_redis_pool.py
│   │   │   └── __init__.py
│   │   └── 📁 database
│   │       ├── dao.py
│   │       ├── db.py
│   │       └── models.py
│   └── 📁 services
│       ├── 📁 delay_service
│       │   ├── consumer.py
│       │   ├── publisher.py
│       │   ├── start_consumer.py
│       │   └── 📁 models
│       │       └── delayed_messages.py
│       ├── 📁 i18n
│       │   └── translator_hub.py
│       ├── 📁 open_street_map_api
│       │   ├── city_parsing.py
│       │   └── city_service.py
│       ├── 📁 scheduler
│       │   ├── taskiq_broker.py
│       │   └── tasks.py
│       └── 📁 weather_api
│           ├── weather_emojis.py
│           ├── weather_parsing.py
│           └── weather_service.py
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── main.py
├── pyproject.toml
├── README.md
└── uv.lock
```
## What can this bot do?
1. Send current weather.

   <img alt="current weather.gif" height="480" src="assets/current%20weather.gif" width="216"/>
2. Send today forecast

   <img alt="today forecast.gif" height="480" src="assets/today%20forecast.gif" width="216"/>
3. Enable/Disable weather daily forecast

   <img alt="enable notification.gif" height="480" src="assets/enable%20notification.gif" width="216"/>
4. General bot settings:
   - Language settings (Russian, English)
   - Time settings for daily forecast
   - Change coords
   - Change city

    <img alt="General settings.gif" height="480" src="assets/General%20settings.gif" width="216"/>
5. Button to add bot to a group as admin

    <img alt="Add in group button.png" src="assets/Add%20in%20group%20button.png"/>
6. Bot settings in group:
   - Language settings for groups messages (Russian, English)
   - Timezone settings
   - 2 Daily forecast tasks with next settings:
     - Time settings for daily forecast
     - Change coords
     - Change city
     - Enable/Disable button

     <img alt="group settings.gif" height="480" src="assets/group%20settings.gif" width="216"/>

## Installation

1. Clone the repository to your local machine via HTTPS:

```bash
git clone https://github.com/Ruslan-Droid/aiogram-weather-bot.git
```

or via SSH:

```bash
git@github.com:Ruslan-Droid/aiogram-weather-bot.git
```

2. Create a `.env` file in the root of the project and copy the code from the `.env.example` file into it. Replace the
   required secrets (BOT_TOKEN, ADMINS_CHAT, etc).

3. Run `docker-compose.yml` with `docker compose up` command. You need docker and docker-compose installed on your local
   machine.

4. Create a virtual environment in the project root and activate it.

5. Install the required libraries in the virtual environment. With `uv`:

```bash
uv sync
```

6. Apply database migrations using the command:

```bash
alembic upgrade head
```

7. Run `create_stream.py` to create NATS stream for delayed messages service:

```bash
python3 -m nats_broker.migrations.create_stream
```

8. Start the taskiq worker first:

```bash
taskiq worker src.services.scheduler.taskiq_broker:broker -fsd
```

and then the scheduler:

```bash
taskiq scheduler src.services.scheduler.taskiq_broker:scheduler
```

9. Run `main.py` to start bot.
