from pydantic import BaseModel

from aiogram.types import ChatMemberAdministrator, ChatMemberUpdated, ChatMemberOwner
from aiogram.enums import ChatMemberStatus, ChatType

from src.infrastructure.database.models import UserRole


class BasePermissions(BaseModel):
    can_manage_chat: bool
    can_delete_messages: bool
    can_manage_video_chats: bool
    can_restrict_members: bool
    can_promote_members: bool
    can_change_info: bool
    can_invite_users: bool
    is_anonymous: bool


class UserPermissions(BasePermissions):
    can_post_messages: bool | None = None
    can_edit_messages: bool | None = None
    can_pin_messages: bool | None = None
    can_post_stories: bool | None = None
    can_edit_stories: bool | None = None
    can_delete_stories: bool | None = None
    custom_title: str | None = None


class BotPermissions(BasePermissions):
    can_pin_messages: bool | None = None


class AdminData(BaseModel):
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    language_code: str | None = "en"
    permissions: dict | None = None


class GroupData(BaseModel):
    chat_id: int
    title: str | None = None
    chat_type: ChatType
    added_by_telegram_id: int
    bot_permissions: dict | None = None
    bot_status: ChatMemberStatus


def _extract_user_admin_permissions(
        admin: ChatMemberAdministrator | ChatMemberOwner
) -> dict:
    if isinstance(admin, ChatMemberOwner):
        return {"rights": "owner, all rights"}

    return UserPermissions(
        can_manage_chat=admin.can_manage_chat,
        can_delete_messages=admin.can_delete_messages,
        can_manage_video_chats=admin.can_manage_video_chats,
        can_restrict_members=admin.can_restrict_members,
        can_promote_members=admin.can_promote_members,
        can_change_info=admin.can_change_info,
        can_invite_users=admin.can_invite_users,
        can_post_messages=getattr(admin, 'can_post_messages', None),
        can_edit_messages=getattr(admin, 'can_edit_messages', None),
        can_pin_messages=getattr(admin, 'can_pin_messages', None),
        can_post_stories=getattr(admin, 'can_post_stories', None),
        can_edit_stories=getattr(admin, 'can_edit_stories', None),
        can_delete_stories=getattr(admin, 'can_delete_stories', None),
        is_anonymous=admin.is_anonymous,
        custom_title=admin.custom_title,
    ).model_dump(mode="json")


def _extract_bot_admin_permissions(event: ChatMemberUpdated) -> dict | None:
    if event.new_chat_member.status != "administrator":
        return None

    return BotPermissions(
        can_manage_chat=event.new_chat_member.can_manage_chat,
        can_change_info=event.new_chat_member.can_change_info,
        can_delete_messages=event.new_chat_member.can_delete_messages,
        can_invite_users=event.new_chat_member.can_invite_users,
        can_pin_messages=getattr(event.new_chat_member, 'can_pin_messages', None),
        can_manage_video_chats=event.new_chat_member.can_manage_video_chats,
        can_restrict_members=event.new_chat_member.can_restrict_members,
        can_promote_members=event.new_chat_member.can_promote_members,
        is_anonymous=event.new_chat_member.is_anonymous,
    ).model_dump(mode="json")


def extract_group_data(event: ChatMemberUpdated) -> GroupData:
    return GroupData(
        chat_id=event.chat.id,
        title=event.chat.title,
        chat_type=ChatType(event.chat.type),
        added_by_telegram_id=event.from_user.id,
        bot_permissions=_extract_bot_admin_permissions(event),
        bot_status=ChatMemberStatus(event.new_chat_member.status)
    )


def extract_admin_data(
        admin: ChatMemberAdministrator | ChatMemberOwner
) -> AdminData:
    language = admin.user.language_code if admin.user.language_code else "en"
    return AdminData(
        telegram_id=admin.user.id,
        username=admin.user.username,
        first_name=admin.user.first_name,
        last_name=admin.user.last_name,
        language_code=language,
        permissions=_extract_user_admin_permissions(admin)
    )
