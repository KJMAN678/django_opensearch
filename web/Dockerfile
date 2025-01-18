FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.5.21 /uv /bin/uv

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app/web
COPY . /app/web
RUN uv sync --dev
