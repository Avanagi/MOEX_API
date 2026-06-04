.PHONY: build up down logs logs-collector restart restart-collector rebuild status ps

COMPOSE := docker-compose
ENV_FILE := backend/.env
ENV_EXAMPLE := backend/.env.example

.PHONY: _check-docker
_check-docker:
	@if ! command -v docker >/dev/null 2>&1; then \
		echo "[ERROR] docker not found. Please install Docker Desktop."; \
		exit 1; \
	fi
	@if ! docker info >/dev/null 2>&1; then \
		echo "[ERROR] Docker is not running. Please start Docker Desktop."; \
		exit 1; \
	fi

.PHONY: _check-env
_check-env:
	@if [ ! -f $(ENV_FILE) ]; then \
		if [ -f $(ENV_EXAMPLE) ]; then \
			cp $(ENV_EXAMPLE) $(ENV_FILE); \
			echo "[OK] .env created from .env.example"; \
		else \
			echo "[ERROR] .env or .env.example not found in backend/"; \
			exit 1; \
		fi; \
	fi

build: _check-docker _check-env
	@echo "[BUILD] Building Docker images..."
	$(COMPOSE) build

up: _check-docker _check-env
	@echo "[START] Starting all services..."
	$(COMPOSE) up -d

down: _check-docker
	@echo "[STOP] Stopping all services..."
	$(COMPOSE) down

logs: _check-docker
	$(COMPOSE) logs -f

logs-collector: _check-docker
	$(COMPOSE) logs -f collector

restart: _check-docker
	@echo "[RESTART] Restarting all services..."
	$(COMPOSE) down
	$(COMPOSE) up -d

restart-collector: _check-docker
	@echo "[RESTART] Restarting collector..."
	$(COMPOSE) restart collector
	$(COMPOSE) logs -f collector

rebuild: _check-docker _check-env
	@echo "[REBUILD] Full rebuild without cache..."
	$(COMPOSE) down
	$(COMPOSE) build --no-cache
	$(COMPOSE) up -d

status: _check-docker
	$(COMPOSE) ps

ps: _check-docker
	$(COMPOSE) ps