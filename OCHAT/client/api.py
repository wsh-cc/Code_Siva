"""Synchronous socket client used by the Tkinter UI and tests."""

from __future__ import annotations

import base64
import mimetypes
import socket
import threading
import uuid
from pathlib import Path
from queue import Empty, Full, Queue
from typing import Any, Callable

from server.protocol import LineReader, send_packet


class OchatClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 8765) -> None:
        self.host = host
        self.port = port
        self.sock: socket.socket | None = None
        self.reader: LineReader | None = None
        self.pending: dict[str, Queue[dict[str, Any]]] = {}
        self.pending_lock = threading.Lock()
        self.send_lock = threading.Lock()
        self.events: Queue[dict[str, Any]] = Queue()
        self._recv_thread: threading.Thread | None = None
        self._closed = threading.Event()

    def connect(self) -> None:
        self.sock = socket.create_connection((self.host, self.port), timeout=5)
        self.sock.settimeout(None)
        self.reader = LineReader(self.sock)
        self._closed.clear()
        self._recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._recv_thread.start()

    def close(self) -> None:
        self._closed.set()
        sock = self.sock
        self.sock = None
        self.reader = None
        if sock:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            sock.close()
        self._fail_pending("connection closed")

    def request(self, action: str, timeout: float = 8, **payload: Any) -> dict[str, Any]:
        if not self.sock:
            self.connect()
        assert self.sock is not None
        request_id = uuid.uuid4().hex
        response_queue: Queue[dict[str, Any]] = Queue(maxsize=1)
        with self.pending_lock:
            self.pending[request_id] = response_queue
        try:
            try:
                with self.send_lock:
                    send_packet(self.sock, action, request_id=request_id, **payload)
            except OSError as exc:
                self._fail_pending("connection lost")
                self.close()
                raise RuntimeError("connection lost") from exc
            try:
                response = response_queue.get(timeout=timeout)
            except Empty as exc:
                raise RuntimeError(f"request timed out: {action}") from exc
            if response.get("ok"):
                return response
            raise RuntimeError(response.get("message", "request failed"))
        finally:
            with self.pending_lock:
                self.pending.pop(request_id, None)

    def poll_event(self, callback: Callable[[dict[str, Any]], None], timeout: float = 0.05) -> None:
        try:
            event = self.events.get(timeout=timeout)
        except Empty:
            return
        callback(event)

    def upload_file(self, file_path: str | Path) -> dict[str, Any]:
        path = Path(file_path)
        mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        content_b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        return self.request("files.upload", filename=path.name, mime_type=mime_type, content_b64=content_b64)

    def download_file(self, file_id: int, save_path: str | Path) -> dict[str, Any]:
        response = self.request("files.download", file_id=file_id)
        file_record = response["file"]
        data = base64.b64decode(file_record["content_b64"].encode("ascii"), validate=True)
        Path(save_path).write_bytes(data)
        return file_record

    def _recv_loop(self) -> None:
        assert self.reader is not None
        try:
            while not self._closed.is_set():
                packet = self.reader.read_packet()
                if packet is None:
                    break
                action = packet.get("action")
                if action == "response":
                    request_id = str(packet.get("request_id", ""))
                    with self.pending_lock:
                        response_queue = self.pending.get(request_id)
                    if response_queue:
                        response_queue.put(packet)
                    else:
                        self.events.put(packet)
                else:
                    self.events.put(packet)
        except Exception as exc:
            if not self._closed.is_set():
                self._fail_pending("connection closed")
                self.events.put({"action": "connection.closed", "message": str(exc)})
        else:
            if not self._closed.is_set():
                self._fail_pending("connection closed")
                self.events.put({"action": "connection.closed", "message": "server closed the connection"})
        finally:
            self.sock = None
            self.reader = None

    def _fail_pending(self, message: str) -> None:
        with self.pending_lock:
            queues = list(self.pending.values())
            self.pending.clear()
        for response_queue in queues:
            try:
                response_queue.put_nowait({"ok": False, "message": message})
            except Full:
                pass
