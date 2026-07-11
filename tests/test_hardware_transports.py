import json
import socket

import pytest

from metastable_suite.hardware import TrialRequest
from metastable_suite.hardware_adapters import TransportCommandBackend
from metastable_suite.transports import (
    RetryPolicy,
    SerialTransport,
    TCPTransport,
    TransportProtocolError,
    TransportTimeout,
    VisaTransport,
)


class FakeSocket:
    def __init__(self, responses=None, recv_error=None):
        self.responses = list(responses or [])
        self.recv_error = recv_error
        self.connected = False
        self.closed = False
        self.sent = []
        self.timeout = None

    def settimeout(self, value):
        self.timeout = value

    def connect(self, address):
        self.connected = True
        self.address = address

    def sendall(self, data):
        self.sent.append(data)

    def recv(self, size):
        if self.recv_error is not None:
            raise self.recv_error
        if not self.responses:
            return b""
        return self.responses.pop(0)

    def close(self):
        self.closed = True


def test_tcp_transport_reconnects_after_timeout():
    first = FakeSocket(recv_error=socket.timeout("slow"))
    second = FakeSocket(responses=[b'{"ok":true,"value":7}\n'])
    sockets = iter([first, second])
    transport = TCPTransport(
        "127.0.0.1",
        9000,
        retry_policy=RetryPolicy(attempts=2, initial_delay_s=0),
        socket_factory=lambda: next(sockets),
    )

    response = transport.exchange("ping", {"sequence": 1})

    assert response == {"ok": True, "value": 7}
    assert first.closed
    assert second.connected
    request = json.loads(second.sent[0].decode().strip())
    assert request == {"command": "ping", "payload": {"sequence": 1}}


def test_tcp_transport_rejects_malformed_response_without_retry():
    connection = FakeSocket(responses=[b"not-json\n"])
    transport = TCPTransport(
        "127.0.0.1",
        9000,
        retry_policy=RetryPolicy(attempts=3, initial_delay_s=0),
        socket_factory=lambda: connection,
    )

    with pytest.raises(TransportProtocolError, match="malformed JSON"):
        transport.exchange("ping", {})

    assert len(connection.sent) == 1


class FakeSerial:
    def __init__(self, response=b'{"ok":true}\n', partial_write=False):
        self.response = response
        self.partial_write = partial_write
        self.timeout = None
        self.write_timeout = None
        self.is_open = True
        self.closed = False
        self.writes = []

    def open(self):
        self.is_open = True

    def close(self):
        self.closed = True
        self.is_open = False

    def write(self, data):
        self.writes.append(data)
        return len(data) - 1 if self.partial_write else len(data)

    def flush(self):
        pass

    def readline(self):
        return self.response

    def reset_input_buffer(self):
        pass


def test_serial_transport_times_out_on_empty_response():
    serial = FakeSerial(response=b"")
    transport = SerialTransport(
        "COM1",
        retry_policy=RetryPolicy(attempts=1),
        serial_factory=lambda **kwargs: serial,
    )

    with pytest.raises(TransportTimeout, match="timed out"):
        transport.exchange("read", {})


def test_serial_transport_detects_partial_write():
    serial = FakeSerial(partial_write=True)
    transport = SerialTransport(
        "COM1",
        retry_policy=RetryPolicy(attempts=1),
        serial_factory=lambda **kwargs: serial,
    )

    with pytest.raises(Exception, match="partial write"):
        transport.exchange("read", {})


class FakeVisaResource:
    def __init__(self, response='{"ok":true,"measurement":1.25}\n'):
        self.response = response
        self.timeout = 0
        self.read_termination = ""
        self.write_termination = ""
        self.messages = []
        self.closed = False

    def write(self, message):
        self.messages.append(message)

    def read(self):
        return self.response

    def close(self):
        self.closed = True


class FakeVisaManager:
    def __init__(self, resource):
        self.resource = resource
        self.opened = []
        self.closed = False

    def open_resource(self, resource_name):
        self.opened.append(resource_name)
        return self.resource

    def close(self):
        self.closed = True


def test_visa_transport_configures_resource_and_closes_manager():
    resource = FakeVisaResource()
    manager = FakeVisaManager(resource)
    transport = VisaTransport(
        "TCPIP0::scope::INSTR",
        timeout_s=1.5,
        resource_manager_factory=lambda: manager,
    )

    response = transport.exchange("measure", {"channel": 1})
    transport.disconnect()

    assert response["measurement"] == 1.25
    assert resource.timeout == 1500
    assert resource.read_termination == "\n"
    assert resource.write_termination == "\n"
    assert resource.closed
    assert manager.closed


def test_transport_command_backend_normalizes_real_transport_lifecycle():
    responses = [
        b'{"ok":true}\n',
        b'{"ok":true,"offset":0.01}\n',
        b'{"reset_ok":true}\n',
        b'{"timestamp_utc":"2026-07-11T12:00:00Z","outcome":{"count":2},"valid":true}\n',
        b'{"laser_lock":true}\n',
        b'{"ok":true}\n',
    ]
    connection = FakeSocket(responses=responses)
    transport = TCPTransport("127.0.0.1", 9000, socket_factory=lambda: connection)
    backend = TransportCommandBackend(transport, backend_id="counter-a", firmware_version="1.2.3")

    backend.prepare("E09", {"gain": 2})
    assert backend.calibrate()["offset"] == 0.01
    assert backend.reset()["reset_ok"] is True
    result = backend.execute_trial(TrialRequest("run-1", "E09", 0))
    assert result.outcome == {"count": 2}
    assert backend.collect_diagnostics()["laser_lock"] is True
    backend.close()

    assert connection.closed
