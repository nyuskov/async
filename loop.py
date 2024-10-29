import asyncio

from aiologger import Logger
from aiologger.formatters.base import Formatter

logger = Logger.with_default_handlers(
    level="DEBUG",
    formatter=Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)


async def get_message():
    await asyncio.sleep(2)

    await logger.info("Привет сервер!")


async def listen_port():
    while True:
        await asyncio.sleep(5)

        await logger.info("Получен запрос на соединение, ждём сообщения")

        await asyncio.create_task(get_message())


async def main():
    await asyncio.create_task(listen_port())


asyncio.run(main())
