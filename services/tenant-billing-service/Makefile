.PHONY: dev test migrate migrate-create install lint

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v

migrate:
	alembic upgrade head

migrate-create:
	@read -p "Migration message: " msg; alembic revision --autogenerate -m "$$msg"

migrate-downgrade:
	alembic downgrade -1

migrate-history:
	alembic history --verbose

lint:
	ruff check app/
