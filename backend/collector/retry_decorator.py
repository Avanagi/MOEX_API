#!/usr/bin/env python3
import sys
import time
import functools
import logging
import psycopg2
import redis

logger = logging.getLogger("moex.retry")

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [retry] %(message)s"
    ))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def retry_on_connection_error(max_retries: int = 5, base_delay: float = 1.0):
    """
    Декоратор, который повторяет вызов функции при ошибках подключения.

    Args:
        max_retries: максимальное число попыток (включая первую).
        base_delay: базовая задержка в секундах (экспоненциальный рост).

    Returns:
        Обёрнутая функция.

    Ловит:
        - psycopg2.OperationalError, psycopg2.InterfaceError
        - redis.ConnectionError, redis.TimeoutError
        - ConnectionRefusedError, TimeoutError, OSError
    """

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            last_exc = None

            for attempt in range(1, max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 1:
                        logger.info(
                            "[%s] Успешно с %d-й попытки",
                            func.__name__,
                            attempt,
                        )
                    return result

                except (
                    psycopg2.OperationalError,
                    psycopg2.InterfaceError,
                ) as e:
                    last_exc = e
                    logger.warning(
                        "[%s] Ошибка БД (попытка %d/%d): %s",
                        func.__name__,
                        attempt,
                        max_retries,
                        e,
                    )

                except (
                    redis.ConnectionError,
                    redis.TimeoutError,
                ) as e:
                    last_exc = e
                    logger.warning(
                        "[%s] Ошибка Redis (попытка %d/%d): %s",
                        func.__name__,
                        attempt,
                        max_retries,
                        e,
                    )

                except (ConnectionRefusedError, TimeoutError, OSError) as e:
                    last_exc = e
                    logger.warning(
                        "[%s] Сетевая ошибка (попытка %d/%d): %s",
                        func.__name__,
                        attempt,
                        max_retries,
                        e,
                    )

                if attempt < max_retries:
                    logger.info(
                        "[%s] Повтор через %.0f сек...",
                        func.__name__,
                        delay,
                    )
                    time.sleep(delay)
                    delay *= 2  # экспоненциальный рост

            # Все попытки исчерпаны
            logger.error(
                "[%s] Не удалось выполнить после %d попыток. Последняя ошибка: %s",
                func.__name__,
                max_retries,
                last_exc,
            )
            raise last_exc

        return wrapper

    return decorator
