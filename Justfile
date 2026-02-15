default:
    @just --choose

setup:
    uv sync

build:
    uv build

test:
    uv run pytest

lint:
    uv run ruff check

format:
    uv run ruff format

check: lint test
    uv run ruff format --check

docs output="doc/html/":
    uv run --group doc sphinx-build doc/ doc/html/


