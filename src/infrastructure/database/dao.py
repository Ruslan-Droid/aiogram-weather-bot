import logging
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.infrastructure.database.models import UserModel, UserRole, DailyUserTaskModel, GroupModel

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_telegram_id(self, telegram_id: int) -> UserModel | None:
        try:
            stmt = select(UserModel).filter(UserModel.telegram_id == telegram_id)
            user = await self.session.scalar(stmt)

            if user:
                logger.info("Fetched user by telegram id: %s", telegram_id)
            else:
                logger.info("User not found by telegram id: %s", telegram_id)
            return user

        except Exception as e:
            logger.error("Error getting user by telegram id %s: %s", telegram_id, str(e))
            raise

    async def create_new_user(
            self,
            telegram_id: int,
            username: str | None,
            first_name: str | None,
            last_name: str | None,
            language_code: str | None = "en",
            is_active: bool = True,
            role: UserRole = UserRole.USER,
    ) -> UserModel:
        new_user = UserModel(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
            role=role,
            is_active=is_active,
        )
        try:
            self.session.add(new_user)
            await self.session.flush()

            daily_task = DailyUserTaskModel(user_id=new_user.id)
            self.session.add(daily_task)

            await self.session.commit()
            await self.session.refresh(new_user)
            logger.info("Created new user with telegram id: %s", telegram_id)
            return new_user
        except IntegrityError:
            logger.error("Error creating new user with telegram id: %s", telegram_id)
            await self.session.rollback()
            existing_user = await self.get_user_by_telegram_id(telegram_id)
            if existing_user:
                existing_user.username = username
                existing_user.first_name = first_name
                existing_user.last_name = last_name
                existing_user.language_code = language_code
                existing_user.is_active = is_active
                await self.session.commit()
                logger.info("Updated existing user with telegram id: %s", telegram_id)
                return existing_user
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error("Error creating user by telegram id: %s, error: %s", telegram_id, str(e))
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
            logger.error("Error updating coordinates for telegram id: %s, error: %s", telegram_id, str(e))
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
            logger.error("Error updating coordinates for telegram id: %s error: %s", telegram_id, str(e))
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
            logger.error("Error updating city for telegram id: %s error: %s", telegram_id, str(e))
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
            logger.error("Error updating is_active status for telegram id: %s error: %s", telegram_id, str(e))
            raise

    async def get_user_notification_settings(
            self,
            telegram_id: int,
    ) -> DailyUserTaskModel | None:
        try:
            stmt = (
                select(DailyUserTaskModel)
                .join(UserModel)
                .filter(UserModel.telegram_id == telegram_id)
            )
            notification_settings = await self.session.scalar(stmt)

            if notification_settings:
                logger.info("Fetched notification settings by telegram id: %s", telegram_id)
            else:
                logger.info("Notification settings not found by telegram id: %s", telegram_id)
            return notification_settings

        except Exception as e:
            logger.error("Error getting notification settings by telegram id %s: error %s", telegram_id, str(e))
            raise

    async def enable_notification_settings_and_add_task_id(
            self,
            telegram_id: int,
            task_id: str
    ) -> None:
        stmt = (
            select(DailyUserTaskModel)
            .join(UserModel, DailyUserTaskModel.user_id == UserModel.id)
            .filter(UserModel.telegram_id == telegram_id)
        )
        user_notification_settings = await self.session.scalar(stmt)

        if user_notification_settings:
            user_notification_settings.notifications_enabled = True
            user_notification_settings.taskiq_task_id = task_id
            await self.session.commit()
            logger.debug("User notification enabled")
        else:
            logger.warning("User notification settings not found by telegram id: %s", telegram_id)

    async def disable_notification_settings_and_remove_task_id(
            self,
            telegram_id: int,
    ) -> None:
        stmt = (
            select(DailyUserTaskModel)
            .join(UserModel, DailyUserTaskModel.user_id == UserModel.id)
            .filter(UserModel.telegram_id == telegram_id)
        )
        user_notification_settings = await self.session.scalar(stmt)

        if user_notification_settings:
            user_notification_settings.notifications_enabled = False
            user_notification_settings.taskiq_task_id = None
            await self.session.commit()
            logger.debug("User notification disabled")
        else:
            logger.warning("User notification settings not found by telegram id: %s", telegram_id)

    async def update_taskiq_task_id(
            self,
            telegram_id: int,
            taskiq_task_id: str,
    ) -> None:
        try:
            stmt = (
                select(UserModel)
                .options(joinedload(UserModel.daily_task))
                .where(UserModel.telegram_id == telegram_id)
            )
            user = await self.session.scalar(stmt)
            if user and user.daily_task:
                user.daily_task.taskiq_task_id = taskiq_task_id
                await self.session.commit()
                logger.info("Updated taskiq_task_id for telegram id: %s", telegram_id)
            else:
                logger.warning("User or notification settings not found for telegram id: %s", telegram_id)

        except Exception as e:
            await self.session.rollback()
            logger.error("Error updating taskiq_task_id  for telegram id: %s, error: %s", telegram_id, str(e))
            raise

    async def update_daly_notification_time(
            self,
            telegram_id: int,
            notification_time: str,
    ) -> None:
        try:
            stmt = (
                select(UserModel)
                .options(joinedload(UserModel.daily_task))  # Загружаем связанные настройки
                .where(UserModel.telegram_id == telegram_id)
            )
            user = await self.session.scalar(stmt)
            if user and user.daily_task:
                user.daily_task.notification_time = notification_time
                await self.session.commit()
                logger.info("Updated notification time for telegram id: %s", telegram_id)
            else:
                logger.warning("User or notification settings not found for telegram id: %s", telegram_id)
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
                    DailyUserTaskModel.notification_time,
                )
                .join(DailyUserTaskModel, DailyUserTaskModel.user_id == UserModel.id)
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


class GroupChatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_new_group(
            self,
            chat_id: int,
            title: str | None,
            chat_type: str,
            added_by_telegram_id: int | None,
            bot_status: str,
            admin_permissions: dict | None,
            is_active: bool = True,
    ) -> GroupModel:
        new_group = GroupModel(
            group_telegram_id=chat_id,
            title=title,
            chat_type=chat_type,
            added_by_telegram_id=added_by_telegram_id,
            bot_status=bot_status,
            admin_permissions=admin_permissions,
            is_active=is_active,
        )
        try:
            self.session.add(new_group)
            await self.session.commit()
            await self.session.refresh(new_group)
            logger.info("Created new new group with chat id: %s", chat_id)
            return new_group
        except IntegrityError:
            logger.error("Error creating new group with chat id: %s, group already exists", chat_id)
            await self.session.rollback()
            existing_group = await self.get_group_by_chat_id(chat_id)
            if existing_group:
                existing_group.group_telegram_id = chat_id
                existing_group.title = title
                existing_group.chat_type = chat_type
                existing_group.bot_status = bot_status
                existing_group.admin_permissions = admin_permissions
                existing_group.is_active = is_active
                await self.session.commit()
                logger.info("Updated existing group with chat id: %s", chat_id)
                return existing_group
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error("Error creating group by chat id: %s, error: %s", chat_id, str(e))
            raise

    async def get_group_by_chat_id(
            self,
            telegram_chat_id: int,
    ) -> GroupModel | None:
        try:
            stmt = select(GroupModel).filter(GroupModel.group_telegram_id == telegram_chat_id)
            group = await self.session.scalar(stmt)

            if group:
                logger.info("Fetched group by telegram id: %s", telegram_chat_id)
            else:
                logger.info("User not found by telegram id: %s", telegram_chat_id)
            return group

        except Exception as e:
            logger.error("Error getting user by telegram id %s: %s", telegram_chat_id, str(e))
            raise

    async def update_activity_status_for_group(
            self,
            chat_id: int,
            status: bool
    ) -> None:
        try:
            stmt = (
                update(GroupModel)
                .where(GroupModel.group_telegram_id == chat_id)
                .values(is_active=status)
            )
            await self.session.execute(stmt)
            await self.session.commit()
            logger.info("Updated is_active status for group id: %s", chat_id)
        except Exception as e:
            await self.session.rollback()
            logger.error("Error updating is_active status for group id: %s error: %s", chat_id, str(e))
            raise