FROM python:3.11-slim

ENV UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_LINK_MODE=copy \
    UV_FROZEN=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY --from=ghcr.io/astral-sh/uv:latest /uvx /usr/local/bin/uvx

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --extra dev --frozen

COPY . .

CMD ["uv", "run", "pytest", "tests/"]
