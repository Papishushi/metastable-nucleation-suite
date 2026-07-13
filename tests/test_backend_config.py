import copy
import json
from pathlib import Path

import pytest

from metastable_suite.backend_config import (
    BackendConfigurationError,
    build_backend_registry,
    validate_backend_configuration,
)
from metastable_suite.execution import BackendRegistry, ExecutionRequest
from metastable_suite.hardware_adapters import (
    SerialCommandBackend,
    TCPCommandBackend,
    VisaCommandBackend,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads(
    (ROOT / "schemas" / "backend-config.schema.json").read_text(
        encoding="utf-8"
    )
)
VALID_CONFIGURATION = {
    "schema_version": "1.0.0",
    "backends": [
        {
            "id": "lab-counter-tcp",
            "transport": "tcp",
            "host": "127.0.0.1",
            "port": 9000,
            "timeout_s": 0.5,
            "supported_specifications": ["E09"],
            "retry_policy": {
                "attempts": 1,
                "initial_delay_s": 0,
                "backoff": 1,
                "maximum_delay_s": 0,
            },
        }
    ],
}


def request(specification_id="E09", backend_id="lab-counter-tcp"):
    return ExecutionRequest(
        run_id="hardware-test",
        specification_id=specification_id,
        backend_id=backend_id,
        trial_count=1,
        parameters={},
    )


def test_valid_configuration_registers_lazy_tcp_backend():
    validate_backend_configuration(VALID_CONFIGURATION, SCHEMA)
    registry = build_backend_registry(VALID_CONFIGURATION)

    backend = registry.create(request())

    assert isinstance(backend, TCPCommandBackend)
    assert backend.backend_id == "lab-counter-tcp"
    assert backend.backend_kind == "hardware"
    assert backend.transport.host == "127.0.0.1"
    assert backend.transport.port == 9000


@pytest.mark.parametrize(
    ("definition", "expected_type", "transport_attribute", "expected_value"),
    [
        (
            {
                "id": "lab-counter-serial",
                "transport": "serial",
                "port": "/dev/ttyUSB0",
                "baudrate": 230400,
                "supported_specifications": ["E09"],
            },
            SerialCommandBackend,
            "port",
            "/dev/ttyUSB0",
        ),
        (
            {
                "id": "lab-counter-visa",
                "transport": "visa",
                "resource_name": "TCPIP0::192.0.2.10::INSTR",
                "supported_specifications": ["E09"],
            },
            VisaCommandBackend,
            "resource_name",
            "TCPIP0::192.0.2.10::INSTR",
        ),
    ],
)
def test_serial_and_visa_configurations_build_lazy_backends(
    definition,
    expected_type,
    transport_attribute,
    expected_value,
):
    document = {
        "schema_version": "1.0.0",
        "backends": [definition],
    }
    validate_backend_configuration(document, SCHEMA)
    registry = build_backend_registry(document)

    backend = registry.create(request(backend_id=definition["id"]))

    assert isinstance(backend, expected_type)
    assert backend.backend_kind == "hardware"
    assert getattr(backend.transport, transport_attribute) == expected_value


def test_duplicate_backend_ids_are_rejected():
    document = copy.deepcopy(VALID_CONFIGURATION)
    document["backends"].append(copy.deepcopy(document["backends"][0]))

    with pytest.raises(BackendConfigurationError, match="duplicate backend id"):
        validate_backend_configuration(document, SCHEMA)


def test_reserved_default_backend_id_is_rejected():
    document = copy.deepcopy(VALID_CONFIGURATION)
    document["backends"][0]["id"] = "reference-simulator"
    validate_backend_configuration(document, SCHEMA)

    with pytest.raises(
        BackendConfigurationError,
        match="cannot register configured backend",
    ):
        build_backend_registry(document, registry=BackendRegistry.default())


def test_unsupported_specification_is_rejected_before_connecting():
    validate_backend_configuration(VALID_CONFIGURATION, SCHEMA)
    registry = build_backend_registry(VALID_CONFIGURATION)

    with pytest.raises(
        BackendConfigurationError,
        match="does not support specification",
    ):
        registry.create(request(specification_id="E11"))


def test_unknown_or_incomplete_transport_configuration_is_rejected():
    document = copy.deepcopy(VALID_CONFIGURATION)
    document["backends"][0].pop("port")

    with pytest.raises(
        BackendConfigurationError,
        match="invalid backend configuration",
    ):
        validate_backend_configuration(document, SCHEMA)


def test_connection_secrets_cannot_be_embedded_as_unknown_fields():
    document = copy.deepcopy(VALID_CONFIGURATION)
    document["backends"][0]["password"] = "do-not-put-secrets-here"

    with pytest.raises(
        BackendConfigurationError,
        match="invalid backend configuration",
    ):
        validate_backend_configuration(document, SCHEMA)
