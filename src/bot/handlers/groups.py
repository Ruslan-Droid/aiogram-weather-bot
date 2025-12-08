import logging
from aiogram import Router, Bot, F
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION, LEAVE_TRANSITION, KICKED, LEFT, RESTRICTED, \
    MEMBER, IS_ADMIN
from aiogram.types import ChatMemberUpdated, Message

from sqlalchemy.ext.asyncio import AsyncSession
from fluentogram import TranslatorRunner

from src.bot.filters.chat_type_filters import ChatTypeFilterChatMember
from src.infrastructure.database.dao import GroupChatRepository
from src.infrastructure.database.models import UserModel, GroupModel

logger = logging.getLogger(__name__)

groups_router = Router()
groups_router.my_chat_member.filter(ChatTypeFilterChatMember(chat_type=["group", "supergroup"]))
groups_router.chat_member.filter(ChatTypeFilterChatMember(chat_type=["group", "supergroup"]))


# bot added in chat
@groups_router.my_chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def bot_added_to_group(
        event: ChatMemberUpdated,
        bot: Bot,
        i18n: TranslatorRunner,
        session: AsyncSession,
) -> None:
    group_repo = GroupChatRepository(session)

    # check if group exists
    group = await group_repo.get_group_by_chat_id(event.chat.id)

    if group is None:
        if event.new_chat_member.status == "administrator":
            admin_perms_for_bot = {
                "can_manage_chat": event.new_chat_member.can_manage_chat,
                "can_delete_messages": event.new_chat_member.can_delete_messages,
                "can_restrict_members": event.new_chat_member.can_restrict_members,
                "can_promote_members": event.new_chat_member.can_promote_members,
                "can_change_info": event.new_chat_member.can_change_info,
                "can_invite_users": event.new_chat_member.can_invite_users,
                "can_pin_messages": event.new_chat_member.can_pin_messages,
                "can_edit_messages": event.new_chat_member.can_edit_messages,
                "is_anonymous": event.new_chat_member.is_anonymous,
            }
            group = await group_repo.create_new_group(
                chat_id=event.chat.id,
                title=event.chat.title,
                chat_type=event.chat.type,
                added_by_telegram_id=event.from_user.id,
                bot_status=event.new_chat_member.status,
                admin_permissions=admin_perms_for_bot,
                is_active=True,
            )

            admins = await bot.get_chat_administrators(event.chat.id)

            # Ответ пользователю
            await event.answer(text=i18n.get("bot-added-as-admin"))

        elif event.new_chat_member.status in ["member", "restricted"]:

            group = await group_repo.create_new_group(
                chat_id=event.chat.id,
                title=event.chat.title,
                chat_type=event.chat.type,
                added_by_telegram_id=event.from_user.id,
                bot_status=event.new_chat_member.status,
                admin_permissions=None,
                is_active=True,
            )

            await event.answer(text=i18n.get("bot-added-not-as-admin"))
    else:
        logger.info("group already added")
        await group_repo.update_activity_status_for_group(
            chat_id=event.chat.id,
            status=True)


# bot kicked from chat
@groups_router.my_chat_member(ChatMemberUpdatedFilter(LEAVE_TRANSITION))
async def bot_kicked_from_group(
        event: ChatMemberUpdated,
        session: AsyncSession,
) -> None:
    group_repo = GroupChatRepository(session)
    await group_repo.update_activity_status_for_group(chat_id=event.chat.id, status=False)


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


# admin lost admin rights
@groups_router.my_chat_member(
    ChatMemberUpdatedFilter((KICKED | LEFT | RESTRICTED | MEMBER) << IS_ADMIN)
)
async def bot_admin_demoted(event: ChatMemberUpdated) -> None:
    await event.answer(
        f"{event.new_chat_member.user.first_name} "
        f"был(а) понижен(а) до обычного юзера! В обработке бота"
    )
