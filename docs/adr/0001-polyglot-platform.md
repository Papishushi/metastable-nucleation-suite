# ADR 0001: Polyglot platform and deployment boundaries

## Status

Accepted.

## Decision

Keep scientific simulation, Monte Carlo, RDF/OWL/SHACL and exploratory analysis in Python while they remain the most productive and validated implementations. Use C#/.NET for operational CLIs, APIs, orchestration, telemetry and device-facing services. Use F# selectively for immutable domain rules and state machines where its type system materially reduces invalid states. Introduce Rust/C++ only after profiling demonstrates a native-performance or latency requirement.

No component is migrated merely for language uniformity.

## Reference architectures

### Standalone

```text
self-contained .NET CLI
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

## Packaging

- .NET CLI and agents: self-contained single-file for `win-x64`, `win-arm64`, `linux-x64`, `linux-arm64`, `osx-x64` and `osx-arm64`.
- Native AOT is evaluated per executable; reflection-heavy or incompatible components remain self-contained.
- Scientific Python: Debian slim container by default because NumPy, SciPy, Arrow, VISA and vendor libraries commonly depend on glibc-compatible native wheels.
- .NET services: chiseled/runtime-deps images by default; Alpine only after musl compatibility is demonstrated.
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

The platform has explicit process and contract boundaries. Internal Python and .NET classes are not shared. Cross-language messages use versioned contracts under `contracts/`.
