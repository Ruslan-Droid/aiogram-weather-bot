import logging
from typing import Any
from collections.abc import Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Update, User
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models import UserModel
from src.infrastructure.database.dao import UserRepository

logger = logging.getLogger(__name__)


class GetUserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: dict[str, Any],
    ) -> Any:
        user: User = data.get("event_from_user")

        if user is None:
            return await handler(event, data)

        session: AsyncSession = data.get("session")

        if session is None:
            logger.error("Database object is not provided in middleware data.")
            raise RuntimeError("Missing `session` in middleware context.")

        try:
            user_repo = UserRepository(session)
            user_row: UserModel | None = await user_repo.get_user_by_telegram_id(user.id)

            data["user_row"] = user_row

            logger.debug("User %s loaded successfully", user.id)

        except Exception as e:
            logger.exception("Error in GetUserMiddleware: %s", e)
            raise

        return await handler(event, data)
