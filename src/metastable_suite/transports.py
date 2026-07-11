from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
import socket
import time
from typing import Any, Callable, Mapping, Protocol


class TransportError(RuntimeError):
    """Base error for hardware communication failures."""


class TransportTimeout(TransportError):
    """The device did not answer within the configured timeout."""


class TransportConnectionError(TransportError):
    """The transport could not connect or lost its connection."""


class TransportProtocolError(TransportError):
    """The device returned a malformed or semantically invalid response."""


@dataclass(frozen=True)
class RetryPolicy:
    attempts: int = 3
    initial_delay_s: float = 0.05
    backoff: float = 2.0
    maximum_delay_s: float = 1.0

    def __post_init__(self) -> None:
        if self.attempts < 1:
            raise ValueError("attempts must be at least one")
        if self.initial_delay_s < 0 or self.maximum_delay_s < 0:
            raise ValueError("retry delays must be non-negative")
        if self.backoff < 1:
            raise ValueError("backoff must be at least one")


class JsonCommandTransport(ABC):
    """Request/response transport using one UTF-8 JSON document per message."""

    def __init__(self, retry_policy: RetryPolicy | None = None) -> None:
        self.retry_policy = retry_policy or RetryPolicy()

    @abstractmethod
    def connect(self) -> None:
        """Open the underlying connection."""

    @abstractmethod
    def disconnect(self) -> None:
        """Close the underlying connection."""

    @abstractmethod
    def _round_trip(self, payload: bytes) -> bytes:
        """Send one encoded request and return one encoded response."""

    def reconnect(self) -> None:
        self.disconnect()
        self.connect()

    def exchange(self, command: str, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        request = json.dumps(
            {"command": command, "payload": dict(payload)},
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        delay = self.retry_policy.initial_delay_s
        last_error: TransportError | None = None

        for attempt in range(self.retry_policy.attempts):
            try:
                raw_response = self._round_trip(request)
                response = json.loads(raw_response.decode("utf-8"))
                if not isinstance(response, dict):
                    raise TransportProtocolError("device response must be a JSON object")
                if response.get("error"):
                    raise TransportProtocolError(str(response["error"]))
                return response
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise TransportProtocolError(f"device returned malformed JSON: {exc}") from exc
            except TransportProtocolError:
                raise
            except (TransportTimeout, TransportConnectionError) as exc:
                last_error = exc
                if attempt + 1 >= self.retry_policy.attempts:
                    break
                try:
                    self.reconnect()
                except TransportError as reconnect_error:
                    last_error = reconnect_error
                if delay:
                    time.sleep(delay)
                delay = min(delay * self.retry_policy.backoff, self.retry_policy.maximum_delay_s)

        assert last_error is not None
        try:
            self.disconnect()
        except Exception:
            # Preserve the terminal transport error even if closing the failed handle also fails.
            pass
        raise last_error


class SocketLike(Protocol):
    def settimeout(self, value: float | None) -> None: ...
    def connect(self, address: tuple[str, int]) -> None: ...
    def sendall(self, data: bytes) -> None: ...
    def recv(self, size: int) -> bytes: ...
    def close(self) -> None: ...


class TCPTransport(JsonCommandTransport):
    backend_id = "tcp-json"

    def __init__(
        self,
        host: str,
        port: int,
        timeout_s: float = 2.0,
        retry_policy: RetryPolicy | None = None,
        socket_factory: Callable[[], SocketLike] | None = None,
        maximum_message_bytes: int = 1_048_576,
    ) -> None:
        super().__init__(retry_policy)
        if not host:
            raise ValueError("host is required")
        if not 1 <= port <= 65535:
            raise ValueError("port must lie in [1, 65535]")
        if timeout_s <= 0:
            raise ValueError("timeout_s must be positive")
        self.host = host
        self.port = port
        self.timeout_s = timeout_s
        self.maximum_message_bytes = maximum_message_bytes
        self._socket_factory = socket_factory or (lambda: socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        self._socket: SocketLike | None = None

    def connect(self) -> None:
        self.disconnect()
        connection = self._socket_factory()
        connection.settimeout(self.timeout_s)
        try:
            connection.connect((self.host, self.port))
        except socket.timeout as exc:
            connection.close()
            raise TransportTimeout(f"TCP connection to {self.host}:{self.port} timed out") from exc
        except OSError as exc:
            connection.close()
            raise TransportConnectionError(f"TCP connection to {self.host}:{self.port} failed: {exc}") from exc
        self._socket = connection

    def disconnect(self) -> None:
        if self._socket is not None:
            try:
                self._socket.close()
            finally:
                self._socket = None

    def _round_trip(self, payload: bytes) -> bytes:
        if self._socket is None:
            self.connect()
        assert self._socket is not None
        try:
            self._socket.sendall(payload + b"\n")
            response = bytearray()
            while True:
                chunk = self._socket.recv(4096)
                if not chunk:
                    raise TransportConnectionError("TCP peer closed before completing a response")
                response.extend(chunk)
                if len(response) > self.maximum_message_bytes:
                    raise TransportProtocolError("TCP response exceeds maximum_message_bytes")
                newline = response.find(b"\n")
                if newline >= 0:
                    return bytes(response[:newline])
        except socket.timeout as exc:
            raise TransportTimeout("TCP device response timed out") from exc
        except TransportError:
            raise
        except OSError as exc:
            raise TransportConnectionError(f"TCP exchange failed: {exc}") from exc


class SerialLike(Protocol):
    timeout: float | None
    write_timeout: float | None
    is_open: bool

    def open(self) -> None: ...
    def close(self) -> None: ...
    def write(self, data: bytes) -> int: ...
    def flush(self) -> None: ...
    def readline(self) -> bytes: ...
    def reset_input_buffer(self) -> None: ...


class SerialTransport(JsonCommandTransport):
    backend_id = "serial-json"

    def __init__(
        self,
        port: str,
        baudrate: int = 115_200,
        timeout_s: float = 2.0,
        retry_policy: RetryPolicy | None = None,
        serial_factory: Callable[..., SerialLike] | None = None,
    ) -> None:
        super().__init__(retry_policy)
        if not port:
            raise ValueError("port is required")
        if baudrate <= 0 or timeout_s <= 0:
            raise ValueError("baudrate and timeout_s must be positive")
        self.port = port
        self.baudrate = baudrate
        self.timeout_s = timeout_s
        self._serial_factory = serial_factory
        self._serial: SerialLike | None = None

    def _create_serial(self) -> SerialLike:
        if self._serial_factory is not None:
            return self._serial_factory(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout_s,
                write_timeout=self.timeout_s,
            )
        try:
            import serial
        except ImportError as exc:
            raise TransportConnectionError(
                "SerialTransport requires the optional dependency `pyserial`; install `.[hardware]`"
            ) from exc
        return serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            timeout=self.timeout_s,
            write_timeout=self.timeout_s,
        )

    def connect(self) -> None:
        self.disconnect()
        try:
            connection = self._create_serial()
            if not connection.is_open:
                connection.open()
            connection.reset_input_buffer()
        except TransportError:
            raise
        except Exception as exc:
            raise TransportConnectionError(f"serial connection to {self.port} failed: {exc}") from exc
        self._serial = connection

    def disconnect(self) -> None:
        if self._serial is not None:
            try:
                if self._serial.is_open:
                    self._serial.close()
            finally:
                self._serial = None

    def _round_trip(self, payload: bytes) -> bytes:
        if self._serial is None:
            self.connect()
        assert self._serial is not None
        try:
            written = self._serial.write(payload + b"\n")
            if written != len(payload) + 1:
                raise TransportConnectionError("serial transport performed a partial write")
            self._serial.flush()
            response = self._serial.readline()
            if not response:
                raise TransportTimeout("serial device response timed out")
            return response.rstrip(b"\r\n")
        except TransportError:
            raise
        except Exception as exc:
            raise TransportConnectionError(f"serial exchange failed: {exc}") from exc


class VisaResourceLike(Protocol):
    timeout: int
    read_termination: str
    write_termination: str

    def write(self, message: str) -> Any: ...
    def read(self) -> str: ...
    def close(self) -> None: ...


class VisaManagerLike(Protocol):
    def open_resource(self, resource_name: str) -> VisaResourceLike: ...
    def close(self) -> None: ...


class VisaTransport(JsonCommandTransport):
    backend_id = "visa-json"

    def __init__(
        self,
        resource_name: str,
        timeout_s: float = 2.0,
        retry_policy: RetryPolicy | None = None,
        resource_manager_factory: Callable[[], VisaManagerLike] | None = None,
    ) -> None:
        super().__init__(retry_policy)
        if not resource_name:
            raise ValueError("resource_name is required")
        if timeout_s <= 0:
            raise ValueError("timeout_s must be positive")
        self.resource_name = resource_name
        self.timeout_s = timeout_s
        self._resource_manager_factory = resource_manager_factory
        self._manager: VisaManagerLike | None = None
        self._resource: VisaResourceLike | None = None

    def _create_manager(self) -> VisaManagerLike:
        if self._resource_manager_factory is not None:
            return self._resource_manager_factory()
        try:
            import pyvisa
        except ImportError as exc:
            raise TransportConnectionError(
                "VisaTransport requires the optional dependency `pyvisa`; install `.[hardware]`"
            ) from exc
        return pyvisa.ResourceManager()

    def connect(self) -> None:
        self.disconnect()
        try:
            manager = self._create_manager()
            resource = manager.open_resource(self.resource_name)
            resource.timeout = int(self.timeout_s * 1000)
            resource.read_termination = "\n"
            resource.write_termination = "\n"
        except TransportError:
            raise
        except Exception as exc:
            raise TransportConnectionError(f"VISA connection to {self.resource_name} failed: {exc}") from exc
        self._manager = manager
        self._resource = resource

    def disconnect(self) -> None:
        resource, manager = self._resource, self._manager
        self._resource = None
        self._manager = None
        if resource is not None:
            try:
                resource.close()
            except Exception:
                pass
        if manager is not None:
            try:
                manager.close()
            except Exception:
                pass

    def _round_trip(self, payload: bytes) -> bytes:
        if self._resource is None:
            self.connect()
        assert self._resource is not None
        try:
            self._resource.write(payload.decode("utf-8"))
            response = self._resource.read()
            if not response:
                raise TransportTimeout("VISA device returned an empty response")
            return response.rstrip("\r\n").encode("utf-8")
        except TransportError:
            raise
        except Exception as exc:
            name = exc.__class__.__name__.lower()
            if "timeout" in name:
                raise TransportTimeout(f"VISA device response timed out: {exc}") from exc
            raise TransportConnectionError(f"VISA exchange failed: {exc}") from exc
