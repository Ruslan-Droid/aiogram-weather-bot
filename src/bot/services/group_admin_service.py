import logging
from aiogram import Bot
from aiogram.types import ChatMemberUpdated, ChatMemberUnion
from sqlalchemy.ext.asyncio import AsyncSession
from src.bot.enums.group_data import AdminData, extract_admin_data, GroupData, extract_group_data, \
    extract_user_admin_permissions
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
        # get admins list
        admins = await bot.get_chat_administrators(telegram_chat_id)

        # get admins data
        admin_data_list: list[AdminData] = []

        for admin in admins:
            if not admin.user.is_bot:
                admin_data = extract_admin_data(admin)
                admin_data_list.append(admin_data)

        # Bulk operation
        user_repo = UserRepository(session)
        group_repo = GroupChatRepository(session)

        # 1. create / update users
        users_dict = await user_repo.bulk_create_or_update_admins(admin_data_list)

        # 2. get data for relationships
        group_admins_data = []
        for admin_data, user in zip(admin_data_list, users_dict):
            group_admins_data.append({
                'user_id': user.id,
                'admin_permissions': admin_data.permissions,
                'is_active': True
            })

        # 3. update admins relationships
        await group_repo.update_group_admins(group_id, group_admins_data)

        logger.info("synchronise %s admins in group: %s", len(admin_data_list), telegram_chat_id)

    except Exception as e:
        logger.error("Error while synchronization in group %s, error: %s ", telegram_chat_id, str(e))
        raise


async def update_single_group_admin(
        user_id,
        group_id: int,
        is_active: bool,
        session: AsyncSession,
        admin_permissions: ChatMemberUnion | None = None,
) -> None:
    group_repo = GroupChatRepository(session)

    if admin_permissions.status == "administrator" or admin_permissions.status == "creator":
        admin_permissions = extract_user_admin_permissions(admin_permissions)
        logger.info("Get all admin permissions for user: %s", user_id)
    else:
        admin_permissions = None
        logger.info("User: %s don't have admin permissions", user_id)

    await group_repo.add_new_single_admin_or_update(
        user_id=user_id,
        group_id=group_id,
        admin_permissions=admin_permissions,
        is_active=is_active,
    )


async def update_or_create_user_in_groups(
        event: ChatMemberUpdated,
        session: AsyncSession,
) -> UserModel | None:
    user_repo = UserRepository(session)
    from_user = event.new_chat_member.user

    if from_user.is_bot:
        logger.info("dont create bot in DB, bot id: %s", from_user.id)
        return None

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
        is_active: bool = True,
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
        is_active=is_active
    )
    return group
