format:
	docker compose exec app uv run ruff format app
	docker compose exec app uv run ruff check --fix app

mypy:
	docker compose exec app uv run mypy app
