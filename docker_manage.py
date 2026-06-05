#!/usr/bin/env python3
"""
docker_manage.py — Скрипт управления Docker-контейнерами MOEX_API.
Работает на Windows, Linux, macOS при наличии Python 3.8+.
Заменяет Makefile, run.sh и run.ps1.

Использование:
    python docker_manage.py build
    python docker_manage.py up
    python docker_manage.py down
    python docker_manage.py logs
    python docker_manage.py logs-collector
    python docker_manage.py restart
    python docker_manage.py restart-collector
    python docker_manage.py rebuild
    python docker_manage.py status
    python docker_manage.py help
"""

import sys
import os
import subprocess
import shutil


# ---------------------------------------------------------------------------
# Цвета (работают на Windows 10+, Linux, macOS)
# ---------------------------------------------------------------------------
class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    BOLD = "\033[1m"
    NC = "\033[0m"  # No Color


def color(text: str, color_code: str) -> str:
    """Оборачивает текст в цветовой код."""
    if shutil.which("tput") or sys.platform != "win32":
        return f"{color_code}{text}{Colors.NC}"
    return text


def info(msg: str):
    print(color(f"  {msg}", Colors.GREEN))


def warn(msg: str):
    print(color(f"  {msg}", Colors.YELLOW))


def err(msg: str):
    print(color(f"  {msg}", Colors.RED))


def title(msg: str):
    print(color(f"  {msg}", Colors.CYAN))


COMPOSE_CMD = "docker-compose"
ENV_FILE = os.path.join("backend", ".env")
ENV_EXAMPLE = os.path.join("backend", ".env.example")


def check_docker():
    """Проверяет, что Docker установлен и запущен."""
    if not shutil.which("docker"):
        err("docker не найден. Установите Docker Desktop.")
        sys.exit(1)

    result = subprocess.run(
        ["docker", "info"],
        capture_output=True,
        timeout=10,
    )
    if result.returncode != 0:
        err("Docker не запущен. Запустите Docker Desktop.")
        sys.exit(1)


def check_env():
    """Создаёт .env из .env.example, если его нет."""
    if not os.path.exists(ENV_FILE):
        if os.path.exists(ENV_EXAMPLE):
            shutil.copy2(ENV_EXAMPLE, ENV_FILE)
            info(".env создан из .env.example")
        else:
            err("Не найден ни .env, ни .env.example в папке backend/")
            sys.exit(1)


def run_compose(*args):
    """Вызывает docker-compose с переданными аргументами."""
    cmd = [COMPOSE_CMD] + list(args)
    return subprocess.run(cmd)


def cmd_build():
    check_docker()
    check_env()
    info("Сборка образов...")
    run_compose("build")


def cmd_up():
    check_docker()
    check_env()
    info("Запуск всех сервисов...")
    run_compose("up", "-d")


def cmd_down():
    check_docker()
    warn("Остановка всех сервисов...")
    run_compose("down")


def cmd_logs():
    check_docker()
    run_compose("logs", "-f")


def cmd_logs_collector():
    check_docker()
    run_compose("logs", "-f", "collector")


def cmd_restart():
    check_docker()
    warn("Перезапуск всех сервисов...")
    run_compose("down")
    run_compose("up", "-d")


def cmd_restart_collector():
    check_docker()
    warn("Перезапуск коллектора...")
    run_compose("restart", "collector")
    run_compose("logs", "-f", "collector")


def cmd_rebuild():
    check_docker()
    check_env()
    warn("Пересборка без кэша...")
    run_compose("down")
    run_compose("build", "--no-cache")
    run_compose("up", "-d")


def cmd_status():
    check_docker()
    run_compose("ps")


HELP_TEXT = """
{bold}╔══════════════════════════════════════════════════════════╗{nc}
{cyan}║       MOEX_API — Управление Docker-контейнерами         ║{nc}
{cyan}╠══════════════════════════════════════════════════════════╣{nc}
{cyan}║                                                          ║{nc}
{blue}  build       {nc}Сборка всех образов
{blue}  up          {nc}Запуск всех сервисов
{blue}  down        {nc}Остановка и удаление контейнеров
{blue}  logs        {nc}Логи всех сервисов (follow)
{blue}  logs-collector   {nc}Логи только коллектора (follow)
{blue}  restart     {nc}Перезапуск всех сервисов
{blue}  restart-collector  {nc}Перезапуск только коллектора
{blue}  rebuild     {nc}Полная пересборка без кэша
{blue}  status      {nc}Статус контейнеров
{blue}  help        {nc}Показать эту справку
{cyan}║                                                          ║{nc}
{cyan}╚══════════════════════════════════════════════════════════╝{nc}
""".format(
    bold=Colors.BOLD,
    cyan=Colors.CYAN,
    blue=Colors.BLUE,
    nc=Colors.NC,
)


COMMANDS = {
    "build": cmd_build,
    "up": cmd_up,
    "down": cmd_down,
    "logs": cmd_logs,
    "logs-collector": cmd_logs_collector,
    "restart": cmd_restart,
    "restart-collector": cmd_restart_collector,
    "rebuild": cmd_rebuild,
    "status": cmd_status,
    "ps": cmd_status,
    "help": None,
    "--help": None,
    "-h": None,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("help", "--help", "-h"):
        print(HELP_TEXT)
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd not in COMMANDS:
        err(f"Неизвестная команда: {cmd}")
        print()
        print(HELP_TEXT)
        sys.exit(1)

    if cmd in COMMANDS and COMMANDS[cmd] is not None:
        COMMANDS[cmd]()
    else:
        print(HELP_TEXT)


if __name__ == "__main__":
    main()
