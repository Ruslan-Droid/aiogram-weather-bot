import logging
from typing import Any, Dict
from collections.abc import Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Chat
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models import GroupModel
from src.infrastructure.database.dao import GroupChatRepository

logger = logging.getLogger(__name__)


class GetGroupMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        chat: Chat = data.get("event_chat")
        session: AsyncSession = data.get("session")

        if session is None:
            logger.error("Database object is not provided in middleware data.")
            raise RuntimeError("Missing `session` in middleware context.")

        try:
            if chat and chat.type in ["group", "supergroup"]:
                group_repo = GroupChatRepository(session)
                group_row: GroupModel = await group_repo.get_group_by_chat_id(telegram_chat_id=chat.id)

                data["group_row"] = group_row
                if group_row is None:
                    logger.debug("Group not found in database.")
                else:
                    logger.debug("group %s loaded successfully",    group_row.group_telegram_id)

        except Exception as e:
            logger.exception("Error in GetUserMiddleware: %s", e)
            raise

        return await handler(event, data)
