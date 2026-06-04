#!/usr/bin/env python3
"""
Скрипт ожидания готовности PostgreSQL и Redis перед запуском коллектора.
- Проверяет PostgreSQL (pg_isready + SELECT 1)
- Проверяет Redis (PING + SET/GET)
- Создаёт таблицы в БД, если их нет
- Использует экспоненциальную задержку (2, 4, 8, 16 сек)
- Возвращает 0 при успехе, 1 при ошибке
"""

import os
import sys
import time
import socket
import subprocess
import psycopg2
import redis


class Colors:
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"


def log(msg: str, color: str = ""):
    """Вывод цветного сообщения."""
    prefix = f"[{time.strftime('%H:%M:%S')}]"
    if color:
        print(f"{color}{prefix} {msg}{Colors.RESET}", file=sys.stdout, flush=True)
    else:
        print(f"{prefix} {msg}", file=sys.stdout, flush=True)


def log_ok(msg: str):
    log(msg, Colors.GREEN)


def log_warn(msg: str):
    log(msg, Colors.YELLOW)


def log_err(msg: str):
    log(msg, Colors.RED)


def wait_for_postgres(max_retries: int = 30) -> bool:
    """
    Ждёт готовности PostgreSQL:
      1. Сетевая доступность порта
      2. pg_isready
      3. SELECT 1 (реальный запрос)
    """
    db_host = os.getenv("DB_HOST", "db")
    db_port = int(os.getenv("DB_PORT", 5432))

    delay = 2
    attempt = 0

    while attempt < max_retries:
        attempt += 1

        # 1. Сетевая проверка
        try:
            with socket.create_connection((db_host, db_port), timeout=3):
                pass
        except (socket.timeout, OSError):
            log_warn(f"PostgreSQL #{attempt}: порт {db_host}:{db_port} недоступен "
                     f"(ожидание {delay} сек)")
            time.sleep(delay)
            delay = min(delay * 2, 16)
            continue

        # 2. pg_isready
        try:
            result = subprocess.run(
                ["pg_isready", "-h", db_host, "-p", str(db_port), "-U", os.getenv("DB_USER", "postgres_user")],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                log_ok(f"PostgreSQL #{attempt}: pg_isready OK")
            else:
                log_warn(f"PostgreSQL #{attempt}: pg_isready вернул {result.returncode} "
                         f"(ожидание {delay} сек)")
                time.sleep(delay)
                delay = min(delay * 2, 16)
                continue
        except FileNotFoundError:
            # pg_isready не установлен — пропускаем
            log_warn("pg_isready не найден, пропускаю проверку")
        except subprocess.TimeoutExpired:
            log_warn(f"PostgreSQL #{attempt}: pg_isready timeout "
                     f"(ожидание {delay} сек)")
            time.sleep(delay)
            delay = min(delay * 2, 16)
            continue

        # 3. SELECT 1 — реальный запрос к БД
        try:
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                user=os.getenv("DB_USER", "postgres_user"),
                password=os.getenv("DB_PASSWORD", "postgres_password"),
                dbname=os.getenv("DB_NAME", "moex_db"),
                connect_timeout=5,
            )
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.close()
            conn.close()
            log_ok(f"PostgreSQL #{attempt}: SELECT 1 выполнен успешно")
            return True
        except psycopg2.OperationalError as e:
            log_warn(f"PostgreSQL #{attempt}: SELECT 1 не выполнен — {e} "
                     f"(ожидание {delay} сек)")
            time.sleep(delay)
            delay = min(delay * 2, 16)
            continue
        except Exception as e:
            log_err(f"PostgreSQL #{attempt}: неожиданная ошибка — {e}")
            return False

    log_err(f"PostgreSQL не готов после {max_retries} попыток")
    return False



