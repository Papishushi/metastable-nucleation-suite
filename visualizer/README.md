# Metastable visualizer

This crate is the Rust/WASM boundary for issue #41. The first foundation provides:

- an opaque `ValidatedScene` produced by one strongly typed parse-and-validate operation;
- stable validation error codes and JSON paths for browser and native hosts;
- a shared JSON Schema/Rust/WASM conformance corpus;
- record-level provenance and scientific-integrity validation before GPU upload;
- adapter capabilities that advertise E09 independently of generic experiment-ID syntax;
- an explicit WebGPU-first, WebGL2-fallback `wgpu` policy;
- native unit tests and a `wasm32-unknown-unknown` compile target.

It intentionally contains no TypeScript or handwritten JavaScript application logic. CI
rejects those files except for two exact generated `wasm-bindgen` output paths documented
in ADR 0002. Browser bootstrap packaging and the first render pipeline follow after the
scene boundary is accepted.

```bash
cargo fmt --check
cargo clippy --locked --all-targets -- -D warnings
cargo clippy --locked --target wasm32-unknown-unknown --lib --tests -- -D warnings
cargo test --locked
wasm-pack test visualizer --headless --chrome -- --locked --test wasm
cargo build --locked --release --target wasm32-unknown-unknown
```
