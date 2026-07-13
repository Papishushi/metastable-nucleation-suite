# Cross-language contracts

Contracts are implementation-independent and versioned by directory (`v1`, `v2`, ...).

Compatibility policy:

- additive optional fields are backward compatible within a major contract version;
- removing, renaming or changing the meaning/type of a field requires a new major directory;
- envelopes include `schema_version`, `request_id` and an RFC 3339 timestamp;
- JSON Schema is canonical for files and low-frequency HTTP messages;
- OpenAPI describes public HTTP APIs when they become externally consumed;
- Protobuf/gRPC is introduced only for measured high-frequency service traffic;
- RDF/JSON-LD remains canonical for semantics and provenance;
- Arrow/Parquet remains canonical for high-volume event datasets.

## Capability negotiation

Servers expose `GET /v1/capabilities` using `v1/server-capabilities.schema.json`.
Clients must gate every optional or remotely versioned operation against a stable capability identifier before invoking it.

- an absent capability is unsupported and must not be invoked;
- `active` capabilities may be used normally;
- `deprecated` capabilities remain callable during their compatibility window, but clients must warn and prefer `replacement` when provided;
- deprecated entries must declare `deprecated_since_version`;
- `sunset_at_utc` communicates a planned removal deadline when one is known;
- removal of an advertised capability is a compatibility event and requires the documented deprecation policy or a new API major version.

Python and .NET code validate against these files and never share internal classes as a contract.

## Visualization scenes

`v1/visualization-scene.schema.json` defines the derived, hash-linked scene consumed by the
Rust/WASM visualizer. It makes coordinate meaning and the measured, derived, inferred or
illustrative status of each layer explicit. JSON-LD/RDF and Arrow/Parquet remain the
canonical semantic and event sources; a visualization scene is never a replacement source
of scientific truth.
