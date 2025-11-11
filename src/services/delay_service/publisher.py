from datetime import datetime

from src.bot.enums.actions import Action
from nats.js.client import JetStreamContext


async def delay_message_deletion(
    js: JetStreamContext, chat_id: int, message_id: int, subject: str, delay: int = 0
) -> None:
    headers = {
        "Tg-Delayed-Type": Action.DELETE,
        "Tg-Delayed-Chat-ID": str(chat_id),
        "Tg-Delayed-Msg-ID": str(message_id),
        "Tg-Delayed-Msg-Timestamp": str(datetime.now().timestamp()), #1762892250.228379
        "Tg-Delayed-Msg-Delay": str(delay), #0
    }
    await js.publish(subject=subject, headers=headers)


async def delay_message_senging(
    js: JetStreamContext, chat_id: int, text: str, subject: str, delay: int = 0
) -> None:
    headers = {
        "Tg-Delayed-Type": Action.POST,
        "Tg-Delayed-Chat-ID": str(chat_id),
        "Tg-Delayed-Msg-Timestamp": str(datetime.now().timestamp()), #1762892250.228379
        "Tg-Delayed-Msg-Delay": str(delay), #0
    }
    payload = text.encode(encoding="utf-8")
    await js.publish(subject=subject, payload=payload, headers=headers)