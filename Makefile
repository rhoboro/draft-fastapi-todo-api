.PHONY: format mypy lint

format:
	docker compose exec app uv run ruff format app
	docker compose exec app uv run ruff check --fix app

mypy:
	docker compose exec app uv run mypy app

pytest:
	docker compose exec app uv run pytest -v

lint: format mypy
