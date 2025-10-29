import logging
from typing import Any, Dict
from collections.abc import Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from fluentogram import TranslatorHub

from src.infrastructure.database.models import UserModel

logger = logging.getLogger(__name__)


class TranslatorRunnerMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user: User = data.get("event_from_user")

        if user is None:
            return await handler(event, data)

        user_row: UserModel = data.get("user_row")
        default_locale = data.get("default_locale")

        if user_row and user_row.language_code:
            user_lang = user_row.language_code
        else:
            user_lang = (
                user.language_code
                if hasattr(user, "language_code") and user.language_code
                else default_locale
            )

        hub: TranslatorHub = data.get("translator_hub")
        data["i18n"] = hub.get_translator_by_locale(user_lang)

        return await handler(event, data)
