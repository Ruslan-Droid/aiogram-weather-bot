import logging

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.enums.roles import UserRole
from src.infrastructure.database.models import UserModel

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_telegram_id(self, telegram_id: int) -> UserModel | None:
        try:
            stmt = select(UserModel).filter(UserModel.telegram_id == telegram_id)
            result = await self.session.execute(stmt)
            user = result.scalar_one_or_none()
            if user:
                logger.debug("Fetched user by telegram id: %s", telegram_id)
            else:
                logger.debug("User not found by telegram id: %s", telegram_id)
            return user

        except Exception as e:
            logger.error("Error getting user by telegram id %s: %s", telegram_id, e)
            raise

    async def create_new_user(
            self,
            telegram_id: int,
            username: str | None,
            first_name: str | None,
            last_name: str | None,
            language_code: str | None = "ru",
            role: UserRole = UserRole.USER,
    ) -> UserModel:
        new_user = UserModel(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
            role=role
        )
        try:
            self.session.add(new_user)
            await self.session.commit()
            logger.info("Created new user with telegram id: %s", telegram_id)
            return new_user

        except Exception as e:
            await self.session.rollback()
            logger.error("Error creating user by telegram id: %s", telegram_id, e)
            raise

    async def update_users_coordinates(
            self,
            telegram_id: int,
            latitude: float,
            longitude: float
    ) -> None:
        try:
            stmt = (
                update(UserModel)
                .where(UserModel.telegram_id == telegram_id)
                .values(latitude=latitude, longitude=longitude)
            )
            await self.session.execute(stmt)
            await self.session.commit()
            logger.info("Updated coordinates for telegram id: %s", telegram_id)
        except Exception as e:
            await self.session.rollback()
            logger.error("Error updating coordinates for telegram id: %s", telegram_id, e)
            raise

    async def update_users_language(
            self,
            telegram_id: int,
            language_code: str
    ) -> None:
        try:
            stmt = (
                update(UserModel)
                .where(UserModel.telegram_id == telegram_id)
                .values(language_code=language_code)
            )
            await self.session.execute(stmt)
            await self.session.commit()
            logger.info("Updated coordinates for telegram id: %s", telegram_id)
        except Exception as e:
            await self.session.rollback()
            logger.error("Error updating coordinates for telegram id: %s", telegram_id, e)
            raise
