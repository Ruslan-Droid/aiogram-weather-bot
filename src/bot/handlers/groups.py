from aiogram import Router, Bot, F
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION, LEAVE_TRANSITION
from aiogram.types import ChatMemberUpdated, Message

from sqlalchemy.ext.asyncio import AsyncSession
from fluentogram import TranslatorRunner

from src.bot.filters.chat_type_filters import ChatTypeFilterChatMember
from src.infrastructure.database.models import UserModel, GroupModel

groups_router = Router()
groups_router.my_chat_member.filter(ChatTypeFilterChatMember(chat_type=["group", "supergroup"]))
groups_router.chat_member.filter(ChatTypeFilterChatMember(chat_type=["group", "supergroup"]))


@groups_router.my_chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def bot_added_to_group(
        event: ChatMemberUpdated,
        bot: Bot,
        i18n: TranslatorRunner,
        session: AsyncSession,
        user_row: UserModel,
) -> None:
    print("Мы в bot join groups_router", event)

    if event.new_chat_member.status == "administrator":
        admin_perms = {
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
        admins = await bot.get_chat_administrators(event.chat.id)
        admin_ids = {admin.user.id for admin in admins}
        print(admin_ids)
    else:
        await event.answer(text=i18n.get(""))


@groups_router.my_chat_member(ChatMemberUpdatedFilter(LEAVE_TRANSITION))
async def bot_kicked_from_group(
        event: ChatMemberUpdated,
        session: AsyncSession,
        user_row: UserModel,
) -> None:
    print("Мы в bot leaved groups_router", event)


@groups_router.message(F.migrate_to_chat_id)
async def group_to_supegroup_migration(
        message: Message,
) -> None:
    print("Произошла миграция", message)


@groups_router.chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=
        (KICKED | LEFT | RESTRICTED | MEMBER)
        >>
        (ADMINISTRATOR | CREATOR)
    )
)
async def admin_promoted(event: ChatMemberUpdated, admins: set[int]):
    admins.add(event.new_chat_member.user.id)
    await event.answer(
        f"{event.new_chat_member.user.first_name} "
        f"был(а) повышен(а) до Администратора!"
    )


@groups_router.chat_member(
    ChatMemberUpdatedFilter(
        # Обратите внимание на направление стрелок
        # Или можно было поменять местами объекты в скобках
        member_status_changed=
        (KICKED | LEFT | RESTRICTED | MEMBER)
        <<
        (ADMINISTRATOR | CREATOR)
    )
)
async def admin_demoted(event: ChatMemberUpdated, admins: set[int]):
    admins.discard(event.new_chat_member.user.id)
    await event.answer(
        f"{event.new_chat_member.user.first_name} "
        f"был(а) понижен(а) до обычного юзера!"
    )
