import logging
from aiogram import Router, Bot, F
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION, LEAVE_TRANSITION, KICKED, LEFT, RESTRICTED, \
    MEMBER, IS_ADMIN
from aiogram.types import ChatMemberUpdated, Message, ChatMemberAdministrator

from sqlalchemy.ext.asyncio import AsyncSession
from fluentogram import TranslatorRunner

from src.bot.filters.chat_type_filters import ChatTypeFilterChatMember
from src.bot.enums.group_data import AdminData, GroupData, extract_group_data, extract_admin_data
from src.infrastructure.database.dao import GroupChatRepository, UserRepository
from src.infrastructure.database.models import UserModel, GroupModel, UserRole

logger = logging.getLogger(__name__)

groups_router = Router()
groups_router.my_chat_member.filter(ChatTypeFilterChatMember(chat_type=["group", "supergroup"]))
groups_router.chat_member.filter(ChatTypeFilterChatMember(chat_type=["group", "supergroup"]))


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

        # Создаем репозитории
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


# bot added in chat
@groups_router.my_chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def bot_added_to_group(
        event: ChatMemberUpdated,
        bot: Bot,
        i18n: TranslatorRunner,
        session: AsyncSession,
) -> None:
    group_repo: GroupChatRepository = GroupChatRepository(session)

    # Подготавливаем данные для группы
    group_data: GroupData = extract_group_data(event)

    # Создаем или обновляем группу с помощью upsert
    group: GroupModel = await group_repo.create_or_update_group(
        chat_id=group_data.chat_id,
        title=group_data.title,
        chat_type=group_data.chat_type,
        added_by_telegram_id=group_data.added_by_telegram_id,
        bot_status=group_data.bot_status,
        admin_permissions=group_data.bot_permissions,
        is_active=True,
    )

    # Отправляем сообщение в зависимости от статуса бота
    if event.new_chat_member.status == "administrator":
        await event.answer(text=i18n.get("bot-added-as-admin"))

        # Запускаем обновление админов
        await process_group_admins(
            bot=bot,
            chat_id=event.chat.id,
            session=session,
            group_id=group.id
        )

    elif event.new_chat_member.status in ["member", "restricted"]:
        await event.answer(text=i18n.get("bot-added-not-as-admin"))
    else:
        logger.warning(f"Bot added with unknown status: {event.new_chat_member.status}")


# bot kicked from chat
@groups_router.my_chat_member(ChatMemberUpdatedFilter(LEAVE_TRANSITION))
async def bot_kicked_from_group(
        event: ChatMemberUpdated,
        session: AsyncSession,
) -> None:
    group_data: GroupData = extract_group_data(event)

    group_repo = GroupChatRepository(session)
    await group_repo.create_or_update_group(
        chat_id=group_data.chat_id,
        title=group_data.title,
        chat_type=group_data.chat_type,
        added_by_telegram_id=group_data.added_by_telegram_id,
        bot_status=group_data.bot_status,
        admin_permissions=group_data.bot_permissions,
        is_active=False,
    )


# group migrate to supergroup
@groups_router.message(F.migrate_to_chat_id)
async def group_to_supergroup_migration(
        message: Message,
) -> None:
    print("Произошла миграция", message)


# user get admin rights
@groups_router.chat_member(
    ChatMemberUpdatedFilter((KICKED | LEFT | RESTRICTED | MEMBER) >> IS_ADMIN)
)
async def user_admin_promoted(event: ChatMemberUpdated) -> None:
    await event.answer(
        f"{event.new_chat_member.user.first_name} "
        f"был(а) повышен(а) до Администратора! В обработке юзера"
    )


# user lost admin rights
@groups_router.chat_member(
    ChatMemberUpdatedFilter((KICKED | LEFT | RESTRICTED | MEMBER) << IS_ADMIN)
)
async def user_admin_demoted(event: ChatMemberUpdated) -> None:
    await event.answer(
        f"{event.new_chat_member.user.first_name} "
        f"был(а) понижен(а) до обычного юзера! В обработке юзера"
    )


# bot get admin rights
@groups_router.my_chat_member(
    ChatMemberUpdatedFilter((KICKED | LEFT | RESTRICTED | MEMBER) >> IS_ADMIN)
)
async def bot_admin_promoted(event: ChatMemberUpdated) -> None:
    await event.answer(
        f"{event.new_chat_member.user.first_name} "
        f"был(а) повышен(а) до Администратора! В обработке бота"
    )


# bot lost admin rights
@groups_router.my_chat_member(
    ChatMemberUpdatedFilter((KICKED | LEFT | RESTRICTED | MEMBER) << IS_ADMIN)
)
async def bot_admin_demoted(event: ChatMemberUpdated) -> None:
    await event.answer(
        f"{event.new_chat_member.user.first_name} "
        f"был(а) понижен(а) до обычного юзера! В обработке бота"
    )
