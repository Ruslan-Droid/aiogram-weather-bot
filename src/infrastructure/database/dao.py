import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models import UserModel

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_telegram_id(self, telegram_id: int) -> UserModel | None:
        try:
            stmt = select(UserModel).filter(UserModel.telegram_id == telegram_id)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error("Error getting user by id %s: %s", telegram_id, e)
            raise
