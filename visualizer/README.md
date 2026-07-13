# Metastable visualizer

This crate is the Rust/WASM boundary for issue #41. The first foundation provides:

- a strongly typed reader for `contracts/v1/visualization-scene.schema.json`;
- cross-reference and scientific-integrity validation before GPU upload;
- an explicit WebGPU-first, WebGL2-fallback `wgpu` policy;
- native unit tests and a `wasm32-unknown-unknown` compile target.

It intentionally contains no TypeScript or handwritten JavaScript application logic.
Browser bootstrap packaging and the first render pipeline follow after the scene boundary is
accepted.

```bash
cargo fmt --check
cargo clippy --all-targets -- -D warnings
cargo test
cargo build --release --target wasm32-unknown-unknown
```
