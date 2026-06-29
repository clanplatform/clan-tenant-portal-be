.PHONY: dev test lint format migrate migrate-create install

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=app

lint:
	flake8 app/ --max-line-length=120

format:
	black app/
	isort app/

migrate:
	alembic upgrade head

migrate-create:
	@read -p "Migration message: " msg; alembic revision --autogenerate -m "$$msg"
