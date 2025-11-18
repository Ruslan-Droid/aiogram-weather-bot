from typing import Optional
from aiogram import Bot, Dispatcher
from config.config import AppConfig

_bot: Optional[Bot] = None
_dp: Optional[Dispatcher] = None
_config: Optional[AppConfig] = None


def set_bot(bot_instance: Bot) -> None:
    global _bot
    _bot = bot_instance


def get_bot() -> Bot:
    if _bot is None:
        raise RuntimeError("Bot not initialized")
    return _bot


def set_dp(dp_instance: Dispatcher) -> None:
    global _dp
    _dp = dp_instance


def get_dp() -> Dispatcher:
    if _dp is None:
        raise RuntimeError("Dispatcher not initialized")
    return _dp


def set_config(config_instance: AppConfig) -> None:
    global _config
    _config = config_instance


def get_config() -> Config:
    if _config is None:
        raise RuntimeError("Config not initialized")
    return _config
