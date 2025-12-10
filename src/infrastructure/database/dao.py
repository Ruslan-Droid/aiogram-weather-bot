import logging
from typing import Any, Coroutine, Sequence

from sqlalchemy import select, update, Row, RowMapping, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.bot.enums.group_data import AdminData
from src.infrastructure.database.models import UserModel, UserRole, DailyUserTaskModel, GroupModel, GroupAdminModel

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

    async def create_or_update_user(
            self,
            telegram_id: int,
            username: str | None,
            first_name: str | None,
            last_name: str | None,
            language_code: str | None = "en",
            is_active: bool = True,
            role: UserRole = UserRole.USER,
    ) -> UserModel:
        insert_stmt = pg_insert(UserModel).values(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
            role=role,
            is_active=is_active,
        )

        # Define what to update on conflict
        update_dict = {
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'language_code': language_code,
            'is_active': is_active,
            "role": role,
        }

        on_conflict_stmt = insert_stmt.on_conflict_do_update(
            index_elements=['telegram_id'],
            set_=update_dict
        ).returning(UserModel)

        try:
            # Execute the upsert
            result = await self.session.execute(on_conflict_stmt)
            user = result.scalar_one()

            # Check if user has DailyUserTaskModel, create if not exists
            stmt = select(DailyUserTaskModel).filter(
                DailyUserTaskModel.user_id == user.id
            )

            daily_task = await self.session.scalar(stmt)

            if not daily_task:
                daily_task = DailyUserTaskModel(user_id=user.id)
                self.session.add(daily_task)
                await self.session.commit()

            logger.info("Created/Updated user with telegram id: %s", telegram_id)
            return user

        except Exception as e:
            await self.session.rollback()
            logger.error("Error creating/updating user by telegram id: %s, error: %s", telegram_id, str(e))
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

    async def bulk_create_or_update_admins(
            self,
            users_data: list[AdminData]
    ) -> list[Any] | Sequence[UserModel]:

        if not users_data:
            return []

        values = []
        for user_data in users_data:
            user_dict = user_data.model_dump(exclude={'permissions'})
            values.append(user_dict)

        insert_stmt = pg_insert(UserModel).values(values)

        update_dict = {
            'username': insert_stmt.excluded.username,
            'first_name': insert_stmt.excluded.first_name,
            'last_name': insert_stmt.excluded.last_name,
            'language_code': insert_stmt.excluded.language_code,
        }

        on_conflict_stmt = insert_stmt.on_conflict_do_update(
            index_elements=['telegram_id'],
            set_=update_dict
        ).returning(UserModel)

        try:
            result = await self.session.execute(on_conflict_stmt)
            users = result.scalars().all()
            print("data base function", users)
            user_ids = [user.id for user in users]

            # Проверяем, у каких пользователей уже есть DailyUserTaskModel
            stmt = select(DailyUserTaskModel.user_id).where(
                DailyUserTaskModel.user_id.in_(user_ids)
            )
            existing_task_user_ids = set(await self.session.scalars(stmt))

            # Создаем DailyUserTaskModel для тех, у кого его нет
            for user in users:
                if user.id not in existing_task_user_ids:
                    daily_task = DailyUserTaskModel(user_id=user.id)
                    self.session.add(daily_task)

            await self.session.commit()
            logger.info("Bulk created/updated %s users", len(users))
            return users

        except Exception as e:
            await self.session.rollback()
            logger.error("Error bulk creating/updating users: %s", str(e))
            raise


class GroupChatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_or_update_group(
            self,
            chat_id: int,
            title: str | None,
            chat_type: str,
            added_by_telegram_id: int | None,
            bot_status: str,
            admin_permissions: dict | None,
            is_active: bool = True,
    ) -> GroupModel:
        insert_stmt = pg_insert(GroupModel).values(
            group_telegram_id=chat_id,
            title=title,
            chat_type=chat_type,
            added_by_telegram_id=added_by_telegram_id,
            bot_status=bot_status,
            admin_permissions=admin_permissions,
            is_active=is_active,
        )

        update_dict = {
            'title': title,
            'chat_type': chat_type,
            'bot_status': bot_status,
            'admin_permissions': admin_permissions,
            'is_active': is_active,
        }

        on_conflict_stmt = insert_stmt.on_conflict_do_update(
            index_elements=['group_telegram_id'],
            set_=update_dict
        ).returning(GroupModel)

        try:
            result = await self.session.execute(on_conflict_stmt)
            group = result.scalar_one()
            await self.session.commit()
            logger.info("Created/Updated group with chat id: %s", chat_id)
            return group

        except Exception as e:
            await self.session.rollback()
            logger.error("Error creating/updating group by chat id: %s, error: %s", chat_id, str(e))
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

    async def update_group_admins(
            self,
            group_id: int,
            admins_data: list[dict[str, Any]]
    ) -> None:
        try:
            # Собираем user_id из новых данных
            new_admin_user_ids = {admin['user_id'] for admin in admins_data} if admins_data else set()

            # 1. Делаем upsert для текущих администраторов
            if admins_data:
                values = []
                for admin_data in admins_data:
                    values.append({
                        'user_id': admin_data['user_id'],
                        'group_id': group_id,
                        'admin_permissions': admin_data.get('admin_permissions'),
                        'is_active': True,
                    })

                insert_stmt = pg_insert(GroupAdminModel).values(values)

                on_conflict_stmt = insert_stmt.on_conflict_do_update(
                    index_elements=['user_id', 'group_id'],
                    set_={
                        'admin_permissions': insert_stmt.excluded.admin_permissions,
                        'is_active': True,
                    }
                )
                await self.session.execute(on_conflict_stmt)

            # 2. Деактивируем администраторов, которых нет в новом списке
            # Находим всех активных администраторов этой группы
            stmt = select(GroupAdminModel).where(
                GroupAdminModel.group_id == group_id,
                GroupAdminModel.is_active == True
            )
            admins_in_db = await self.session.scalars(stmt)

            for admin in admins_in_db:
                if admin.user_id not in new_admin_user_ids:
                    admin.is_active = False

            await self.session.commit()
            logger.info(f"Updated admins for group: %s."
                        f"Active admins: %s", group_id, len(new_admin_user_ids))

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating admins for group: %s error: %s", group_id, str(e))
            raise
