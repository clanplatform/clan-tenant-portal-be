.PHONY: help build up down restart logs logs-tenant logs-billing logs-appconfig \
        migrate migrate-tenant migrate-billing migrate-appconfig \
        test clean ps

help:
	@echo ""
	@echo "clan-tenant-portal-be — Available commands:"
	@echo ""
	@echo "  make build              Build all Docker images"
	@echo "  make up                 Start all services (detached)"
	@echo "  make down               Stop all services"
	@echo "  make restart            Restart all services"
	@echo "  make ps                 Show running containers"
	@echo ""
	@echo "  make logs               Tail all service logs"
	@echo "  make logs-tenant        Tail tenant-service logs"
	@echo "  make logs-billing       Tail tenant-billing-service logs"
	@echo "  make logs-appconfig     Tail tenant-app-config-service logs"
	@echo ""
	@echo "  make migrate            Run all migrations"
	@echo "  make migrate-tenant     Run tenant-service migrations"
	@echo "  make migrate-billing    Run tenant-billing-service migrations"
	@echo "  make migrate-appconfig  Run tenant-app-config-service migrations"
	@echo ""
	@echo "  make test               Run all tests"
	@echo "  make clean              Stop and remove volumes"
	@echo ""

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

ps:
	docker-compose ps

logs:
	docker-compose logs -f

logs-tenant:
	docker-compose logs -f tenant-service

logs-billing:
	docker-compose logs -f tenant-billing-service

logs-appconfig:
	docker-compose logs -f tenant-app-config-service

migrate: migrate-tenant migrate-billing migrate-appconfig

migrate-tenant:
	docker-compose exec tenant-service alembic upgrade head

migrate-billing:
	docker-compose exec tenant-billing-service alembic upgrade head

migrate-appconfig:
	docker-compose exec tenant-app-config-service alembic upgrade head

test:
	docker-compose exec tenant-service pytest tests/ -v
	docker-compose exec tenant-billing-service pytest tests/ -v
	docker-compose exec tenant-app-config-service pytest tests/ -v

clean:
	docker-compose down -v --remove-orphans

dev-setup: build up
	@echo "Waiting for services to be healthy..."
	@sleep 15
	$(MAKE) migrate
	@echo ""
	@echo "Development environment ready!"
	@echo "  tenant-service:          http://localhost:8010"
	@echo "  tenant-billing-service:  http://localhost:8011"
	@echo "  tenant-app-config-service: http://localhost:8012"
	@echo ""
	@echo "API Docs:"
	@echo "  http://localhost:8010/docs"
	@echo "  http://localhost:8011/docs"
	@echo "  http://localhost:8012/docs"
