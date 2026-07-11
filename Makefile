.PHONY: install test lint validate simulate plan semantic check

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
	python scripts/semantic_graph.py validate ontology/examples/reference-run.jsonld

simulate:
	python scripts/run_suite.py --trials 80000 --seed 7

plan:
	python scripts/plan_experiment.py --experiment chsh --target-s 2.4 --output artifacts/chsh-plan.json

semantic:
	python scripts/semantic_graph.py from-report artifacts/reference_report.json artifacts/reference_run.jsonld --run-id local-reference
	python scripts/semantic_graph.py query artifacts/reference_run.jsonld ontology/queries/completed-runs.rq

check: lint validate test plan simulate semantic
