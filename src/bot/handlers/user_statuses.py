import logging

from aiogram import Router
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION, LEAVE_TRANSITION
from aiogram.types import ChatMemberUpdated
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.bot.filters.chat_type_filters import ChatTypeFilterChatMember
from src.infrastructure.database.dao import UserRepository
from src.infrastructure.database.models import UserModel

logger = logging.getLogger(__name__)

user_status_router = Router()
user_status_router.my_chat_member.filter(ChatTypeFilterChatMember(chat_type=["private"]))


@user_status_router.my_chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def user_leave_handler(
        event: ChatMemberUpdated,
        session: AsyncSession,
        user_row: UserModel | None,
) -> None:
    if user_row:
        user_repo: UserRepository = UserRepository(session)
        await user_repo.update_activity_status(telegram_id=user_row.telegram_id, status=False)
        logger.info('User leave from bot %s', user_row.telegram_id)
    else:
        user_rep: UserRepository = UserRepository(session)
        user_row: UserModel = await user_rep.create_new_user(
            telegram_id=event.from_user.id,
            username=event.from_user.username,
            first_name=event.from_user.first_name,
            last_name=event.from_user.last_name,
            language_code=event.from_user.language_code,
            is_active=False,
        )
        logger.info('User leave from bot %s', user_row.telegram_id)


@user_status_router.my_chat_member(ChatMemberUpdatedFilter(LEAVE_TRANSITION))
async def user_join_handler(
        event: ChatMemberUpdated,
        session: AsyncSession,
        user_row: UserModel | None,
) -> None:
    if user_row:
        user_repo: UserRepository = UserRepository(session)
        await user_repo.update_activity_status(telegram_id=user_row.telegram_id, status=True)
        logger.info('User join in bot %s', user_row.telegram_id)
    else:
        user_rep: UserRepository = UserRepository(session)
        user_row: UserModel = await user_rep.create_or_update_user(
            telegram_id=event.from_user.id,
            username=event.from_user.username,
            first_name=event.from_user.first_name,
            last_name=event.from_user.last_name,
            language_code=event.from_user.language_code,
            is_active=False,
        )
        logger.info('User join bot telegram_id: %s', user_row.telegram_id)
