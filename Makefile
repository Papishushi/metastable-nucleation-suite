.PHONY: install test lint validate simulate plan check

install:
	python -m pip install -e .[dev]

test:
	pytest -q

lint:
	ruff check .

validate:
	python scripts/validate_catalog.py
	python scripts/validate_specifications.py
	python scripts/verify_references.py --no-network

simulate:
	python scripts/run_suite.py --trials 80000 --seed 7

plan:
	python scripts/plan_experiment.py --experiment chsh --target-s 2.4 --output artifacts/chsh-plan.json

check: lint validate test plan simulate
