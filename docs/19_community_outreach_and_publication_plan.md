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
2. **Persistent identity:** enable Zenodo archiving, publish an immutable release DOI and expose the concept DOI for project-level citation.
3. **Contribution inventory:** maintain 8–12 bounded `good first issue` tasks with explicit stack, first file and validation command.
4. **Review bundles:** publish a monthly group of at most three focused artifacts in issue #74. Each review should be possible without auditing the whole repository.
5. **Technical communication:** publish short posts on reproducibility, semantic provenance, release engineering and evidence-preserving visualization.
6. **Community events:** prepare a reliable demo and curated sprint backlog for Scientific Python or research-software events.
7. **Preprint and publication:** publish an arXiv software or methods preprint tied to an exact Zenodo release, then submit the software paper to the selected venue.

Do not create a permanent chat server until there is enough recurring participation to moderate it. Issue #93 is the initial asynchronous entry point.

## Software-publication strategy

Keep publications and identifiers separated by claim type:

- **Zenodo software archive:** immutable DOI for each cited release plus a concept DOI for the evolving project. `CITATION.cff` is the canonical metadata source.
- **arXiv software or methods preprint:** public manuscript describing architecture, reproducibility, evidence boundaries and reuse. The preprint must cite the exact Zenodo version DOI, tag and commit used.
- **Software paper:** architecture, installation, contracts, tests, reproducibility, releases and reuse. JOSS or JORS are the primary candidates; SoftwareX is a possible extended route.
- **Experimental papers:** only after the relevant physical gate is completed, preregistered evidence exists and the claim boundary is independently reviewed.

The complete identifier, source-hygiene and cross-link procedure is defined in [docs/20_zenodo_arxiv_archiving_workflow.md](20_zenodo_arxiv_archiving_workflow.md).

A DOI, arXiv identifier, software-paper acceptance, passing CI or repository completeness must never be described as evidence that a physical hypothesis is true.

## Zenodo execution gate

The maintainer must connect the repository to Zenodo through the authorised account. Once enabled, new GitHub releases are automatically ingested and archived by Zenodo.

Repository work must prepare this gate by:

- maintaining complete `CITATION.cff` metadata;
- aligning version and release-date metadata before each tag;
- preserving immutable tags and archived release assets;
- adding DOI badges and identifiers only after Zenodo returns real values;
- recording the concept DOI separately from each version DOI.

This work is tracked in #104.

## arXiv execution gate

arXiv submission must be performed by a registered author and may require endorsement for a new category. The repository should provide clean, compilable manuscript sources, but it must not automate submission with stored author credentials.

Repository work must prepare this gate by:

- maintaining a minimal manuscript source tree under `paper/arxiv/`;
- compiling the exact upload archive in a clean environment;
- excluding secrets, hidden metadata, drafts and unrelated repository files;
- verifying title, abstract, figures, references, licence and category metadata;
- updating README, `CITATION.cff`, Zenodo and issue #103 only after a real arXiv identifier exists.

This work is tracked in #105.

## Six-month execution roadmap

| Horizon | Deliverable | Exit condition |
|---|---|---|
| Month 1 | Governance, security, onboarding and architecture map | A newcomer can identify a lane and reporting path |
| Month 1 | Zenodo repository activation and first archived release | Real version DOI and concept DOI are recorded |
| Month 1 | Initial `good first issue` inventory | At least eight bounded tasks are open and labelled |
| Month 2 | Deterministic public demo and module index | A new user can produce and inspect one synthetic artifact |
| Month 2 | First focused reviewer bundle | Three bounded review requests are published in #74 |
| Month 3 | Technical post series and outreach kit | Reusable accurate messaging exists in English and Spanish |
| Month 4 | Event demo or sprint proposal | Tasks, setup and facilitator notes are ready |
| Month 4–5 | arXiv-ready manuscript and external technical read | Clean source archive compiles and cites an exact Zenodo release |
| Month 5 | arXiv preprint submission | Real identifier and source version are recorded |
| Month 5–6 | Software-paper submission | Scope excludes unsupported physical claims |
| Month 6 | KPI and governance review | #72 and #103 record what worked, stalled or should stop |

## KPIs

Track outcomes rather than vanity alone:

- median maintainer response time to a first external contribution;
- number of open, genuinely bounded `good first issue` tasks;
- external issue authors, pull-request authors and merged contributors;
- substantive independent reviews recorded through #74;
- time from first contributor comment to first review;
- successful clean-install and release-smoke reports;
- Zenodo releases archived successfully and DOI metadata consistency;
- arXiv manuscript build, submission and version status;
- software-paper submission and review status;
- citations that identify an exact release rather than only the moving repository;
- contributor retention after the first merged change.

Stars and forks are discovery signals, not evidence of scientific or community maturity.

## Social copy

### English

> MNS is an open platform for executable protocols, data contracts, semantic provenance and reproducible execution around metastability and nucleation research. Releases will be archived for persistent citation once the Zenodo repository gate is complete, and the software/methods manuscript will be published as an openly reviewable preprint. We are looking for focused reviewers and contributors in scientific Python, semantics, .NET, Rust/WASM, experimental design, materials and statistics. Critical reviews and technically supported no-go conclusions are welcome.

### Español

> MNS es una plataforma abierta para protocolos ejecutables, contratos de datos, procedencia semántica y ejecución reproducible en investigación sobre metaestabilidad y nucleación. Las releases se archivarán con identificadores persistentes y el manuscrito de software o metodología se publicará como preprint abierto. Buscamos revisores y colaboradores en Python científico, semántica, .NET, Rust/WASM, diseño experimental, materiales y estadística. Las críticas fundamentadas y las conclusiones no-go son resultados útiles.
