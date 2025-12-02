from aiogram import Router
from aiogram.filters import ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER
from aiogram.types import ChatMemberUpdated
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.filters.chat_type_filters import ChatTypeFilter
from src.infrastructure.database.models import UserModel, GroupChatModel

groups_router = Router()

groups_router.my_chat_member.filter(ChatTypeFilter(chat_type=["group", "supergroup"]))


@groups_router.my_chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_bot_joined_group(
        event: ChatMemberUpdated,
        session: AsyncSession,
        user_row: UserModel,
) -> None:
    print("Мы в groups_router",event)
    if event.chat.type not in ["group", "supergroup"]:
        return

    if event.new_chat_member.status == "administrator":
        admin_perms = {
            "can_manage_chat": event.new_chat_member.can_manage_chat,
            "can_delete_messages": event.new_chat_member.can_delete_messages,
            "can_manage_video_chats": event.new_chat_member.can_manage_video_chats,
            "can_restrict_members": event.new_chat_member.can_restrict_members,
            "can_promote_members": event.new_chat_member.can_promote_members,
            "can_change_info": event.new_chat_member.can_change_info,
            "can_invite_users": event.new_chat_member.can_invite_users,
            "can_pin_messages": event.new_chat_member.can_pin_messages,
            "can_manage_topics": getattr(event.new_chat_member, "can_manage_topics", False),
            "is_anonymous": event.new_chat_member.is_anonymous,
        }


@groups_router.my_chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def on_bot_leaved_group(
        event: ChatMemberUpdated,
        session: AsyncSession,
        user_row: UserModel,
) -> None:
    print("Мы в groups_router",event)
    if event.chat.type not in ["group", "supergroup"]:
        return
