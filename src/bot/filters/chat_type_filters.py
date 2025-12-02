from typing import Union
from aiogram.filters import BaseFilter
from aiogram.types import ChatMemberUpdated


class ChatTypeFilter(BaseFilter):
    def __init__(self, chat_type: Union[str, list]):
        self.chat_type = chat_type

    async def __call__(self, event: ChatMemberUpdated) -> bool:
        if isinstance(self.chat_type, str):
            return event.chat.type == self.chat_type
        else:
            return event.chat.type in self.chat_type