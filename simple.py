import socket
import asyncio
import signal

from typing import List
from asyncio import AbstractEventLoop
from aiologger import Logger
from aiologger.formatters.base import Formatter

logger = Logger.with_default_handlers(
    level="INFO",
    formatter=Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)


class GracefulExit(SystemExit):
    pass


def shutdown():
    raise GracefulExit()


async def close_echo_tasks(echo_tasks: List[asyncio.Task]):
    waiters = [asyncio.wait_for(task, 2) for task in echo_tasks]
    for task in waiters:
        try:
            await task
        except asyncio.exceptions.TimeoutError:
            pass


async def echo(connection: socket,
               loop: AbstractEventLoop) -> None:
    try:
        while data := await loop.sock_recv(connection, 1024):
            logger.info(f"Получены данные: {data}")
            if data == b"\xff\xf4\xff\xfd\x06":
                shutdown()
            await loop.sock_sendall(connection, data)
    except Exception as ex:
        logger.exception(ex)
    finally:
        connection.close()


async def connection_listener(server_socket: socket, loop: AbstractEventLoop):
    while True:
        connection, address = await loop.sock_accept(server_socket)
        connection.setblocking(False)
        logger.info(f"Получено сообщение от {address}")
        echo_task = asyncio.create_task(echo(connection, loop))
        echo_tasks.append(echo_task)


async def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_address = ("127.0.0.1", 8000)
    server_socket.setblocking(False)
    server_socket.bind(server_address)
    server_socket.listen()

    for signame in {'SIGINT', 'SIGTERM'}:
        loop.add_signal_handler(getattr(signal, signame), shutdown)
    await connection_listener(server_socket, loop)


echo_tasks = []
loop: AbstractEventLoop = asyncio.new_event_loop()

try:
    loop.run_until_complete(main())
except GracefulExit:
    loop.run_until_complete(close_echo_tasks(echo_tasks))
finally:
    loop.close()
