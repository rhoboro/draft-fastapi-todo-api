FROM python:3.14-slim AS base

# non-rootユーザーの作成
WORKDIR /app
RUN groupadd -r app \
  && useradd --no-log-init -m -g app app \
  && chown app /app
USER app

# uvバイナリを配置
COPY --from=ghcr.io/astral-sh/uv:0.9.17 /uv /bin/

FROM base AS local
# 依存関係の解決のみ先に実行
RUN --mount=type=cache,target=/app/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --group dev --no-install-project
EXPOSE 8080
CMD ["uv", "run", "fastapi", "dev", "--host", "0.0.0.0", "--port", "8080"]

FROM base AS production
COPY --chown=app:app . /app
RUN uv sync --frozen
EXPOSE 8080
CMD ["uv", "run", "fastapi", "run", "--host", "0.0.0.0", "--port", "8080"]
