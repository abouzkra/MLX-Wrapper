MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

install:
	uv sync

run:
	uv run python -m src

debug:
	uv run python -m pdb src

lint:
	uv run flake8 . --exclude=.venv,llm_sdk
	uv run mypy . --exclude .venv --exclude llm_sdk $(MYPY_FLAGS)

clean:
	rm -rf .venv/
	rm -rf $$(find . -name "__pycache__" -o -name ".mypy_cache")
