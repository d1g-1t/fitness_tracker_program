.PHONY: help build up down restart logs shell db-migrate db-upgrade db-downgrade test clean format lint

help:
	@echo "Доступные команды:"
	@echo "  make build        - Собрать Docker образы"
	@echo "  make up           - Запустить все сервисы"
	@echo "  make down         - Остановить все сервисы"
	@echo "  make restart      - Перезапустить все сервисы"
	@echo "  make logs         - Показать логи всех сервисов"
	@echo "  make shell        - Войти в контейнер приложения"
	@echo "  make db-migrate   - Создать новую миграцию БД"
	@echo "  make db-upgrade   - Применить миграции БД"
	@echo "  make db-downgrade - Откатить последнюю миграцию"
	@echo "  make test         - Запустить тесты"
	@echo "  make clean        - Очистить кеш и временные файлы"
	@echo "  make format       - Форматировать код"
	@echo "  make lint         - Проверить код линтерами"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Приложение запущено на http://localhost:8000"
	@echo "API документация доступна на http://localhost:8000/docs"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

shell:
	docker-compose exec api bash

db-migrate:
	docker-compose exec api alembic revision --autogenerate -m "$(msg)"

db-upgrade:
	docker-compose exec api alembic upgrade head

db-downgrade:
	docker-compose exec api alembic downgrade -1

test:
	docker-compose exec api pytest -v --cov=src --cov-report=html

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +

format:
	docker-compose exec api black src tests
	docker-compose exec api ruff check --fix src tests

lint:
	docker-compose exec api ruff check src tests
	docker-compose exec api mypy src
	docker-compose exec api black --check src tests
