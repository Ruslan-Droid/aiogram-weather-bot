import logging
from aiogram import Router, Bot, F
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION, LEAVE_TRANSITION, KICKED, LEFT, RESTRICTED, \
    MEMBER, IS_ADMIN
from aiogram.types import ChatMemberUpdated, Message

from sqlalchemy.ext.asyncio import AsyncSession
from fluentogram import TranslatorRunner

from src.bot.filters.chat_type_filters import ChatTypeFilterChatMember
from src.bot.services.group_admin_service import sync_group_admins, update_or_create_user_in_groups, \
    update_or_create_group_in_groups_events

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
    await update_or_create_user_in_groups(
        event=event,
        session=session,
    )

    group = await update_or_create_group_in_groups_events(
        event=event,
        session=session,
    )

    # Отправляем сообщение в зависимости от статуса бота
    if event.new_chat_member.status == "administrator":
        await event.answer(text=i18n.get("bot-added-as-admin"))

        # Запускаем обновление админов
        await sync_group_admins(
            bot=bot,
            telegram_chat_id=event.chat.id,
            session=session,
            group_id=group.id,
        )
    elif event.new_chat_member.status in ["member", "restricted"]:
        await event.answer(text=i18n.get("bot-added-not-as-admin"))
    else:
        logger.warning(f"Bot added with unknown status: {event.new_chat_member.status}")
        await event.answer(text=i18n.get("bot-added-not-as-admin"))


# bot kicked from chat
@groups_router.my_chat_member(ChatMemberUpdatedFilter(LEAVE_TRANSITION))
async def bot_kicked_from_group(
        event: ChatMemberUpdated,
        session: AsyncSession,
) -> None:
    await update_or_create_user_in_groups(
        event=event,
        session=session,
    )
    await update_or_create_group_in_groups_events(
        event=event,
        session=session,
    )


# group migrate to supergroup
@groups_router.message(F.migrate_to_chat_id)
async def group_to_supergroup_migration(
        message: Message,
) -> None:
    print("Произошла миграция", message)


# bot get admin rights
@groups_router.my_chat_member(
    ChatMemberUpdatedFilter((KICKED | LEFT | RESTRICTED | MEMBER) >> IS_ADMIN)
)
async def bot_admin_promoted(
        event: ChatMemberUpdated,
        bot: Bot,
        i18n: TranslatorRunner,
        session: AsyncSession,
) -> None:
    await event.answer(text=i18n.get("bot-get-admin-rights"))

    await update_or_create_user_in_groups(
        event=event,
        session=session,
    )

    group = await update_or_create_group_in_groups_events(
        event=event,
        session=session,
    )

    try:
        await sync_group_admins(
            bot=bot,
            telegram_chat_id=event.chat.id,
            session=session,
            group_id=group.id,
        )
        await event.answer(text=i18n.get("bot-update-admin-list"))
    except Exception as e:
        await event.answer(text=str(e))


# bot lost admin rights
@groups_router.my_chat_member(
    ChatMemberUpdatedFilter((KICKED | LEFT | RESTRICTED | MEMBER) << IS_ADMIN)
)
async def bot_admin_demoted(
        event: ChatMemberUpdated,
        session: AsyncSession,
        i18n: TranslatorRunner,
) -> None:
    await event.answer(text=i18n.get("bot-lost-admin-rights"))

    await update_or_create_user_in_groups(
        event=event,
        session=session,
    )

    await update_or_create_group_in_groups_events(
        event=event,
        session=session,
    )


######### User admins in groups
# user get admin rights
@groups_router.chat_member(
    ChatMemberUpdatedFilter((KICKED | LEFT | RESTRICTED | MEMBER) >> IS_ADMIN)
)
async def user_admin_promoted(
        event: ChatMemberUpdated,
        session: AsyncSession,
) -> None:
    user = await update_or_create_user_in_groups(
        event=event,
        session=session,
    )

    # Обновляем данные группы
    group = await update_or_create_group_in_groups_events(
        event=event,
        session=session,
    )

    # Добавляем пользователя как администратора
    await update_single_group_admin(
        user_id=user.id,
        group_id=group.id,
        admin_permissions=event.new_chat_member,
        is_active=True,
        session=session,
    )
    await event.answer(
        f"{event.new_chat_member.user.first_name} "
        f"был(а) повышен(а) до Администратора! В обработке юзера"
    )


# user lost admin rights
@groups_router.chat_member(
    ChatMemberUpdatedFilter((KICKED | LEFT | RESTRICTED | MEMBER) << IS_ADMIN)
)
async def user_admin_demoted(
        event: ChatMemberUpdated,
        session: AsyncSession
) -> None:
    # Обновляем данные пользователя
    user = await update_or_create_user_in_groups(
        event=event,
        session=session,
    )

    # Обновляем данные группы
    group = await update_or_create_group_in_groups_events(
        event=event,
        session=session,
    )

    # Убираем пользователя из администраторов
    await update_single_group_admin(
        user_id=user.id,
        group_id=group.id,
        admin_permissions={},
        is_active=False,
        session=session,
    )

    await event.answer(
        f"{event.new_chat_member.user.first_name} "
        f"был(а) понижен(а) до обычного юзера!"
    )
