from aiogram.enums import ParseMode
from dynaconf import Dynaconf
from pydantic import BaseModel, Field


class LogsConfig(BaseModel):
    level_name: str = Field(
        default="INFO", description="Log level name (e.g. DEBUG, INFO, WARNING, ERROR)."
    )
    format: str = Field(
        default="%(asctime)s [%(levelname)s] %(message)s",
        description="Log message format."
    )


class I18nConfig(BaseModel):
    default_locale: str = Field(default="en", description="Default locale for the application.")
    locales: list[str] = Field(default=["en"], description="List of supported locales.")


class BotConfig(BaseModel):
    token: str = Field(..., description="Telegram bot API token.")
    parse_mode: ParseMode = Field(
        ..., description="Default parse mode for sending messages (e.g. HTML, Markdown)."
    )


class WeatherConfig(BaseModel):
    token: str = Field(..., description="Weather API token.")
    base_url: str = Field(..., description="Weather API base URL.")


class OPENSTREETMAPConfig(BaseModel):
    base_url: str = Field(..., description="OPEN STREAT MAP BASE URL.")


class PostgresConfig(BaseModel):
    name: str = Field(..., description="PostgreSQL database name.")
    host: str = Field(..., description="PostgreSQL server hostname.")
    port: int = Field(..., description="PostgreSQL server port.")
    user: str = Field(..., description="PostgreSQL username.")
    password: str = Field(..., description="PostgreSQL user password.")
    url: str = Field(..., description="PostgreSQL server URL.")


class RedisConfig(BaseModel):
    host: str = Field(default="localhost", description="Redis server hostname.")
    port: int = Field(default=6379, description="Redis server port.")
    database: int = Field(default=0, description="Redis database index.")
    username: str | None = Field(None, description="Optional Redis username.")
    password: str | None = Field(None, description="Optional Redis password.")
    redis_url: str | None = Field(None, description="Redis server URL.")


class NatsConfig(BaseModel):
    servers: str | list[str] = Field(..., description="NATS servers.")
    delayed_consumer_subject: str = Field(..., description="NATS subject for delayed consumer.")
    delayed_consumer_stream: str = Field(..., description="NATS stream for delayed messages.")
    delayed_consumer_durable_name: str = Field(
        ..., description="Durable consumer name for delayed processing."
    )


class AdminConfig(BaseModel):
    admin_id: int = Field(..., description="Admin telegram id.")
    admin_chat_id: int = Field(..., description="Admin telegram chatID.")


class WebhookConfig(BaseModel):
    WEB_SERVER_HOST: str = Field(..., description="Webhook server host.")
    WEB_SERVER_PORT: int = Field(..., description="Webhook server port.")
    WEBHOOK_PATH: str = Field(..., description="Webhook path name.")
    WEBHOOK_SECRET: str = Field(..., description="Webhook secret.")
    WEBHOOK_BASE_URL: str = Field(..., description="Webhook base URL.")


class AppConfig(BaseModel):
    logs: LogsConfig
    i18n: I18nConfig
    bot: BotConfig
    weather: WeatherConfig
    open_street_map: OPENSTREETMAPConfig
    postgres: PostgresConfig
    redis: RedisConfig
    nats: NatsConfig
    admin: AdminConfig
    webhook: WebhookConfig


# Инициализация Dynaconf
_settings = Dynaconf(
    envvar_prefix=False,  # "DYNACONF",
    environments=True,
    env_switcher="ENV_FOR_DYNACONF",
    settings_files=["settings.toml"],
    load_dotenv=True,
)


def get_config() -> AppConfig:
    """
        Returns a typed application configuration.

        Returns:
            AppConfig: A validated Pydantic model containing the application language_settings.
    """
    logs = LogsConfig(
        level_name=_settings.logs.level_name,
        format=_settings.logs.format,
    )

    i18n = I18nConfig(
        default_locale=_settings.i18n.default_locale,
        locales=_settings.i18n.locales,
    )

    weather = WeatherConfig(
        token=_settings.weather_token,
        base_url=_settings.weather_base_url,
    )
    open_street_map = OPENSTREETMAPConfig(
        base_url=_settings.openstreetmap_base_url,
    )

    bot = BotConfig(
        token=_settings.bot_token,
        parse_mode=_settings.bot.parse_mode,
    )

    postgres = PostgresConfig(
        name=_settings.postgres_name,
        host=_settings.postgres_host,
        port=_settings.postgres_port,
        user=_settings.postgres_user,
        password=_settings.postgres_password,
        url=f"postgresql+asyncpg://{_settings.postgres_user}:{_settings.postgres_password}@{_settings.postgres_host}:"
            f"{_settings.postgres_port}/{_settings.postgres_name}"
    )

    redis = RedisConfig(
        host=_settings.redis_host,
        port=_settings.redis_port,
        database=_settings.redis_database,
        username=_settings.redis_username,
        password=_settings.redis_password,
        redis_url=f"redis://{_settings.redis_username}:{_settings.redis_password}@{_settings.redis_host}:{_settings.redis_port}/{_settings.redis_database}"
    )

    nats = NatsConfig(
        servers=_settings.nats.servers,
        delayed_consumer_subject=_settings.nats.delayed_consumer_subject,
        delayed_consumer_stream=_settings.nats.delayed_consumer_stream,
        delayed_consumer_durable_name=_settings.nats.delayed_consumer_durable_name,
    )

    admin = AdminConfig(
        admin_id=_settings.admin_id,
        admin_chat_id=_settings.admin_chat,
    )

    webhook = WebhookConfig(
        WEB_SERVER_HOST=_settings.WEB_SERVER_HOST,
        WEB_SERVER_PORT=_settings.WEB_SERVER_PORT,
        WEBHOOK_PATH=_settings.WEBHOOK_PATH,
        WEBHOOK_SECRET=_settings.WEBHOOK_SECRET,
        WEBHOOK_BASE_URL=_settings.WEBHOOK_BASE_URL,
    )

    return AppConfig(
        logs=logs,
        i18n=i18n,
        weather=weather,
        open_street_map=open_street_map,
        bot=bot,
        postgres=postgres,
        redis=redis,
        nats=nats,
        admin=admin,
        webhook=webhook,
    )
