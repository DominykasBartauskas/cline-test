.PHONY: help install dev test lint format migrate run docker-build docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install      Install dependencies"
	@echo "  make dev          Install development dependencies"
	@echo "  make test         Run tests"
	@echo "  make lint         Run linters"
	@echo "  make format       Format code"
	@echo "  make migrate      Run database migrations"
	@echo "  make run          Run the application"
	@echo "  make docker-build Build Docker image"
	@echo "  make docker-up    Start Docker containers"
	@echo "  make docker-down  Stop Docker containers"

install:
	uv pip install -r requirements.txt

dev:
	uv pip install -r requirements.txt
	pre-commit install

test:
	pytest -v

lint:
	black --check app tests
	isort --check app tests
	pyright

format:
	black app tests
	isort app tests

migrate:
	alembic upgrade head

run:
	uvicorn app.main:app --reload

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down
