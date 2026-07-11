from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from .hardware import CommandBackend, TrialRequest, TrialResponse
from .transports import (
    JsonCommandTransport,
    SerialTransport,
    TCPTransport,
    TransportError,
    VisaTransport,
)


class TransportCommandBackend(CommandBackend):
    """Command backend backed by a JSON request/response transport."""

    backend_id = "transport-command"

    def __init__(
        self,
        transport: JsonCommandTransport,
        backend_id: str,
        firmware_version: str = "unknown",
    ) -> None:
        if not backend_id:
            raise ValueError("backend_id is required")
        super().__init__(firmware_version=firmware_version)
        self.transport = transport
        self.backend_id = backend_id

    def _exchange(self, command: str, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        return self.transport.exchange(command, payload)

    def execute_trial(self, request: TrialRequest) -> TrialResponse:
        try:
            return super().execute_trial(request)
        except TransportError as exc:
            return TrialResponse(
                timestamp_utc=datetime.now(timezone.utc).isoformat(),
                outcome={"transport_error": exc.__class__.__name__},
                diagnostics={
                    "transport_error_type": exc.__class__.__name__,
                    "transport_error_message": str(exc),
                },
                valid=False,
                exclusion_reasons=("transport_failure",),
            )

    def close(self) -> None:
        try:
            if self.specification_id is not None:
                self._exchange("close", {})
        finally:
            self.transport.disconnect()
            self.specification_id = None
            self.parameters = {}


class SerialCommandBackend(TransportCommandBackend):
    def __init__(
        self,
        port: str,
        baudrate: int = 115_200,
        timeout_s: float = 2.0,
        backend_id: str = "serial-device",
        firmware_version: str = "unknown",
        **transport_options: Any,
    ) -> None:
        super().__init__(
            SerialTransport(
                port=port,
                baudrate=baudrate,
                timeout_s=timeout_s,
                **transport_options,
            ),
            backend_id=backend_id,
            firmware_version=firmware_version,
        )


class TCPCommandBackend(TransportCommandBackend):
    def __init__(
        self,
        host: str,
        port: int,
        timeout_s: float = 2.0,
        backend_id: str = "tcp-device",
        firmware_version: str = "unknown",
        **transport_options: Any,
    ) -> None:
        super().__init__(
            TCPTransport(
                host=host,
                port=port,
                timeout_s=timeout_s,
                **transport_options,
            ),
            backend_id=backend_id,
            firmware_version=firmware_version,
        )


class VisaCommandBackend(TransportCommandBackend):
    def __init__(
        self,
        resource_name: str,
        timeout_s: float = 2.0,
        backend_id: str = "visa-device",
        firmware_version: str = "unknown",
        **transport_options: Any,
    ) -> None:
        super().__init__(
            VisaTransport(
                resource_name=resource_name,
                timeout_s=timeout_s,
                **transport_options,
            ),
            backend_id=backend_id,
            firmware_version=firmware_version,
        )
