.PHONY: dev test migrate migrate-create

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v

migrate:
	alembic upgrade head

migrate-create:
	@read -p "Migration message: " msg; alembic revision --autogenerate -m "$$msg"
