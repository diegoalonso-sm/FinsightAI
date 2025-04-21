PYTHON-VERSION=3.12

# ========== Environment ==========

venv:
	@echo "Creating virtual environment with Python $(PYTHON-VERSION)..."
	uv venv --prompt=FinsightAI --python=$(PYTHON-VERSION)
	chmod -R 777 .

sync:
	@echo "Syncing virtual environment..."
	uv sync
	@echo "Virtual environment created and synced."

upgrade:
	@echo "Updating environment with latest dependencies..."
	uv sync --upgrade
	@echo "Environment updated."

activate:
	@echo "Run the following command to activate the virtual environment:"
	@echo "source .venv/bin/activate"

deactivate:
	@echo "Run the following command to deactivate the virtual environment:"
	@echo "deactivate"

clean:
	@echo "Cleaning up the environment..."
	rm -rf .venv __pycache__ .pytest_cache
	@echo "Environment cleaned."

# ========== Development ==========

run:
	uv run python -m finsight.app

test:
	uv run python -m pytest || true

format:
	uv run ruff format .

# ========== Docker Services ==========

build:
	docker compose build

up:
	docker compose up -d --remove-orphans

down:
	docker compose down

logs:
	docker compose logs -f