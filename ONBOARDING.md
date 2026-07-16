# Contributor onboarding

You do not need to understand the whole Metastable Nucleation Suite (MNS) repository before contributing. Start with one bounded artifact, one testable outcome and one validation command.

MNS separates measured, simulated, derived, inferred and illustrative information. A passing test proves consistency with the implemented contracts; it does not prove a physical claim.

## Choose a contribution lane

| Lane | Start with | Typical first contribution |
|---|---|---|
| Scientific Python | `src/metastable_suite/`, `tests/` | Regression test, synthetic adversarial case or clearer diagnostic |
| Data and semantics | `schemas/`, `contracts/`, `ontology/` | Example validation, SHACL test or provenance clarification |
| .NET operations | `dotnet/`, `services/`, `compose.yaml` | CLI test, health-check documentation or fail-closed boundary |
| Rust/WASM visualizer | `visualizer/`, issue #41 | Contract test, deterministic fixture or accessibility documentation |
| Documentation and CI | `docs/`, `.github/`, `scripts/` | Broken link, quickstart, workflow check or contributor tooling |
| Independent review | `REVIEWING.md`, issue #74 | Focused review of one claim, equation, reference, control or software boundary |

The [architecture and contribution map](docs/18_architecture_and_contribution_map.md) explains how these areas connect.

## Thirty-minute local path

Prerequisites: Git, Python 3.10 or newer and a shell. Other toolchains are only needed for their own lane.

```bash
git clone https://github.com/Papishushi/metastable-nucleation-suite.git
cd metastable-nucleation-suite
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
make check
```

If `make` is unavailable on Windows, use the equivalent commands defined in `Makefile` and describe that limitation in issue #93. A dedicated Windows quickstart is tracked as contributor work.

## Find a first task

1. Look for issues labelled `good first issue` and `help wanted`.
2. Prefer a task whose acceptance criteria fit one coherent pull request.
3. Comment on the issue before substantial work so scope and dependencies remain visible.
4. If no task fits, use [issue #93](https://github.com/Papishushi/metastable-nucleation-suite/issues/93) for contribution matching.

A first contribution should normally avoid changing scientific claims, experiment gates or public schemas unless the issue explicitly requires it.

## Pull-request expectations

Read `CONTRIBUTING.md` before opening a pull request. Link the PBI using `Closes #N`, state the delivered outcome and list the checks actually run.

For documentation, CI or tooling changes, hypothesis and null-prediction fields may be marked `Not applicable` with a short reason. Do not invent a scientific hypothesis to satisfy a template.

For scientific or statistical changes, include assumptions, null behaviour, confounders and regression evidence. Exploratory findings must remain distinguishable from confirmatory results.

## Asking for help

Use issue #93 for installation, architecture and task-selection questions. Use issue #74 for independent review volunteering. Security vulnerabilities must follow `SECURITY.md` and must not be posted publicly.

All participation is governed by `CODE_OF_CONDUCT.md`.