import functools
import time

from typing import Callable, Any
from termcolor import colored


def async_timed():
    def wrapper(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapped(*args, **kwargs) -> Any:
            print(colored(
                f'Выполняется функция `{func.__name__}` с аргументами {args} {kwargs}', 'green'))
            start = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                end = time.time()
                total = end - start
                print(
                    colored(f'Функция `{func.__name__}` завершилась за {total:.4f} с', 'green'))
        return wrapped

    return wrapper
