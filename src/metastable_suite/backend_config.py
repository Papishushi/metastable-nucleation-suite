from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator

from .execution import BackendRegistry, ExecutionRequest
from .hardware import ExperimentalBackend
from .hardware_adapters import (
    SerialCommandBackend,
    TCPCommandBackend,
    VisaCommandBackend,
)
from .transports import RetryPolicy


class BackendConfigurationError(ValueError):
    """A hardware-backend configuration is invalid or internally inconsistent."""


def _read_json_object(path: str | Path, *, label: str) -> dict[str, Any]:
    source = Path(path)
    try:
        document = json.loads(source.read_text(encoding="utf-8"))
    except OSError as exc:
        raise BackendConfigurationError(
            f"cannot read {label} {source}: {exc}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise BackendConfigurationError(
            f"{label} {source} is not valid JSON: {exc}"
        ) from exc
    if not isinstance(document, dict):
        raise BackendConfigurationError(
            f"{label} {source} must contain a JSON object"
        )
    return document


def validate_backend_configuration(
    document: Mapping[str, Any],
    schema: Mapping[str, Any],
) -> None:
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    errors = sorted(
        validator.iter_errors(document),
        key=lambda error: tuple(
            str(component) for component in error.absolute_path
        ),
    )
    if errors:
        error = errors[0]
        location = (
            ".".join(str(component) for component in error.absolute_path)
            or "<root>"
        )
        raise BackendConfigurationError(
            f"invalid backend configuration at {location}: {error.message}"
        )

    identifiers: set[str] = set()
    for definition in document["backends"]:
        backend_id = definition["id"]
        if backend_id in identifiers:
            raise BackendConfigurationError(
                f"duplicate backend id {backend_id!r}"
            )
        identifiers.add(backend_id)


def _retry_policy(definition: Mapping[str, Any]) -> RetryPolicy:
    values = definition.get("retry_policy", {})
    return RetryPolicy(
        attempts=int(values.get("attempts", 3)),
        initial_delay_s=float(values.get("initial_delay_s", 0.05)),
        backoff=float(values.get("backoff", 2.0)),
        maximum_delay_s=float(values.get("maximum_delay_s", 1.0)),
    )


def _create_backend(
    definition: Mapping[str, Any],
    request: ExecutionRequest,
) -> ExperimentalBackend:
    backend_id = str(definition["id"])
    supported = frozenset(
        str(value) for value in definition["supported_specifications"]
    )
    if request.specification_id not in supported:
        raise BackendConfigurationError(
            f"backend {backend_id!r} does not support specification "
            f"{request.specification_id!r}"
        )

    common = {
        "backend_id": backend_id,
        "firmware_version": str(
            definition.get("firmware_version", "unknown")
        ),
        "timeout_s": float(definition.get("timeout_s", 2.0)),
        "retry_policy": _retry_policy(definition),
    }
    transport = definition["transport"]
    if transport == "tcp":
        return TCPCommandBackend(
            host=str(definition["host"]),
            port=int(definition["port"]),
            maximum_message_bytes=int(
                definition.get("maximum_message_bytes", 1_048_576)
            ),
            **common,
        )
    if transport == "serial":
        return SerialCommandBackend(
            port=str(definition["port"]),
            baudrate=int(definition.get("baudrate", 115_200)),
            **common,
        )
    if transport == "visa":
        return VisaCommandBackend(
            resource_name=str(definition["resource_name"]),
            **common,
        )
    raise BackendConfigurationError(f"unsupported transport {transport!r}")


def build_backend_registry(
    document: Mapping[str, Any],
    *,
    registry: BackendRegistry | None = None,
) -> BackendRegistry:
    target = registry or BackendRegistry.default()
    for definition in document["backends"]:
        backend_id = str(definition["id"])
        try:
            target.register(
                backend_id,
                lambda request, definition=definition: _create_backend(
                    definition,
                    request,
                ),
                backend_kind="hardware",
            )
        except ValueError as exc:
            raise BackendConfigurationError(
                f"cannot register configured backend {backend_id!r}: {exc}"
            ) from exc
    return target


def load_backend_registry(
    configuration_path: str | Path,
    schema_path: str | Path,
    *,
    registry: BackendRegistry | None = None,
) -> BackendRegistry:
    document = _read_json_object(
        configuration_path,
        label="backend configuration",
    )
    schema = _read_json_object(
        schema_path,
        label="backend configuration schema",
    )
    validate_backend_configuration(document, schema)
    return build_backend_registry(document, registry=registry)
