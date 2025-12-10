import logging
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.enums.group_data import AdminData, extract_admin_data
from src.infrastructure.database.dao import UserRepository, GroupChatRepository
from src.infrastructure.database.models import UserRole

logger = logging.getLogger(__name__)


async def process_group_admins(
        bot: Bot,
        chat_id: int,
        session: AsyncSession,
        group_id: int
) -> None:
    try:
        # Получаем список администраторов
        chat_admins = await bot.get_chat_administrators(chat_id)
        logger.info("Got %s chat administrators for chat: %s", len(chat_admins), chat_id)

        user_repo = UserRepository(session)
        group_repo = GroupChatRepository(session)

        # Подготавливаем данные пользователей для bulk операции
        users_to_upsert = []
        telegram_id_to_user_data = {}  # Для связи telegram_id -> данные пользователя

        for admin in chat_admins:
            if admin.user.is_bot:
                continue

            admin_data: AdminData = extract_admin_data(admin)
            users_to_upsert.append(admin_data)
            telegram_id_to_user_data[admin_data.telegram_id] = admin_data

        # Bulk создание/обновление пользователей
        user_id_map = {}  # telegram_id -> user.id в БД
        if users_to_upsert:
            users = await user_repo.bulk_create_or_update_admins(users_to_upsert)

            # Создаем словарь telegram_id -> user.id
            for user in users:
                user_id_map[user.telegram_id] = user.id

        # Если bulk операция не вернула пользователей (они уже были в базе),
        # получаем их по отдельности
        for telegram_id, user_data in telegram_id_to_user_data.items():
            if telegram_id not in user_id_map:
                user = await user_repo.get_user_by_telegram_id(telegram_id)
                if user:
                    user_id_map[telegram_id] = user.id
                else:
                    # Создаем пользователя, если его нет
                    user = await user_repo.create_or_update_user(
                        telegram_id=telegram_id,
                        username=user_data['username'],
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        language_code=user_data['language_code'],
                        is_active=True,
                        role=UserRole.USER
                    )
                    user_id_map[telegram_id] = user.id

        # Подготавливаем данные для связей с группой
        admins_data = []
        for telegram_id, user_data in telegram_id_to_user_data.items():
            if telegram_id in user_id_map:
                admins_data.append({
                    'user_id': user_id_map[telegram_id],
                    'admin_permissions': user_data.permissions
                })

        # Обновляем администраторов группы
        await group_repo.update_group_admins(group_id, admins_data)

        logger.info(f"Successfully processed {len(admins_data)} admins for group {chat_id}")

    except Exception as e:
        logger.error(f"Error processing admins for group {chat_id}: {str(e)}")
        raise
