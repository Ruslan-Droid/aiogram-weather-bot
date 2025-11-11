import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter

from src.bot.enums.actions import Action
from src.services.delay_service.models.delayed_messages import DelayedMessageDeletion
from nats.aio.client import Client
from nats.aio.msg import Msg
from nats.js import JetStreamContext

logger = logging.getLogger(__name__)


class DelayedMessageConsumer:
    def __init__(
            self,
            nc: Client,
            js: JetStreamContext,
            bot: Bot,
            subject: str,
            stream: str,
            durable_name: str,
    ) -> None:
        self.nc = nc
        self.js = js
        self.bot = bot
        self.subject = subject
        self.stream = stream
        self.durable_name = durable_name

    async def start(self) -> None:
        self.stream_sub = await self.js.subscribe(
            subject=self.subject,
            stream=self.stream,
            cb=self.on_message,
            durable=self.durable_name,
            manual_ack=True,
        )

    async def on_message(self, msg: Msg):
        if msg.headers.get("Tg-Delayed-Type") == Action.DELETE:
            msg_to_delete = DelayedMessageDeletion.from_dict(msg.headers)

            if msg_to_delete.is_ready_time():
                try:
                    await self.bot.delete_message(
                        chat_id=msg_to_delete.chat_id,
                        message_id=msg_to_delete.message_id,
                    )
                    await msg.ack()

                except TelegramBadRequest:
                    logger.warning("TelegramBadRequest while deleting message")
                    # Игнорируем ошибки "сообщение не найдено" и т.д.
                    await msg.ack()

                except TelegramRetryAfter as e:
                    # Обрабатываем ограничение при флуде
                    logger.warning("TelegramRetryAfter while deleting message, retry after %s", e.retry_after)
                    await msg.nak(delay=e.retry_after)  # Откладываем на время, указанное Telegram
            else:
                # Отправляем nak с временем задержки
                await msg.nak(delay=msg_to_delete.calc_delay())

        # Отложенный пост сообщений
        elif msg.headers.get("Tg-Delayed-Type") == Action.POST:
            pass
        else:
            raise Exception("Unknown Msg Type")

    async def unsubscribe(self) -> None:
        if self.stream_sub:
            await self.stream_sub.unsubscribe()
            logger.info("Consumer unsubscribed")
