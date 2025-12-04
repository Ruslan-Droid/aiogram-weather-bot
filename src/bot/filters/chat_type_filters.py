from typing import Union
from aiogram.filters import BaseFilter
from aiogram.types import ChatMemberUpdated, CallbackQuery, Message


class ChatTypeFilterChatMember(BaseFilter):
    def __init__(self, chat_type: Union[str, list]):
        self.chat_type = chat_type

    async def __call__(self, event: ChatMemberUpdated) -> bool:
        if isinstance(self.chat_type, str):
            return event.chat.type == self.chat_type
        else:
            return event.chat.type in self.chat_type


class ChatTypeFilterMessage(ChatTypeFilterChatMember):
    async def __call__(self, message: Message) -> bool:
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type


class ChatTypeFilterCallback(ChatTypeFilterChatMember):
    async def __call__(self, callback: CallbackQuery) -> bool:
        if isinstance(self.chat_type, str):
            return callback.message.chat.type == self.chat_type
        else:
            return callback.message.chat.type in self.chat_type
