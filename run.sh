#!/bin/bash
# ============================================================================
# run.sh — Скрипт управления Docker-контейнерами MOEX_API
# ============================================================================
# Для Git Bash на Windows, WSL, Linux, macOS
# Не требует make — работает с обычным bash
# ============================================================================

set -euo pipefail


RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color


COMPOSE="docker-compose"
ENV_FILE="./backend/.env"
ENV_EXAMPLE="./backend/.env.example"


check_docker() {
    if ! command -v docker &>/dev/null; then
        echo -e "${RED} docker не найден. Установите Docker Desktop.${NC}"
        exit 1
    fi

    if ! docker info &>/dev/null; then
        echo -e "${RED} Docker не запущен. Запустите Docker Desktop.${NC}"
        exit 1
    fi
}


check_env() {
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "$ENV_EXAMPLE" ]; then
            cp "$ENV_EXAMPLE" "$ENV_FILE"
            echo -e "${GREEN} .env создан из .env.example${NC}"
        else
            echo -e "${RED} Не найден ни .env, ни .env.example в папке backend/${NC}"
            exit 1
        fi
    fi
}


show_help() {
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║       MOEX_API — Управление Docker-контейнерами         ║${NC}"
    echo -e "${CYAN}╠══════════════════════════════════════════════════════════╣${NC}"
    echo -e "${CYAN}║                                                          ║${NC}"
    echo -e "${BLUE}  build${NC}       Сборка всех образов"
    echo -e "${BLUE}  up${NC}          Запуск всех сервисов"
    echo -e "${BLUE}  down${NC}        Остановка и удаление контейнеров"
    echo -e "${BLUE}  logs${NC}        Логи всех сервисов (follow)"
    echo -e "${BLUE}  logs-collector${NC}  Логи только коллектора (follow)"
    echo -e "${BLUE}  restart${NC}     Перезапуск всех сервисов"
    echo -e "${BLUE}  restart-collector${NC}  Перезапуск только коллектора"
    echo -e "${BLUE}  rebuild${NC}     Полная пересборка без кэша"
    echo -e "${BLUE}  status${NC}      Статус контейнеров"
    echo -e "${BLUE}  help${NC}        Показать эту справку"
    echo -e "${CYAN}║                                                          ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
}


cmd_build() {
    check_docker
    check_env
    echo -e "${GREEN} Сборка образов...${NC}"
    $COMPOSE build
}

cmd_up() {
    check_docker
    check_env
    echo -e "${GREEN} Запуск всех сервисов...${NC}"
    $COMPOSE up -d
}

cmd_down() {
    check_docker
    echo -e "${YELLOW} Остановка всех сервисов...${NC}"
    $COMPOSE down
}

cmd_logs() {
    check_docker
    $COMPOSE logs -f
}

cmd_logs_collector() {
    check_docker
    $COMPOSE logs -f collector
}

cmd_restart() {
    check_docker
    echo -e "${YELLOW} Перезапуск всех сервисов...${NC}"
    $COMPOSE down
    $COMPOSE up -d
}

cmd_restart_collector() {
    check_docker
    echo -e "${YELLOW} Перезапуск коллектора...${NC}"
    $COMPOSE restart collector
    $COMPOSE logs -f collector
}

cmd_rebuild() {
    check_docker
    check_env
    echo -e "${YELLOW} Пересборка без кэша...${NC}"
    $COMPOSE down
    $COMPOSE build --no-cache
    $COMPOSE up -d
}

cmd_status() {
    check_docker
    $COMPOSE ps
}


main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi

    local cmd="$1"
    shift

    case "$cmd" in
        build)
            cmd_build "$@"
            ;;
        up)
            cmd_up "$@"
            ;;
        down)
            cmd_down "$@"
            ;;
        logs)
            cmd_logs "$@"
            ;;
        logs-collector)
            cmd_logs_collector "$@"
            ;;
        restart)
            cmd_restart "$@"
            ;;
        restart-collector)
            cmd_restart_collector "$@"
            ;;
        rebuild)
            cmd_rebuild "$@"
            ;;
        status|ps)
            cmd_status "$@"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED} Неизвестная команда: $cmd${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
