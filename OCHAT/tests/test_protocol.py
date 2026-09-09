import socket

import pytest

from server.protocol import LineReader, ProtocolError, send_packet


def test_send_and_read_packet() -> None:
    left, right = socket.socketpair()
    try:
        send_packet(left, "ping", value="你好")
        packet = LineReader(right).read_packet()
        assert packet == {"action": "ping", "value": "你好"}
    finally:
        left.close()
        right.close()


def test_invalid_json_raises_protocol_error() -> None:
    left, right = socket.socketpair()
    try:
        left.sendall(b"{bad json}\n")
        with pytest.raises(ProtocolError):
            LineReader(right).read_packet()
    finally:
        left.close()
        right.close()

