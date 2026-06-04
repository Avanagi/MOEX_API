# MOEX_API — Сбор и API финансовых инструментов Московской биржи

FastAPI-приложение для сбора данных с MOEX ISS API, хранения в PostgreSQL и кэширования в Redis.

## Архитектура

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Frontend    │     │  Backend    │     │ Collector   │
│  (Nginx)    │────▶│  (FastAPI)  │◀───▶│  (async)    │
│   :80        │     │   :8000     │     │             │
└─────────────┘     └──────┬──────┘     └──────┬──────┘
                           │                     │
                    ┌──────▼──────┐     ┌───────▼───────┐
                    │   Redis     │     │  PostgreSQL   │
                    │   :6379     │     │    :5432      │
                    └─────────────┘     └───────────────┘
```

### Сервисы

| Сервис     | Описание                          | Порт  |
|------------|-----------------------------------|-------|
| `frontend` | React + Nginx (фронтенд)          | 80    |
| `backend`  | FastAPI REST API                  | 8000  |
| `collector`| Сборщик данных MOEX ISS (asyncio) | —     |
| `db`       | PostgreSQL 15 (хранилище)         | 5432  |
| `cache`    | Redis 7 (кэш)                    | 6379  |

---

## Быстрый старт

### 1. Требования

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (4.0+)
- **Git Bash** + `make` — для Linux/macOS/WSL
- Или **PowerShell** — для Windows без Git Bash

### 2. Запуск (3 варианта)

#### Вариант A: Makefile (Linux / macOS / WSL / Git Bash с make)

```bash
make build
make up
make status
```

#### Вариант B: run.sh (Git Bash без make)

```bash
chmod +x run.sh
./run.sh build
./run.sh up
./run.sh status
```

#### Вариант C: run.ps1 (PowerShell на Windows)

```powershell
.\run.ps1 build
.\run.ps1 up
.\run.ps1 status
```

> Все три варианта автоматически создают `backend/.env` из `.env.example`, если его нет.

### 3. Проверка

```bash
# Статус контейнеров
make status

# Логи
make logs

# Логи только коллектора
make logs-collector

# API health-check
curl http://localhost:8000/health
```

---

## Все команды

| Команда              | Описание                          |
|----------------------|-----------------------------------|
| `build`              | Сборка всех Docker-образов        |
| `up`                 | Запуск всех сервисов в фоне       |
| `down`               | Остановка и удаление контейнеров  |
| `logs`               | Логи всех сервисов (follow)       |
| `logs-collector`     | Логи только коллектора            |
| `restart`            | Полный перезапуск всех сервисов   |
| `restart-collector`  | Перезапуск только коллектора      |
| `rebuild`            | Пересборка без кэша               |
| `status` / `ps`     | Статус контейнеров                |
| `help`              | Показать справку                  |

---


## API

### Endpoints

| Метод    | Путь                         | Описание                    |
|----------|------------------------------|-----------------------------|
| `GET`    | `/api/instruments`           | Список инструментов с фильтрацией |
| `GET`    | `/api/instruments/search?q=...` | Поиск по названию/тикеру |
| `GET`    | `/api/instruments/types`     | Доступные типы              |
| `GET`    | `/api/instruments/count`     | Количество (с кэшем)        |
| `GET`    | `/api/instruments/{ticker}`  | Детали по тикеру            |
| `GET`    | `/health`                    | Health-check (DB + Redis)   |

### Фильтрация `/api/instruments`

| Параметр       | Тип    | Описание                    |
|----------------|--------|-----------------------------|
| `type`         | string | stock, bond, futures, option|
| `sector`       | string | Сектор экономики            |
| `min_price`    | float  | Минимальная цена (>= 0)     |
| `max_price`    | float  | Максимальная цена (>= 0)    |
| `min_yield`    | float  | Минимальная доходность      |
| `max_yield`    | float  | Максимальная доходность     |
| `maturity_from`| date   | Срок погашения от           |
| `maturity_to`  | date   | Срок погашения до           |
| `sort_by`      | string | ticker, price, volume, name |
| `order`        | string | asc, desc                   |
| `limit`        | int    | 1–200 (default: 50)         |
| `offset`       | int    | Пагинация (default: 0)      |

### Примеры

```bash
# Все акции
curl "http://localhost:8000/api/instruments?type=stock&limit=10"

