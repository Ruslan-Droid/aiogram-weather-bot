import logging

from aiogram import Router
from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER, ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.bot.filters.chat_type_filters import ChatTypeFilter
from src.infrastructure.database.dao import UserRepository
from src.infrastructure.database.models import UserModel

logger = logging.getLogger(__name__)

user_status_router = Router()

user_status_router.my_chat_member.filter(ChatTypeFilter(chat_type=["private"]))


@user_status_router.my_chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def on_user_leave(
        event: ChatMemberUpdated,
        session: AsyncSession,
        user_row: UserModel,
) -> None:
    print("Мы в user_statuses leave", event)
    if event.from_user.is_bot:
        return

    user_repo: UserRepository = UserRepository(session)
    await user_repo.update_activity_status(telegram_id=user_row.telegram_id, status=False)
    logger.info('User leave from bot %s', user_row.telegram_id)


@user_status_router.my_chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_user_join(
        event: ChatMemberUpdated,
        session: AsyncSession,
        user_row: UserModel,
) -> None:
    print("Мы в user_statuses join", event)
    if event.from_user.is_bot:
        return

    user_repo: UserRepository = UserRepository(session)
    await user_repo.update_activity_status(telegram_id=user_row.telegram_id, status=True)
    logger.info('User join in bot %s', user_row.telegram_id)
