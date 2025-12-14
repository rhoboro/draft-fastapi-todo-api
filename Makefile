.PHONY: format mypy lint pytest
all: format mypy pytest

format:
	docker compose exec app uv run ruff format app
	docker compose exec app uv run ruff check --fix app

mypy:
	docker compose exec app uv run mypy app

pytest:
	docker compose exec app uv run pytest -v

