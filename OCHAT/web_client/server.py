"""Local HTTP bridge for the browser-based OCHAT client."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import secrets
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from client.api import OchatClient
from server.network import endpoint_hints, resolve_bind_host


STATIC_ROOT = Path(__file__).resolve().parent / "static"
DEFAULT_WEB_HOST = "127.0.0.1"
DEFAULT_WEB_PORT = 8080
DEFAULT_CHAT_HOST = "127.0.0.1"
DEFAULT_CHAT_PORT = 8765
DEFAULT_MAX_BODY_BYTES = 18 * 1024 * 1024


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str) -> list[str]:
    value = os.getenv(name, "")
    return [item.strip() for item in value.split(",") if item.strip()]


class BrowserSession:
    def __init__(self, chat_host: str, chat_port: int) -> None:
        self.chat_host = chat_host
        self.chat_port = chat_port
        self.client = OchatClient(chat_host, chat_port)
        self.lock = threading.Lock()

    def request(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self.lock:
            return self.client.request(action, **payload)

    def config(self) -> dict[str, Any]:
        return {"ok": True, "host": self.chat_host, "port": self.chat_port}

    def configure(self, chat_host: str, chat_port: int) -> dict[str, Any]:
        host = str(chat_host or "").strip()
        port = int(chat_port)
        if not host:
            raise ValueError("server host cannot be empty")
        if not 1 <= port <= 65535:
            raise ValueError("server port must be between 1 and 65535")
        with self.lock:
            self.client.close()
            self.chat_host = host
            self.chat_port = port
            self.client = OchatClient(host, port)
        return self.config()

    def state_snapshot(self) -> dict[str, Any]:
        with self.lock:
            friends = self.client.request("friends.list")
            groups = self.client.request("groups.list")
            conversations = self.client.request("conversations.list")
            requests = self.client.request("friends.requests.list")
        return {
            "ok": True,
            "friends": friends.get("friends", []),
            "groups": groups.get("groups", []),
            "conversations": conversations.get("conversations", []),
            "requests": requests.get("requests", {}),
        }

    def poll_event(self, timeout: float = 20.0) -> dict[str, Any] | None:
        event: dict[str, Any] | None = None

        def capture(payload: dict[str, Any]) -> None:
            nonlocal event
            event = payload

        self.client.poll_event(capture, timeout=timeout)
        return event

    def close(self) -> None:
        self.client.close()


class WebClientServer(ThreadingHTTPServer):
    def __init__(
        self,
        address: tuple[str, int],
        chat_host: str,
        chat_port: int,
        *,
        production: bool = False,
        allowed_origins: set[str] | None = None,
        secure_cookies: bool = False,
        max_body_bytes: int = DEFAULT_MAX_BODY_BYTES,
    ) -> None:
        super().__init__(address, WebClientHandler)
        self.chat_host = chat_host
        self.chat_port = chat_port
        self.production = production
        self.allowed_origins = allowed_origins or set()
        self.secure_cookies = secure_cookies
        self.max_body_bytes = max_body_bytes
        self.sessions: dict[str, BrowserSession] = {}
        self.sessions_lock = threading.Lock()

    def session(self, session_id: str | None) -> tuple[str, BrowserSession, bool]:
        created = False
        if not session_id:
            session_id = secrets.token_urlsafe(24)
            created = True
        with self.sessions_lock:
            session = self.sessions.get(session_id)
            if session is None:
                session = BrowserSession(self.chat_host, self.chat_port)
                self.sessions[session_id] = session
                created = True
        return session_id, session, created


class WebClientHandler(BaseHTTPRequestHandler):
    server: WebClientServer

    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/healthz":
            self.write_json({"ok": True, "service": "ochat-web", "production": self.server.production})
            return
        if parsed.path == "/readyz":
            self.handle_ready()
            return
        if parsed.path == "/api/events":
            self.handle_events()
            return
        if parsed.path == "/":
            self.serve_static("index.html")
            return
        if parsed.path.startswith("/static/"):
            self.serve_static(parsed.path.removeprefix("/static/"))
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if not self.request_origin_allowed():
            self.write_json({"ok": False, "message": "request origin is not allowed"}, status=HTTPStatus.FORBIDDEN)
            return
        if parsed.path == "/api/request":
            self.handle_request()
            return
        if parsed.path == "/api/logout":
            self.handle_logout()
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def handle_request(self) -> None:
        session_id, session, created = self.current_session()
        try:
            body = self.read_json()
            action = str(body.get("action", ""))
            payload = body.get("payload", {})
            if not isinstance(payload, dict):
                raise ValueError("payload must be an object")
            if action == "bridge.config":
                response = {**session.config(), "locked": self.server.production}
            elif action == "bridge.config.update":
                if self.server.production:
                    raise PermissionError("server connection is fixed in production mode")
                response = session.configure(str(payload.get("host", "")), int(payload.get("port", 0)))
            elif action == "bridge.state":
                response = session.state_snapshot()
            else:
                response = session.request(action, payload)
            self.write_json(response, session_id=session_id if created else None)
        except Exception as exc:
            self.write_json({"ok": False, "message": str(exc)}, status=HTTPStatus.BAD_REQUEST, session_id=session_id if created else None)

    def handle_ready(self) -> None:
        client = OchatClient(self.server.chat_host, self.server.chat_port)
        try:
            response = client.request("health", timeout=2)
            self.write_json({"ok": True, "service": "ochat-web", "chat": response})
        except Exception as exc:
            self.write_json({"ok": False, "service": "ochat-web", "message": str(exc)}, status=HTTPStatus.SERVICE_UNAVAILABLE)
        finally:
            client.close()

    def handle_events(self) -> None:
        query = parse_qs(urlparse(self.path).query)
        timeout = float(query.get("timeout", ["20"])[0])
        session_id, session, created = self.current_session()
        try:
            event = session.poll_event(timeout=max(1.0, min(timeout, 30.0)))
            self.write_json({"ok": True, "event": event}, session_id=session_id if created else None)
        except Exception as exc:
            self.write_json({"ok": False, "message": str(exc)}, status=HTTPStatus.BAD_REQUEST, session_id=session_id if created else None)

    def handle_logout(self) -> None:
        session_id = self.request_session_id()
        if session_id:
            with self.server.sessions_lock:
                session = self.server.sessions.pop(session_id, None)
            if session:
                try:
                    session.request("logout", {})
                except Exception:
                    pass
                session.close()
        self.write_json({"ok": True}, clear_session=True)

    def serve_static(self, relative_path: str) -> None:
        target = (STATIC_ROOT / relative_path).resolve()
        if STATIC_ROOT.resolve() not in [target, *target.parents] or not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content = target.read_bytes()
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_security_headers()
        self.send_header("Content-Type", f"{content_type}; charset=utf-8" if content_type.startswith("text/") else content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def current_session(self) -> tuple[str, BrowserSession, bool]:
        return self.server.session(self.request_session_id())

    def request_session_id(self) -> str | None:
        header_value = str(self.headers.get("X-OCHAT-Web-Session", "")).strip()
        if header_value and len(header_value) <= 128 and all(char.isalnum() or char in "-_" for char in header_value):
            return header_value
        return self.cookie_session_id()

    def cookie_session_id(self) -> str | None:
        cookie = self.headers.get("Cookie", "")
        for part in cookie.split(";"):
            name, _, value = part.strip().partition("=")
            if name == "ochat_web_session" and value:
                return value
        return None

    def read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        if length > self.server.max_body_bytes:
            raise ValueError("request body too large")
        data = self.rfile.read(length)
        return json.loads(data.decode("utf-8"))

    def request_origin_allowed(self) -> bool:
        if not self.server.allowed_origins:
            return True
        origin = str(self.headers.get("Origin", "")).strip()
        return not origin or origin in self.server.allowed_origins

    def write_json(
        self,
        payload: dict[str, Any],
        *,
        status: HTTPStatus = HTTPStatus.OK,
        session_id: str | None = None,
        clear_session: bool = False,
    ) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_security_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        if session_id:
            self.send_header("Set-Cookie", self.session_cookie(session_id))
        if clear_session:
            self.send_header("Set-Cookie", self.session_cookie("", clear=True))
        self.end_headers()
        self.wfile.write(data)

    def send_security_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Permissions-Policy", "geolocation=(), microphone=(), camera=()")

    def session_cookie(self, value: str, *, clear: bool = False) -> str:
        parts = [f"ochat_web_session={value}", "Path=/", "SameSite=Lax", "HttpOnly"]
        if clear:
            parts.append("Max-Age=0")
        if self.server.secure_cookies:
            parts.append("Secure")
        return "; ".join(parts)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the browser-based OCHAT client.")
    parser.add_argument("--host", default=os.getenv("OCHAT_WEB_HOST"), help="HTTP host for the web client")
    parser.add_argument("--lan", action="store_true", default=env_bool("OCHAT_WEB_LAN"), help="listen on all network interfaces for LAN browsers")
    parser.add_argument("--port", default=int(os.getenv("OCHAT_WEB_PORT", str(DEFAULT_WEB_PORT))), type=int, help="HTTP port for the web client")
    parser.add_argument("--chat-host", default=os.getenv("OCHAT_CHAT_HOST", DEFAULT_CHAT_HOST), help="OCHAT TCP server host")
    parser.add_argument("--chat-port", default=int(os.getenv("OCHAT_CHAT_PORT", str(DEFAULT_CHAT_PORT))), type=int, help="OCHAT TCP server port")
    parser.add_argument("--production", action="store_true", default=env_bool("OCHAT_PRODUCTION"), help="lock down browser-facing behavior for deployment")
    parser.add_argument("--allowed-origin", action="append", default=env_list("OCHAT_ALLOWED_ORIGINS"), help="allowed browser Origin for POST requests; can be repeated")
    parser.add_argument("--secure-cookies", action="store_true", default=env_bool("OCHAT_SECURE_COOKIES"), help="add Secure to browser session cookies")
    parser.add_argument("--max-body-mb", default=int(os.getenv("OCHAT_MAX_BODY_MB", "18")), type=int, help="maximum JSON request body size in MiB")
    return parser


def print_access_hints(host: str, port: int) -> None:
    hints = endpoint_hints(host, port, scheme="http")
    print(f"OCHAT Web client local URL: {hints['local'][0]}", flush=True)
    if hints["lan"]:
        print("OCHAT Web client LAN URLs for other browsers:", flush=True)
        for endpoint in hints["lan"]:
            print(f"  {endpoint}", flush=True)
    elif host == "0.0.0.0":
        print("LAN mode is enabled, but no non-loopback IPv4 address was detected.", flush=True)


def main() -> None:
    args = build_arg_parser().parse_args()
    host = resolve_bind_host(args.host, args.lan, DEFAULT_WEB_HOST)
    server = WebClientServer(
        (host, args.port),
        args.chat_host,
        args.chat_port,
        production=args.production,
        allowed_origins=set(args.allowed_origin),
        secure_cookies=args.secure_cookies,
        max_body_bytes=max(1, args.max_body_mb) * 1024 * 1024,
    )
    print(f"OCHAT Web client listening on {host}:{args.port}", flush=True)
    print_access_hints(host, args.port)
    print(f"Proxying OCHAT server: {args.chat_host}:{args.chat_port}", flush=True)
    if args.production:
        print("Production mode: browser-side server reconfiguration is disabled.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        with server.sessions_lock:
            sessions = list(server.sessions.values())
            server.sessions.clear()
        for session in sessions:
            session.close()
        server.server_close()


if __name__ == "__main__":
    main()
