# Community, outreach and publication plan

## Positioning

MNS should be presented as open infrastructure for reproducible protocols, explicit data contracts, semantic provenance and critical review. It must not be marketed as proof of extraordinary physical claims.

Core message:

> MNS separates measured, simulated, derived, inferred and reviewed outputs so that hypotheses can be tested, criticised and rejected without hiding the evidence boundary.

## Target contributor groups

| Group | Relevant entry point | Useful contribution |
|---|---|---|
| Research software engineers and Scientific Python contributors | Python core, tests, scripts, packaging | Reproducibility, diagnostics, fixtures and release quality |
| Semantic-web and knowledge-graph contributors | Ontology, SHACL, JSON-LD and SPARQL | Provenance constraints, examples and validation |
| .NET platform engineers | CLI, Kestrel control plane and Extend0 boundary | Capability checks, recovery and operational safety |
| Rust/WASM and WebGPU contributors | Visualizer and scene contracts | Deterministic rendering, accessibility and browser integration |
| Experimental physicists and materials researchers | Issues #37–#40, #50 and reviewer call #74 | Controls, feasibility, fabrication and no-go reviews |
| Statistics and information-theory reviewers | Bell/no-signalling and capacity models | Null models, uncertainty, channel models and adversarial tests |

## Outreach sequence

1. **Foundation:** merge governance, onboarding, security and architecture documentation.
2. **Contribution inventory:** maintain 8–12 bounded `good first issue` tasks with explicit stack, first file and validation command.
3. **Review bundles:** publish a monthly group of at most three focused artifacts in issue #74. Each review should be possible without auditing the whole repository.
4. **Technical communication:** publish short posts on reproducibility, semantic provenance, release engineering and evidence-preserving visualization.
5. **Community events:** prepare a reliable demo and curated sprint backlog for Scientific Python or research-software events.
6. **Publication:** submit the software as research infrastructure before attempting strong papers about unvalidated physical results.

Do not create a permanent chat server until there is enough recurring participation to moderate it. Issue #93 is the initial asynchronous entry point.

## Software-publication strategy

Keep publications separated by claim type:

- **Software paper:** architecture, installation, contracts, tests, reproducibility, releases and reuse. JOSS or JORS are the primary candidates; SoftwareX is a possible extended route.
- **Method or architecture preprint:** semantic provenance, evidence-status separation or executable experimental protocols. Verify current venue and preprint requirements before submission.
- **Experimental papers:** only after the relevant physical gate is completed, preregistered evidence exists and the claim boundary is independently reviewed.

A software manuscript should not use continuous integration, simulations or repository completeness as evidence that a physical hypothesis is true.

## Six-month execution roadmap

| Horizon | Deliverable | Exit condition |
|---|---|---|
| Month 1 | Governance, security, onboarding and architecture map | A newcomer can identify a lane and reporting path |
| Month 1 | Initial `good first issue` inventory | At least eight bounded tasks are open and labelled |
| Month 2 | Deterministic public demo and module index | A new user can produce and inspect one synthetic artifact |
| Month 2 | First focused reviewer bundle | Three bounded review requests are published in #74 |
| Month 3 | Technical post series and outreach kit | Reusable accurate messaging exists in English and Spanish |
| Month 4 | Event demo or sprint proposal | Tasks, setup and facilitator notes are ready |
| Month 4–5 | Software-paper draft and external technical read | Scope excludes unsupported physical claims |
| Month 6 | KPI and governance review | #72 records what worked, stalled or should stop |

## KPIs

Track outcomes rather than vanity alone:

- median maintainer response time to a first external contribution;
- number of open, genuinely bounded `good first issue` tasks;
- external issue authors, pull-request authors and merged contributors;
- substantive independent reviews recorded through #74;
- time from first contributor comment to first review;
- successful clean-install and release-smoke reports;
- citations, archived releases and software-paper status;
- contributor retention after the first merged change.

Stars and forks are discovery signals, not evidence of scientific or community maturity.

## Social copy

### English

> MNS is an open platform for executable protocols, data contracts, semantic provenance and reproducible execution around metastability and nucleation research. We are looking for focused reviewers and contributors in scientific Python, semantics, .NET, Rust/WASM, experimental design, materials and statistics. Critical reviews and technically supported no-go conclusions are welcome.

### Español

> MNS es una plataforma abierta para protocolos ejecutables, contratos de datos, procedencia semántica y ejecución reproducible en investigación sobre metaestabilidad y nucleación. Buscamos revisores y colaboradores en Python científico, semántica, .NET, Rust/WASM, diseño experimental, materiales y estadística. Las críticas fundamentadas y las conclusiones no-go son resultados útiles.