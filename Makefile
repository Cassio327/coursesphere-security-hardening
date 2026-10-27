.PHONY: up down logs test security load-balance smoke

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f nginx backend-1 backend-2

test:
	python -m pytest -q backend/tests
	cd frontend && npm run lint && npm run build

security:
	bandit -q -r backend -x backend/tests
	pip-audit -r backend/requirements.txt
	cd frontend && npm audit --audit-level=high

load-balance:
	./scripts/demo-load-balancing.sh

smoke:
	./scripts/security-smoke-test.sh
