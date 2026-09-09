"""JSON-lines protocol helpers used by the OCHAT client and server."""

from __future__ import annotations

import json
import socket
from typing import Any


# A 10 MB file becomes about 13.4 MB after base64 encoding, plus JSON overhead.
MAX_LINE_BYTES = 16 * 1024 * 1024


class ProtocolError(Exception):
    """Raised when a peer sends invalid protocol data."""


def send_packet(sock: socket.socket, action: str, **payload: Any) -> None:
    packet = {"action": action, **payload}
    encoded = json.dumps(packet, ensure_ascii=False).encode("utf-8") + b"\n"
    sock.sendall(encoded)


class LineReader:
    def __init__(self, sock: socket.socket) -> None:
        self.sock = sock
        self.buffer = bytearray()

    def read_packet(self) -> dict[str, Any] | None:
        while b"\n" not in self.buffer:
            chunk = self.sock.recv(4096)
            if not chunk:
                if self.buffer:
                    raise ProtocolError("connection closed during packet")
                return None
            self.buffer.extend(chunk)
            if len(self.buffer) > MAX_LINE_BYTES:
                raise ProtocolError("packet too large")

        line, _, rest = self.buffer.partition(b"\n")
        self.buffer = bytearray(rest)
        if not line.strip():
            return {}

        try:
            packet = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ProtocolError("invalid json packet") from exc
        if not isinstance(packet, dict):
            raise ProtocolError("packet must be a json object")
        return packet


def ok(**payload: Any) -> dict[str, Any]:
    return {"ok": True, **payload}


def fail(message: str, code: str = "ERROR", **payload: Any) -> dict[str, Any]:
    return {"ok": False, "code": code, "message": message, **payload}
