import logging
from typing import Any
from collections.abc import Awaitable, Callable

from aiogram import BaseMiddleware
from sqlalchemy.ext.asyncio import async_sessionmaker

logger = logging.getLogger(__name__)


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, async_session_maker: async_sessionmaker):
        self.async_session_maker = async_session_maker

    async def __call__(
            self,
            handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
            event: Any,
            data: dict[str, Any]
    ) -> Any:
        async with self.async_session_maker() as session:
            data["session"] = session
            try:
                result = await handler(event, data)
                await session.commit()
                logger.info("Successfully committed")
                return result
            except Exception as e:
                await session.rollback()
                logger.exception("Transaction rolled back due to error: %s", e)
                raise
