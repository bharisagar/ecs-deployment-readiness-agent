.PHONY: setup backend frontend test mock-check lint format

setup:
	python -m venv backend/.venv
	backend/.venv/bin/pip install -r requirements.txt
	cd frontend && npm install

backend:
	cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

test:
	pytest backend/tests

mock-check:
	python -m backend.app.cli check --config examples/readiness-config.yaml

lint:
	ruff check backend

format:
	black backend
