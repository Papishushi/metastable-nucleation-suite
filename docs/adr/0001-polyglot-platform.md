# ADR 0001: Polyglot platform and deployment boundaries

## Status

Accepted.

## Decision

Keep scientific simulation, Monte Carlo, RDF/OWL/SHACL and exploratory analysis in Python while they remain the most productive and validated implementations. Use C#/.NET 10 for operational CLIs, APIs, orchestration, telemetry and device-facing services. Use F# on .NET 10 selectively for immutable domain rules and state machines where its type system materially reduces invalid states. Introduce Rust/C++ only after profiling demonstrates a native-performance or latency requirement.

No component is migrated merely for language uniformity. The operational baseline is .NET 10, pinned through `global.json`; new .NET components must not target an older framework unless a separate compatibility ADR justifies it.

## Reference architectures

### Standalone

```text
self-contained .NET 10 CLI
        |
        +-- local packaged Python worker
        |       +-- semantic validation
        |       +-- simulation / Monte Carlo
        |       +-- Parquet / JSON-LD artifacts
        +-- local device adapters
```

A central server is not required. The distribution contains its runtimes and must not require a user-managed Python or .NET installation.

### Distributed

```text
optional Nginx edge
        |
ASP.NET Core/Kestrel operational service
        |
        +-- scientific Python worker
        +-- device agents
        +-- persisted artifacts
```

A central operational service is required only for shared scheduling, remote access, multi-user coordination or distributed device nodes. YARP is introduced only for dynamic routing or device-node proxying. Nginx is limited to edge TLS, static assets, caching or one external entrypoint. Kestrel hosts application APIs; these responsibilities must not overlap without an explicit ADR.

## Capability negotiation

Every remotely versioned operation has a stable capability identifier. Servers expose a versioned manifest at `GET /v1/capabilities`, validated against `contracts/v1/server-capabilities.schema.json`.

Clients must discover and gate capabilities before invoking remote operations:

- missing capability: reject locally as unsupported;
- `active`: execute normally;
- `deprecated`: execute with a warning and prefer the advertised replacement;
- unknown state or unsupported manifest version: fail closed;
- removal: only after the deprecation window or through a new API major version.

Capability identifiers are versioned independently from deployment versions, for example `experiments.execute.v1`. This prevents a server version comparison from becoming a proxy for actual feature compatibility.

## Packaging

- .NET 10 CLI and agents: self-contained single-file for `win-x64`, `win-arm64`, `linux-x64`, `linux-arm64`, `osx-x64` and `osx-arm64`.
- Native AOT is evaluated per executable; reflection-heavy or incompatible components remain self-contained.
- Scientific Python: Debian slim container by default because NumPy, SciPy, Arrow, VISA and vendor libraries commonly depend on glibc-compatible native wheels.
- .NET 10 services: Ubuntu Noble chiseled/runtime-deps images by default; Alpine only after musl compatibility is demonstrated.
- Nginx Alpine is acceptable only for edge/static responsibilities.

## Migration decision matrix

| Evidence | Keep current language | Consider migration |
|---|---|---|
| Correct and maintainable | Yes | No |
| Deployment friction | Package runtime first | Migrate only if packaging remains unacceptable |
| Type-safety defects | Add schemas/tests | F# or C# when invalid states dominate |
| Operational/API workload | Python may remain worker | C#/.NET preferred for new operational boundary |
| Measured latency bottleneck | Optimize/profile first | Rust/C++ for the isolated hot path |
| Hard real-time requirement | No managed-runtime assumption | Firmware/FPGA/native control path |

## Consequences

The platform has explicit process and contract boundaries. Internal Python and .NET classes are not shared. Cross-language messages use versioned contracts under `contracts/`. Clients negotiate concrete capabilities instead of inferring support from server versions.
