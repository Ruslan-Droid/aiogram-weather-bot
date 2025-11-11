import asyncio
import os
import sys

from nats.aio.client import Client as NatsClient
from nats.js import JetStreamContext
from nats.js.api import StreamConfig, RetentionPolicy, StorageType

from config.config import get_config


async def main():
    config = get_config()
    nc = NatsClient()
    await nc.connect(servers=config.nats.servers)

    js: JetStreamContext = nc.jetstream()

    stream_name = config.nats.delayed_consumer_stream

    # Конфигурация стрима
    stream_config = StreamConfig(
        name=stream_name,
        subjects=[config.nats.delayed_consumer_subject],
        retention=RetentionPolicy.LIMITS,  # Политика хранения сообщений (limits, interest, workqueue)
        storage=StorageType.FILE,  # Тип хранения сообщений (file, memory)
    )

    # Создание стрима
    await js.add_stream(stream_config)

    print(f"Stream `{stream_name}` created")

    # Закрытие соединения
    await nc.close()


if sys.platform.startswith("win") or os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

asyncio.run(main())
