# Security Policy

## Supported versions

Security fixes are applied to:

- the current `main` branch;
- the latest stable release when a backport is practical.

Older releases may be documented as affected without receiving a patch. Scientific validity questions, incorrect models and ordinary bugs belong in normal issues unless they create a concrete security or safety impact.

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability involving remote execution, secrets, authentication, artifact integrity, dependency compromise, unsafe hardware control or disclosure of private data.

Report it privately to `danielmolinero111@cyberdude.com` with the subject `MNS security report`.

Include, where possible:

- affected commit, release, component or deployment mode;
- prerequisites and impact;
- minimal reproduction steps or proof of concept;
- whether hardware, credentials or network access are required;
- suggested mitigation;
- your preferred attribution or request for anonymity.

Do not send real secrets, personal data or destructive payloads. Use synthetic fixtures and redact tokens.

## Coordinated disclosure

The maintainer will validate the report, determine affected versions and coordinate a fix before public disclosure when the report is reproducible and security-relevant. Public credit is optional and requires the reporter's permission.

A report may be closed as non-security when it is a scientific disagreement, unsupported hypothetical risk, configuration question or bug without a security boundary impact. Such findings can still be moved into the normal issue workflow after sensitive details are removed.

## Security boundaries

MNS must fail closed around:

- remote device execution and deployment secrets;
- artifact hashes, attestations and provenance;
- deserialization and schema validation;
- local-only defaults and proxy forwarding assumptions;
- hardware commands, timeouts and invalid trials;
- third-party dependencies and release workflows.

CI success does not establish deployment security or laboratory safety. See `docs/07_seguridad_y_limites.md` and issue #36 for operational security work.