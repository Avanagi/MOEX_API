import os
import json
import logging
from typing import Any, Optional

import redis

logger = logging.getLogger("moex.cache")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

DEFAULT_TTL = int(os.getenv("CACHE_TTL", 25 * 60))  # 25 минут

NAMESPACE = "moex"

_client: Optional[redis.Redis] = None


def get_client() -> Optional[redis.Redis]:

    global _client
    if _client is not None:
        return _client
    try:
        client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            socket_connect_timeout=2,
            socket_timeout=2,
            decode_responses=True,
        )
        client.ping()
        _client = client
        logger.info("Redis подключён: %s:%s", REDIS_HOST, REDIS_PORT)
    except Exception as exc:
        logger.warning("Redis недоступен (%s). Работаем без кэша.", exc)
        _client = None
    return _client


def make_key(prefix: str, **params: Any) -> str:

    parts = [f"{k}={params[k]}" for k in sorted(params) if params[k] is not None]
    suffix = "&".join(parts) if parts else "all"
    return f"{NAMESPACE}:{prefix}:{suffix}"


def get(key: str) -> Optional[Any]:
    client = get_client()
    if client is None:
        return None
    try:
        raw = client.get(key)
        return json.loads(raw) if raw is not None else None
    except Exception as exc:
        logger.warning("Ошибка чтения из кэша (%s): %s", key, exc)
        return None


def set(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:

    client = get_client()
    if client is None:
        return
    try:
        client.set(key, json.dumps(value, default=str, ensure_ascii=False), ex=ttl)
    except Exception as exc:
        logger.warning("Ошибка записи в кэш (%s): %s", key, exc)


def flush() -> int:

    client = get_client()
    if client is None:
        return 0
    try:
        keys = list(client.scan_iter(match=f"{NAMESPACE}:*", count=500))
        if keys:
            client.delete(*keys)
        logger.info("Кэш инвалидирован: удалено %d ключей", len(keys))
        return len(keys)
    except Exception as exc:
        logger.warning("Ошибка очистки кэша: %s", exc)
        return 0
