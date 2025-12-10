import logging
from aiogram import Bot
from aiogram.types import ChatMemberUpdated, ChatMemberUnion
from sqlalchemy.ext.asyncio import AsyncSession
from src.bot.enums.group_data import AdminData, extract_admin_data, GroupData, extract_group_data, \
    _extract_user_admin_permissions
from src.infrastructure.database.dao import UserRepository, GroupChatRepository
from src.infrastructure.database.models import UserModel, GroupModel

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


async def update_single_group_admin(
        user_id: int,
        group_id: int,
        is_active: bool,
        session: AsyncSession,
        admin_permissions: ChatMemberUnion | None = None,
) -> None:
    group_repo = GroupChatRepository(session)

    if admin_permissions:
        admin_permissions = _extract_user_admin_permissions(admin_permissions)

    admins_data = [{
        'user_id': user_id,
        'admin_permissions': admin_permissions,
    }]

    # Этот метод сам обработает активацию/деактивацию
    await


async def update_or_create_user_in_groups(
        event: ChatMemberUpdated,
        session: AsyncSession,
) -> UserModel | None:
    user_repo = UserRepository(session)
    from_user = event.from_user

    user = await user_repo.create_or_update_user(
        telegram_id=from_user.id,
        username=from_user.username,
        first_name=from_user.first_name,
        last_name=from_user.last_name,
        language_code=from_user.language_code or "en",
        is_active=False,
    )
    return user


async def update_or_create_group_in_groups_events(
        event: ChatMemberUpdated,
        session: AsyncSession,
) -> GroupModel:
    group_data: GroupData = extract_group_data(event)

    group_repo = GroupChatRepository(session)
    group = await group_repo.create_or_update_group(
        telegram_chat_id=group_data.chat_id,
        title=group_data.title,
        chat_type=group_data.chat_type,
        added_by_telegram_id=group_data.added_by_telegram_id,
        bot_status=group_data.bot_status,
        admin_permissions=group_data.bot_permissions,
        is_active=True
    )
    return group
