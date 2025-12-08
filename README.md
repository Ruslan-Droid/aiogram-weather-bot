# Aiogram 3 Weather Bot

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
📁 aiogram_bot_template/
├── 📁 alembic/
│   ├── 📁 versinos/
│   │   ├── 1541bb8a3f26_.py
│   │   └── b20e5643d3bd_.py
│   ├── env.py
│   └── script.py.mako
├── 📁 app/
│   ├── 📁 bot/
│   │   ├── 📁 dialogs/
│   │   │   ├── 📁 flows/
│   │   │   │   ├── 📁 settings/
│   │   │   │   │   ├── dialogs.py
│   │   │   │   │   ├── getters.py
│   │   │   │   │   ├── handlers.py
│   │   │   │   │   ├── keyboards.py
│   │   │   │   │   └── states.py
│   │   │   │   ├── 📁 start/
│   │   │   │   │   ├── dialogs.py
│   │   │   │   │   ├── getters.py
│   │   │   │   │   ├── handlers.py
│   │   │   │   │   └── states.py
│   │   │   │   └── __init__.py
│   │   │   └── 📁 widgets/
│   │   │       └── i18n.py
│   │   ├── 📁 enums/
│   │   │   ├── actions.py
│   │   │   └── roles.py
│   │   ├── 📁 filters/
│   │   │   └── dialog_filters.py
│   │   ├── 📁 handlers/
│   │   │   ├── __init__.py
│   │   │   ├── commands.py
│   │   │   └── errors.py
│   │   ├── 📁 i18n/
│   │   │   └── translator_hub.py
│   │   ├── 📁 keyboards/
│   │   │   ├── links_kb.py
│   │   │   └── menu_button.py
│   │   ├── 📁 middlewares/
│   │   │   ├── database.py
│   │   │   ├── get_user.py
│   │   │   ├── i18n.py
│   │   │   └── shadow_ban.py
│   │   ├── 📁 states/
│   │   │   └── states.py
│   │   ├── __init__.py
│   │   └── bot.py
│   ├── 📁 infrastructure/
│   │   ├── 📁 cache/
│   │   │   └── connect_to_redis.py
│   │   ├── 📁 database/
│   │   │   ├── 📁 connection/
│   │   │   │   ├── base.py
│   │   │   │   ├── connect_to_pg.py
│   │   │   │   └── psycopg_connection.py
│   │   │   ├── 📁 models/
│   │   │   │   └── users.py
│   │   │   ├── 📁 query/
│   │   │   │   └── results.py
│   │   │   ├── 📁 tables/
│   │   │   │   ├── 📁 enums/
│   │   │   │   │   ├── base.py
│   │   │   │   │   └── users.py
│   │   │   │   ├── base.py
│   │   │   │   └── users.py
│   │   │   ├── 📁 views/
│   │   │   │   └── views.py
│   │   │   └── db.py
│   │   └── 📁 storage/
│   │       ├── 📁 storage/
│   │       │   └── nats_storage.py
│   │       └── nats_connect.py
│   └── 📁 services/
│       ├── 📁 delay_service/
│       │   ├── 📁 models/
│       │   │   └── delayed_messages.py
│       │   ├── consumer.py
│       │   ├── publisher.py
│       │   └── start_consumer.py
│       └── 📁 scheduler/
│           ├── taskiq_broker.py
│           └── tasks.py
├── 📁 config/
│   ├── config.py
│   └── settings.toml
├── 📁 locales/
│   ├── 📁 en/
│   │   ├── 📁 LC_MESSAGES/
│   │   │   └── txt.ftl
│   │   └── 📁 static/
│   └── 📁 ru/
│       ├── 📁 LC_MESSAGES/
│       │   └── txt.ftl
│       └── 📁 static/
├── 📁 nats_broker/
│   ├── 📁 config/
│   │   └── server.conf
│   └── 📁 migrations/
│       └── create_stream.py
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.example
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

## Developer tools

For convenient interaction with nats-server you need to install nats cli tool. For macOS you can do this through the
homebrew package manager. Run the commands:

```bash
brew tap nats-io/nats-tools
brew install nats-io/nats-tools/nats
```

For linux:

```bash
curl -sf https://binaries.nats.dev/nats-io/natscli/nats@latest | sh
sudo mv nats /usr/local/bin/
```

After this you can check the NATS version with the command:

```bash
nats --version
```

## TODO

1. Add mailing service
2. Set up a CICD pipeline using Docker and GitHub Actions
