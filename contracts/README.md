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

Python and .NET code validate against these files and never share internal classes as a contract.
