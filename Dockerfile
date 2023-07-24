# syntax=docker/dockerfile:1

# The builder image, used to build the virtual environment
FROM python:3.11-buster as builder

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install poetry==1.5.1

WORKDIR /app

COPY pyproject.toml poetry.lock README.md ./

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.11-slim-buster as runtime

RUN set -ex; \
    apt-get update; \
    apt-get install -y --no-install-recommends curl libyaml-dev; \
    apt-get clean -y;

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

ENV PROMETHEUS_DISABLE_CREATED_SERIES=true

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY merger ./merger

ENTRYPOINT ["python", "-m", "merger"]
