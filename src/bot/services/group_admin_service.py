import logging
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from src.bot.enums.group_data import AdminData, extract_admin_data
from src.infrastructure.database.dao import UserRepository, GroupChatRepository

logger = logging.getLogger(__name__)


async def sync_group_admins(
        bot: Bot,
        telegram_chat_id: int,
        session: AsyncSession,
        group_id: int,
) -> None:
    try:
        # Получаем список администраторов
        admins = await bot.get_chat_administrators(telegram_chat_id)

        # Извлекаем данные администраторов
        admin_data_list: list[AdminData] = []

        for admin in admins:
            if not admin.user.is_bot:
                admin_data = extract_admin_data(admin)
                admin_data_list.append(admin_data)

        # Bulk операции
        user_repo = UserRepository(session)
        group_repo = GroupChatRepository(session)

        # 1. Создаем/обновляем пользователей
        users_dict = await user_repo.bulk_create_or_update_admins(admin_data_list)

        # 2. Подготавливаем данные для связей
        group_admins_data = []
        for admin_data, user in zip(admin_data_list, users_dict):
            group_admins_data.append({
                'user_id': user.id,
                'admin_permissions': admin_data.permissions,
                'is_active': True
            })

        print("group_admins_data", group_admins_data)
        # 3. Обновляем связи администраторов
        await group_repo.update_group_admins(group_id, group_admins_data)

        logger.info("Синхронизировано %s администраторов для группы %s", len(admin_data_list), telegram_chat_id)

    except Exception as e:
        logger.error("Ошибка синхронизации администраторов для группы %s, error: %s ", telegram_chat_id, str(e))
        raise
