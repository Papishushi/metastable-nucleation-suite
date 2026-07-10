.PHONY: install test lint validate simulate check

install:
	python -m pip install -e .[dev]

test:
	pytest -q

lint:
	ruff check .

validate:
	python scripts/validate_catalog.py

simulate:
	python scripts/run_suite.py --trials 80000 --seed 7

check: lint validate test simulate