def wait_for_redis(max_retries: int = 30) -> bool:
    """
    Ждёт готовности Redis:
      1. PING
      2. SET/GET тест
    """
    redis_host = os.getenv("REDIS_HOST", "cache")
    redis_port = int(os.getenv("REDIS_PORT", 6379))

    delay = 2
    attempt = 0

    while attempt < max_retries:
        attempt += 1

        try:
            client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=int(os.getenv("REDIS_DB", 0)),
                socket_connect_timeout=3,
                socket_timeout=3,
                decode_responses=True,
            )

            # PING
            if not client.ping():
                log_warn(f"Redis #{attempt}: PING вернул False "
                         f"(ожидание {delay} сек)")
                time.sleep(delay)
                delay = min(delay * 2, 16)
                continue

            log_ok(f"Redis #{attempt}: PING OK")

            # SET/GET тест
            test_key = "_wait_for_services_test"
            test_value = "ok"
            client.set(test_key, test_value, ex=5)
            got = client.get(test_key)

            if got == test_value:
                client.delete(test_key)
                log_ok(f"Redis #{attempt}: SET/GET тест пройден")
                return True
            else:
                log_warn(f"Redis #{attempt}: SET/GET тест провален "
                         f"(ожидание {delay} сек)")
                time.sleep(delay)
                delay = min(delay * 2, 16)
                continue

        except redis.ConnectionError as e:
            log_warn(f"Redis #{attempt}: ConnectionError — {e} "
                     f"(ожидание {delay} сек)")
            time.sleep(delay)
            delay = min(delay * 2, 16)
            continue
        except redis.TimeoutError:
            log_warn(f"Redis #{attempt}: TimeoutError "
                     f"(ожидание {delay} сек)")
            time.sleep(delay)
            delay = min(delay * 2, 16)
            continue
        except Exception as e:
            log_err(f"Redis #{attempt}: неожиданная ошибка — {e}")
            return False

    log_err(f"Redis не готов после {max_retries} попыток")
    return False



def init_db_tables():
    """Создаёт таблицы в БД, если их нет (по init.sql)."""
    db_host = os.getenv("DB_HOST", "db")
    db_port = int(os.getenv("DB_PORT", 5432))

    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=os.getenv("DB_USER", "postgres_user"),
            password=os.getenv("DB_PASSWORD", "postgres_password"),
            dbname=os.getenv("DB_NAME", "moex_db"),
            connect_timeout=5,
        )
        cur = conn.cursor()

        # Проверяем, существует ли таблица instruments
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'instruments'
            );
        """)
        exists = cur.fetchone()[0]

        if exists:
            log_ok("Таблица 'instruments' уже существует")
        else:
            # Читаем init.sql и выполняем
            init_sql_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "init.sql"
            )

            if os.path.exists(init_sql_path):
                with open(init_sql_path, "r") as f:
                    sql = f.read()
                cur.execute(sql)
                conn.commit()
                log_ok("Таблица 'instruments' создана из init.sql")
            else:
                log_warn("init.sql не найден, пропускаю инициализацию таблиц")

        cur.close()
        conn.close()

    except Exception as e:
        log_err(f"Ошибка инициализации БД: {e}")
        return False

    return True



def main():
    print("=" * 60)
    print("  Ожидание готовности сервисов...")
    print("=" * 60)

    log_ok("Начинаю проверку PostgreSQL...")
    db_ready = wait_for_postgres()
    if not db_ready:
        log_err("PostgreSQL не готов. Отмена запуска.")
        sys.exit(1)

    log_ok("Начинаю проверку Redis...")
    redis_ready = wait_for_redis()
    if not redis_ready:
        log_err("Redis не готов. Отмена запуска.")
        sys.exit(1)

    log_ok("Все сервисы готовы!")
    log_ok("Инициализация таблиц БД...")
    tables_ok = init_db_tables()
    if not tables_ok:
        log_err("Не удалось инициализировать таблицы. Отмена запуска.")
        sys.exit(1)

    log_ok("Готово к запуску коллектора.")
    print("=" * 60)
    sys.exit(0)


if __name__ == "__main__":
    main()