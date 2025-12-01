import logging
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models import UserModel, UserRole, UserScheduleTask

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
                logger.info("Fetched user by telegram id: %s", telegram_id)
            else:
                logger.info("User not found by telegram id: %s", telegram_id)
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
            language_code: str | None = "en",
            role: UserRole = UserRole.USER,
    ) -> UserModel:
        new_user = UserModel(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
            role=role,
            user_schedule_task=UserScheduleTask()
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

    async def update_user_city(
            self,
            telegram_id: int,
            city: str
    ) -> None:
        try:
            stmt = (
                update(UserModel)
                .where(UserModel.telegram_id == telegram_id)
                .values(city=city)
            )
            await self.session.execute(stmt)
            await self.session.commit()
            logger.info("Updated city for telegram id: %s", telegram_id)
        except Exception as e:
            await self.session.rollback()
            logger.error("Error updating city for telegram id: %s", telegram_id, e)
            raise

    async def update_activity_status(
            self,
            telegram_id: int,
            status: bool
    ) -> None:
        try:
            stmt = (
                update(UserModel)
                .where(UserModel.telegram_id == telegram_id)
                .values(is_active=status)
            )
            await self.session.execute(stmt)
            await self.session.commit()
            logger.info("Updated is_active status for telegram id: %s", telegram_id)
        except Exception as e:
            await self.session.rollback()
            logger.error("Error updating is_active status for telegram id: %s", telegram_id, e)
            raise

    async def get_user_notification_settings(
            self,
            telegram_id: int,
    ) -> UserScheduleTask | None:
        try:
            stmt = select(UserScheduleTask).filter(UserScheduleTask.telegram_id == telegram_id)
            result = await self.session.execute(stmt)
            notification_settings = result.scalar_one_or_none()
            if notification_settings:
                logger.info("Fetched notification settings by telegram id: %s", telegram_id)
            else:
                logger.info("Notification settings not found by telegram id: %s", telegram_id)
            return notification_settings

        except Exception as e:
            logger.error("Error getting notification settings by telegram id %s: %s", telegram_id, e)
            raise

    async def enable_notification_settings_and_add_task_id(
            self,
            telegram_id: int,
            task_id: str
    ) -> None:
        stmt = select(UserScheduleTask).filter(UserScheduleTask.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        user_notification_settings = result.scalar_one_or_none()

        if user_notification_settings:
            user_notification_settings.notifications_enabled = True
            user_notification_settings.taskiq_task_id = task_id
            logger.debug("User notification enabled")
        else:
            logger.warning("User notification settings not found by telegram id: %s", telegram_id)

        await self.session.commit()

    async def disable_notification_settings_and_remove_task_id(
            self,
            telegram_id: int,
    ) -> None:
        stmt = select(UserScheduleTask).filter(UserScheduleTask.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        user_notification_settings = result.scalar_one_or_none()

        if user_notification_settings:
            user_notification_settings.notifications_enabled = False
            user_notification_settings.taskiq_task_id = None
            logger.debug("User notification disabled")
        else:
            logger.warning("User notification settings not found by telegram id: %s", telegram_id)

        await self.session.commit()

    async def update_taskiq_task_id(
            self,
            telegram_id: int,
            taskiq_task_id: str,
    ) -> None:
        try:
            stmt = (
                update(UserScheduleTask)
                .where(UserScheduleTask.telegram_id == telegram_id)
                .values(taskiq_task_id=taskiq_task_id)
            )
            await self.session.execute(stmt)
            await self.session.commit()
            logger.info("Updated taskiq_task_id  for telegram id: %s", telegram_id)
        except Exception as e:
            await self.session.rollback()
            logger.error("Error updating taskiq_task_id  for telegram id: %s", telegram_id, e)
            raise

    async def update_daly_notification_time(
            self,
            telegram_id: int,
            notification_time: str,
    ) -> None:
        try:
            stmt = (
                update(UserScheduleTask)
                .where(UserScheduleTask.telegram_id == telegram_id)
                .values(notification_time=notification_time)
            )
            await self.session.execute(stmt)
            await self.session.commit()
            logger.info("Updated notification time for telegram id: %s", telegram_id)
        except Exception as e:
            await self.session.rollback()
            logger.error("Error updating notification time for telegram id: %s", telegram_id, e)
            raise

    async def get_all_user_settings(
            self,
            telegram_id: int,
    ) -> dict[str, Any] | None:
        try:
            stmt = (
                select(
                    UserModel.language_code,
                    UserModel.city,
                    UserModel.latitude,
                    UserModel.longitude,
                    UserScheduleTask.notification_time,
                )
                .join(UserScheduleTask, UserScheduleTask.telegram_id == UserModel.telegram_id)
                .where(UserModel.telegram_id == telegram_id)
            )

            result = await self.session.execute(stmt)
            row = result.one_or_none()

            if not row:
                logger.info("User not found by telegram id: %s", telegram_id)
                return None

            logger.info("Fetched user settings by telegram id: %s", telegram_id)
            return {
                "language_code": row.language_code,
                "notification_time": row.notification_time,
                "city": row.city,
                "coords": f"{row.latitude}, {row.longitude}",
            }

        except Exception as e:
            logger.error("Error getting user settings by telegram id %s: %s", telegram_id, e)
            raise
