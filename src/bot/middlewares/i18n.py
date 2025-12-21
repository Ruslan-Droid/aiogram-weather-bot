import logging
from typing import Any, Dict
from collections.abc import Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from fluentogram import TranslatorHub

from src.infrastructure.database.models import UserModel, GroupModel

logger = logging.getLogger(__name__)


class TranslatorRunnerMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        group_row: GroupModel = data.get("group_row")
        user_row: UserModel = data.get("user_row")
        default_locale = data.get("default_locale")

        if group_row and group_row.language_code:
            locale = group_row.language_code
            logger.debug("Using group language: %s for group %s", locale, group_row.group_telegram_id)
        elif user_row and user_row.language_code:
            locale = user_row.language_code
            logger.debug("Using user language: %s for user %s", locale, user_row.telegram_id)
        else:
            user: User = data.get("event_from_user")

            locale = (
                user.language_code
                if hasattr(user, "language_code") and user.language_code
                else default_locale
            )

        hub: TranslatorHub = data.get("translator_hub")
        data["i18n"] = hub.get_translator_by_locale(locale)
        logger.debug("Successful loaded translator for language: %s", locale)
        return await handler(event, data)
