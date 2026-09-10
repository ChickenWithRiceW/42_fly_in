ENTRY = src
MAP = "example_map.txt"

install:
	uv sync

run: install
	uv run python -m $(ENTRY) $(MAP)

debug: install
	uv run python -m pdb $(ENTRY)

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +

lint:
	uv run flake8 src/ $(ENTRY)
	uv run mypy src/
	uv run mypy $(ENTRY)

lint-strict:
	uv run flake8 src/ $(ENTRY)
	uv run mypy src/ --strict
	uv run mypy $(ENTRY) --strict
