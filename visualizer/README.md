# Metastable visualizer

This crate is the Rust/WASM boundary for issue #41. The first foundation provides:

- an opaque `ValidatedScene` produced by one strongly typed parse-and-validate operation;
- stable validation error codes and JSON paths for browser and native hosts;
- a shared JSON Schema/Rust/WASM conformance corpus;
- record-level provenance and scientific-integrity validation before GPU upload;
- adapter capabilities that advertise E09 independently of generic experiment-ID syntax;
- an explicit WebGPU-first, WebGL2-fallback `wgpu` policy;
- deterministic E09 render state that retains scientific roles, exclusions, uncertainty and
  record-level provenance;
- a native/WASM-shared orbit camera and selection model for pointer and keyboard adapters;
- native unit tests and a `wasm32-unknown-unknown` compile target.

It intentionally contains no TypeScript or handwritten JavaScript application logic. CI
rejects those files except for two exact generated `wasm-bindgen` output paths documented
in ADR 0002. The current #44 increment prepares validated GPU inputs and deterministic
interaction state. Browser canvas ownership, surface configuration, shaders and the first
visible frame remain before the draft can be marked ready for review.

```bash
cargo fmt --check
cargo clippy --locked --all-targets -- -D warnings
cargo clippy --locked --target wasm32-unknown-unknown --lib --tests -- -D warnings
cargo test --locked
CARGO_TARGET_WASM32_UNKNOWN_UNKNOWN_RUNNER=wasm-bindgen-test-runner \
  CHROMEDRIVER=/usr/bin/chromedriver WASM_BINDGEN_TEST_ONLY_WEB=1 \
  cargo test --locked --target wasm32-unknown-unknown --test wasm
cargo build --locked --release --target wasm32-unknown-unknown
```
