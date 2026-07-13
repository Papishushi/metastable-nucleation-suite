# ADR 0002: Rust/WASM boundary for the scientific visualizer

## Status

Accepted.

## Context

Issue #41 introduces an interactive three-dimensional viewer for physical experiment
geometry and abstract metastable configuration spaces. The viewer must process large,
chunked datasets, retain source provenance and run in a browser without a user-managed
runtime. It must also leave open a native renderer using the same scientific scene model.

Blazor WebAssembly would reuse the platform's C# skills, but it would add the .NET browser
runtime and a second graphics abstraction at the most performance-sensitive boundary.
Browser WebGPU access would still require bindings and interop that do not improve the
scientific contract. A JavaScript or TypeScript graphics framework would make the browser
implementation the architectural centre and would not provide the required native path.

## Decision

Implement the visualizer core in Rust 2024, compiled to `wasm32-unknown-unknown`, with
`wgpu` as the graphics abstraction. WebGPU is the preferred browser backend and WebGL2 is
the compatibility fallback. The same `wgpu` renderer may later target Vulkan, Metal,
Direct3D 12 or OpenGL in a native host.

The boundary is intentionally strict:

- scene parsing, validation, state, filtering, playback and rendering live in Rust/WASM;
- no handwritten TypeScript or JavaScript application logic is allowed;
- generated bootstrap code may only instantiate WASM and expose browser primitives;
- DOM, file-picker and browser lifecycle access uses narrow generated bindings;
- Python projects canonical scientific artifacts into a versioned scene contract;
- .NET 10 launches and serves the packaged viewer and integrates distributed APIs;
- neither Python, .NET nor Rust imports another component's internal models.

The visualization scene is a derived projection. JSON-LD/RDF remains canonical for
semantics and provenance, and Arrow/Parquet remains canonical for high-volume events.
Every renderable item links back to immutable source-artifact identifiers and hashes.

## Scientific constraints

The scene contract records whether a layer is measured, derived, inferred or illustrative.
Physical and abstract coordinate systems are explicit. A renderer must never silently
interpolate measured transitions, hide invalid observations or present model-derived
geometry as measured apparatus geometry.

Version 1 starts with a document scene suitable for deterministic fixtures. Chunk and
stream transport will be a separate contract so large-run delivery can evolve without
changing the meaning of a scene.

## Packaging

Rust is pinned through `rust-toolchain.toml`. Release builds produce a WASM module and only
the generated host bootstrap needed by the browser. Users do not install Rust, Cargo,
Node.js or npm. The assets are bundled into all supported self-contained .NET release
archives and the relevant container image by the release work in #33.

## Consequences

The repository gains a Rust toolchain and Cargo dependency supply chain. CI must format,
lint, test and compile the crate for WASM. This cost is accepted because the visualizer is
an isolated graphics boundary with a real cross-platform and performance requirement,
which satisfies the exception established by ADR 0001.

UI work that is not part of the visualizer remains eligible for .NET. This decision does
not introduce Rust into the scientific worker or operational control plane.
