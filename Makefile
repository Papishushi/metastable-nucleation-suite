.PHONY: install test lint validate simulate plan power semantic execute check

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

power:
	python scripts/monte_carlo_power.py --design chsh --sample-size 4000 --visibility 0.95 --alpha 0.05 --repetitions 300 --output artifacts/chsh-power.json

semantic:
	python scripts/semantic_graph.py from-report artifacts/reference_report.json artifacts/reference_run.jsonld --run-id local-reference
	python scripts/semantic_graph.py query artifacts/reference_run.jsonld ontology/queries/completed-runs.rq

execute:
	python scripts/semantic_execute.py ontology/examples/planned-e09.jsonld artifacts/execution

check: lint validate test plan power simulate semantic execute
