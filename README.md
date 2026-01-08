# Aiogram 3 Weather Bot
<img src="https://github.com/Ruslan-Droid/aiogram-weather-bot/actions/workflows/deploy.yml/badge.svg?branch=master" />

https://t.me/KLG_Weather_Bot

@KLG_Weather_Bot

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

## Installation

1. Clone the repository to your local machine via HTTPS:

```bash
git clone https://github.com/kmsint/aiogram_bot_template.git
```

or via SSH:

```bash
git clone git@github.com:kmsint/aiogram_bot_template.git
```

2. Create a `docker-compose.yml` file in the root of the project and copy the code from the `docker-compose.example`
   file into it.

3. Create a `.env` file in the root of the project and copy the code from the `.env.example` file into it. Replace the
   required secrets (BOT_TOKEN, ADMINS_CHAT, etc).

4. Run `docker-compose.yml` with `docker compose up` command. You need docker and docker-compose installed on your local
   machine.

5. Create a virtual environment in the project root and activate it.

6. Install the required libraries in the virtual environment. With `pip`:

```bash
pip install .
```

or if you use `poetry`:

```bash
poetry install --no-root
```

7. Write SQL code in the `upgrade` and `downgrade` functions to create a database schema. See example in file
   `alembic/versions/1541bb8a3f26_.py`.

8. If required, create additional empty migrations with the command:

```bash
alembic revision
```

and fill them with SQL code.

9. Apply database migrations using the command:

```bash
alembic upgrade head
```

10. Run `create_stream.py` to create NATS stream for delayed messages service:

```bash
python3 -m nats_broker.migrations.create_stream
```

11. If you want to use the Taskiq broker for background tasks as well as the Taskiq scheduler, add your tasks to the
    `tasks.py` module and start the worker first:

```bash
taskiq worker src.services.scheduler.taskiq_broker:broker -fsd
```

and then the scheduler:

```bash
taskiq scheduler src.services.scheduler.taskiq_broker:scheduler
```

12. Run `main.py` to check the functionality of the template.

13. You can fill the template with the functionality you need.
