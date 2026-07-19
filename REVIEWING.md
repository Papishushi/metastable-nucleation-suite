# Reviewing Metastable Nucleation Suite

MNS welcomes narrow, critical and independent review. You do not need to understand or audit the whole repository.

The project spans experimental nucleation, optical metastability, Bell/no-signalling analysis, scientific software, semantic provenance and the speculative NECE materials programme. A useful review can focus on one equation, one assumption, one experimental control, one reference or one software boundary.

## Start here

The central call for reviewers is [issue #74](https://github.com/Papishushi/metastable-nucleation-suite/issues/74).

Current priority reviews:

1. [PR #61](https://github.com/Papishushi/metastable-nucleation-suite/pull/61): NECE physical definition, information model and fabrication path.
2. [PR #60](https://github.com/Papishushi/metastable-nucleation-suite/pull/60): scalar capacity, energy and compute-ceiling model.
3. [Issues #38–#40](https://github.com/Papishushi/metastable-nucleation-suite/issues/37): first real single-node optical validation programme.
4. [PR #62](https://github.com/Papishushi/metastable-nucleation-suite/pull/62): competitor comparison and technological go/no-go criteria.
5. [PR #59](https://github.com/Papishushi/metastable-nucleation-suite/pull/59): Metastate Atlas and nucleation-defined circuitry.
6. [PR #46](https://github.com/Papishushi/metastable-nucleation-suite/pull/46): provenance-preserving Rust/WASM visualization boundary.

## Reviews that help

A review may do any of the following:

- identify an unsupported or overstated scientific claim;
- propose a stronger null model or adversarial test;
- identify contamination, drift, postselection, timing or classification risks;
- challenge an independence, energy, capacity or scaling assumption;
- verify or replace a primary reference;
- assess whether a proposed experiment is fabricable, measurable and falsifiable;
- check whether measured, simulated, inferred and illustrative information remain distinguishable;
- provide a synthetic dataset that should expose a failure;
- recommend a no-go decision.

Negative conclusions are useful. The project is intended to eliminate weak explanations and overclaims before escalating an experiment.

## Suggested review format

Please include:

```text
Domain/perspective:
Reviewed artifact:
Finding type: blocking | recommended | exploratory
Finding:
Why it matters:
Suggested test or change:
References or assumptions:
Conflict of interest, if any:
```

Line comments are useful for local problems. A summary review or focused issue is better for cross-cutting scientific concerns.

## Domain-specific entry points

### Nucleation, metastability and experimental design

- `docs/01_marco_cientifico.md`
- `docs/02_matriz_hipotesis.md`
- `docs/03_suite_experimentos.md`
- `docs/12_matriz_de_fallos_y_lagunas.md`
- issues #37–#40

Questions to ask:

- Are the ordinary physical explanations sufficiently broad?
- Are reset, memory, drift and batch effects operationally testable?
- Are stage transitions protected by objective go/no-go criteria?

### Statistics, Bell and no-signalling

- `docs/05_estadistica_y_falsacion.md`
- E10–E13 in `experiments/specifications.yaml`
- `src/metastable_suite/monte_carlo_power.py`

Questions to ask:

- Can memory, optional stopping, coincidence selection or setting-dependent loss create the result?
- Is the trial definition fixed independently of the observed outcomes?
- Does the no-signalling analysis use all locally valid trials rather than selected coincidences?

### Phase-change materials and NECE

- issue #50 and child issues #51–#58
- PRs #61 and #62
- issues #67, #68, #71 and #73

Questions to ask:

- Is NECE distinct from scalar multilevel PCM in a measurable way?
- Can iso-aggregate configurations be repeatedly written and blindly decoded?
- Do thermal coupling, domain growth and readout overhead destroy the proposed gain?

### Information theory and quantitative modelling

- PRs #60 and #61
- issues #67 and #68

Questions to ask:

- Are unknown values distinguished from physical zero?
- Are uncertainties and correlations propagated?
- Is recoverable information derived from a write/read channel rather than combinatorial counting alone?

### Scientific software and provenance

- `docs/11_contrato_de_datos.md`
- `docs/13_ontologia_semantica.md`
- `docs/14_motor_ejecucion_hardware_y_potencia.md`
- issue #41 and PR #46

Questions to ask:

- Can invalid trials disappear silently?
- Can derived geometry be mistaken for measured geometry?
- Are every transformation and exclusion linked to source artifacts and hashes?

## Running checks

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
make check
```

A passing check means that the implementation is internally consistent with its tests and contracts. It does not establish experimental truth, peer review or independent replication.

## Reviewer recognition

Reviewers may remain pseudonymous. With permission, substantive reviews can be acknowledged in release notes, documentation or a future reviewer record. Credentials are not required for a technically supported criticism, and claimed credentials are not treated as verified without an attributable source.

## Conduct

Critique claims, assumptions, methods and code—not people. Declare uncertainty. Distinguish a demonstrated error from a concern that still needs testing. The maintainer should answer substantive criticism on technical grounds and preserve unresolved objections in the review record.