# Поиск по тикеру
curl "http://localhost:8000/api/instruments/search?q=SBER"

# Фильтрация по цене и сортировка
curl "http://localhost:8000/api/instruments?min_price=100&max_price=500&sort_by=price&order=asc"

# Health-check
curl http://localhost:8000/health
```

---

## Запуск тестов

```bash
cd backend
pip install -r requirements.txt
pytest -v
```

С покрытием:
```bash
pytest --cov=app --cov=collector --cov-report=term-missing
```

---

## Переменные окружения

### Backend / Collector

| Переменная       | Значение по умолчанию | Описание         |
|------------------|------------------------|------------------|
| `DB_HOST`        | db                     | Адрес PostgreSQL |
| `DB_PORT`        | 5432                   | Порт PostgreSQL  |
| `DB_USER`        | postgres_user          | Пользователь БД  |
| `DB_PASSWORD`    | postgres_password      | Пароль БД        |
| `DB_NAME`        | moex_db                | Имя базы данных  |
| `REDIS_HOST`     | cache                  | Адрес Redis      |
| `REDIS_PORT`     | 6379                   | Порт Redis       |
| `REDIS_DB`       | 0                      | Номер БД Redis   |
| `CACHE_TTL`      | 1500 (25 мин)         | TTL кэша в секундах |

### PostgreSQL

| Переменная         | Значение       |
|--------------------|----------------|
| `POSTGRES_DB`      | moex_db        |
| `POSTGRES_USER`    | postgres_user  |
| `POSTGRES_PASSWORD`| postgres_password |

---

## Как работает запуск (порядок)

```
1. Docker-compose поднимает db (PostgreSQL)
2. Docker-compose поднимает cache (Redis)
3. Healthcheck гарантирует: pg_isready + redis-cli ping прошли успешно
4. backend ждёт service_healthy db + cache → запускается
5. collector ждёт service_healthy db + cache → запускается
6. wait_for_services.py:
   a. Проверяет socket → pg_isready → SELECT 1 (PostgreSQL)
   b. Проверяет PING → SET/GET (Redis)
   c. Создаёт таблицу instruments из init.sql
7. collector/moex_collector.py начинает сбор данных
8. backend/FastAPI принимает API-запросы
```

---

## Troubleshooting

### Коллектор не запускается

```bash
# Проверить логи
make logs-collector

# Перезапустить
make restart-collector
```

### БД не готова

```bash
# Войти в контейнер PostgreSQL
docker exec -it moex_db psql -U postgres_user -d moex_db

# Проверить таблицы
\dt

# Выйти
\q
```

### Redis недоступен

```bash
# Войти в контейнер Redis
docker exec -it moex_cache redis-cli

# Проверить соединение
ping

# Выйти
quit
```

### Очистка и полный перезапуск

```bash
make down
make rebuild
```

### Порт 8000 уже занят

```bash
# Найти процесс
lsof -i :8000    # Linux/macOS
netstat -ano | findstr :8000  # Windows

# Остановить контейнер
docker stop moex_backend
```

---

## GitHub Actions

CI запускается при push/PR на ветки `main`, `backend`, `testing`:

```yaml
jobs:
  test: pytest + coverage (Python 3.11, 3.12)
  lint: flake8
```

---

## Стек

| Компонент      | Технология           |
|----------------|----------------------|
| Backend        | Python 3.12 + FastAPI |
| ORM/Driver     | psycopg2-binary      |
| Кэш             | Redis 7 + redis-py   |
| БД              | PostgreSQL 15        |
| Frontend       | React + Nginx        |
| Оркестрация    | Docker Compose       |
| Тесты           | pytest + pytest-asyncio |
| CI              | GitHub Actions       |
