MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

install:
	uv sync

wheel:
	uv build --wheel

run:
	uv run python main.py

debug:
	uv run python -m pdb main.py

lint:
	uv run flake8 . --exclude=.venv
	uv run mypy . --exclude .venv $(MYPY_FLAGS)

clean:
	rm -rf .venv/
	rm -rf dist/
	rm -rf $$(find . -name "__pycache__" -o -name ".mypy_cache")
