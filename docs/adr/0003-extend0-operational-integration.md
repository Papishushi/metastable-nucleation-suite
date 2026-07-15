# ADR 0003: Bounded Extend0 integration in the .NET operational layer

## Status

Accepted.

## Context

The suite already assigns operational CLIs, APIs, orchestration, telemetry and device-facing services to .NET 10. The next distributed slice in #34 needs durable operational state, service ownership, liveness and coordination, while the standalone CLI needs to remain self-contained.

[Extend0](https://github.com/Papishushi/Extend0) targets .NET 10 and provides two relevant systems:

- Lifecycle for service identity, unique ownership, liveness and transport-mediated access;
- MetaDB for schema-defined metadata tables, references, indexes and storage-backed operational state.

The suite also has stronger scientific data guarantees that Extend0 must not blur. JSON-LD/RDF ABoxes, SHACL validation, event manifests, NDJSON/Parquet datasets and content hashes are the scientific record. Capability manifests and contracts under `contracts/` are the public cross-process and cross-language boundary.

## Decision

Adopt Extend0 as a bounded dependency of the suite's .NET operational layer.

The integration pins the stable Extend0 NuGet package to `1.1.9691.41434`, adds an executable `metastable-platform extend0 doctor` diagnostic and constructs managers through the published `MetaDB.CreateManager()` facade. The distributed control plane uses `CrossProcessSingleton<IRunOrchestrator>` as the single-owner dispatch boundary and stores derived run/artifact indexes in explicit MetaDB schemas. The package is consumed by .NET projects only; Python workers, F# scientific domain rules and Rust/WASM visualization code do not import Extend0 types.

### Lifecycle boundary

Lifecycle may be used by the Kestrel control plane and local operational services for:

- stable service identity;
- explicit owner/client roles;
- single-owner coordination within a declared process, machine or network scope;
- liveness and endpoint diagnostics;
- transport-mediated access where the operational topology requires it.

Lifecycle does not replace HTTP APIs, capability negotiation, authentication, authorization, idempotency or the versioned message contracts. Remote clients continue to use the suite's public API rather than an Extend0 internal proxy contract.

### MetaDB boundary

MetaDB may persist or index:

- queued and running job state;
- idempotency and dispatch metadata;
- worker and device endpoint metadata;
- derived run and artifact lookup indexes;
- recovery checkpoints for operational services.

MetaDB is not the canonical store for experiment definitions, completed ABoxes, measurements, event datasets, provenance or artifact hashes. Every MetaDB record that refers to scientific material must use immutable suite identifiers or hashes. Operational indexes must be rebuildable from canonical artifacts wherever possible.

Deleting or rebuilding a MetaDB index must never mutate a scientific artifact. Recovery semantics for accepted work are defined by the control-plane contract in #34, not inferred from MetaDB implementation details.

### Ontology boundary

The Extend0 ontology describes Extend0 platform concepts. The suite ontology describes experiments, execution, devices, datasets and provenance. Any alignment between them must be explicit and reviewed as a mapping. The suite does not import the complete Extend0 TBox and does not expose Extend0 implementation classes as scientific concepts.

### Dependency and compatibility policy

- The NuGet dependency is pinned exactly; floating versions are forbidden. Version `1.1.9691.41434` exposes the supported `MetaDB.CreateManager()` facade, incorporates the completed cross-platform file-semantics work from [Extend0 #5](https://github.com/Papishushi/Extend0/issues/5), and is validated on Windows, Linux and macOS, including native ARM64 release smoke. Durable suite schemas and recovery behavior still require the control-plane contracts and tests in #34.
- An Extend0 upgrade is independent from the suite semantic version and requires restore, analyzer, self-test, publish and clean-machine smoke coverage on all six release RIDs.
- Release SBOM and provenance must record the resolved package version.
- Package compatibility is established by tests and documented contracts, not by assuming that matching .NET target frameworks imply behavioral compatibility.
- If the package cannot satisfy self-contained publishing, security, recovery or corruption requirements, the integration remains replaceable behind suite-owned operational interfaces.

## Consequences

The suite reuses Extend0's operational systems instead of creating another singleton, coordination and metadata framework. Kestrel instances resolve one orchestration owner; only that owner mutates the MetaDB run and artifact tables or dispatches work. Queued work is resumed after restart, while interrupted running work enters the explicit `recovery_required` state rather than being repeated silently.

The dependency adds supply-chain and compatibility surface to release builds. Exact version pinning, SBOM coverage and multi-RID smoke tests therefore become mandatory. Extend0 remains an implementation detail of the .NET operational boundary; scientific artifacts and public APIs stay portable if the implementation is replaced.

## Alternatives considered

### Copy Extend0 source into this repository

Rejected because it would fork ownership, hide version provenance and make security updates harder to audit.

### Add Extend0 as a Git submodule

Rejected for the initial integration because recursive checkout complicates source archives, release automation and contributor onboarding. A package dependency gives the release pipeline an explicit versioned input.

### Replace RDF/JSON-LD and artifact manifests with MetaDB

Rejected because it would collapse operational indexing into the scientific source of truth and weaken portability, provenance and cross-language validation.

### Defer all coordination until the Kestrel service exists

Rejected because a small diagnostic slice now validates dependency restoration, self-contained publication and runtime construction before those concerns become entangled with the control plane.

## Follow-up

Tracked by #45. The first durable consumer lands with #34; migration, corruption and clean-release expansion remain integration follow-ups. Extend0 portability issue [#5](https://github.com/Papishushi/Extend0/issues/5) is completed and the stable package has native ARM64 validation; those platform guarantees do not replace suite-specific recovery tests.
