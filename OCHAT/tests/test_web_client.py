import json
import socket
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

from server.app import ChatServer
from web_client.server import WebClientServer


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_for_port(port: int) -> None:
    deadline = time.time() + 3
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                return
        except OSError:
            time.sleep(0.05)
    raise RuntimeError(f"port {port} did not open")


def post_json(
    base_url: str,
    action: str,
    payload: dict | None = None,
    cookie: str | None = None,
    web_session_id: str | None = None,
) -> tuple[dict, str]:
    data = json.dumps({"action": action, "payload": payload or {}}).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}/api/request",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    if cookie:
        request.add_header("Cookie", cookie)
    if web_session_id:
        request.add_header("X-OCHAT-Web-Session", web_session_id)
    with urllib.request.urlopen(request, timeout=5) as response:
        set_cookie = response.headers.get("Set-Cookie", "").split(";", 1)[0]
        return json.loads(response.read().decode("utf-8")), set_cookie or cookie or ""


def post_json_response(
    base_url: str,
    action: str,
    payload: dict | None = None,
    *,
    origin: str | None = None,
) -> tuple[int, dict]:
    data = json.dumps({"action": action, "payload": payload or {}}).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}/api/request",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    if origin:
        request.add_header("Origin", origin)
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def get_json(base_url: str, path: str) -> tuple[int, dict, dict[str, str]]:
    try:
        with urllib.request.urlopen(f"{base_url}{path}", timeout=5) as response:
            return response.status, json.loads(response.read().decode("utf-8")), dict(response.headers)
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8")), dict(exc.headers)


def test_bridge_state_returns_combined_web_client_snapshot(tmp_path: Path) -> None:
    chat_port = free_port()
    web_port = free_port()
    chat_server = ChatServer(
        host="127.0.0.1",
        port=chat_port,
        db_path=tmp_path / "ochat.db",
        db_backend="sqlite",
        upload_dir=tmp_path / "uploads",
    )
    web_server = WebClientServer(("127.0.0.1", web_port), "127.0.0.1", chat_port)
    threading.Thread(target=chat_server.serve_forever, daemon=True).start()
    threading.Thread(target=web_server.serve_forever, daemon=True).start()
    wait_for_port(chat_port)
    wait_for_port(web_port)

    try:
        base_url = f"http://127.0.0.1:{web_port}"
        register, cookie = post_json(base_url, "register", {"username": "web_state_user", "password": "secret1"})
        login, cookie = post_json(base_url, "login", {"username": "web_state_user", "password": "secret1"}, cookie)
        snapshot, _ = post_json(base_url, "bridge.state", cookie=cookie)

        assert register["ok"]
        assert login["ok"]
        assert snapshot["ok"]
        assert isinstance(snapshot["friends"], list)
        assert isinstance(snapshot["groups"], list)
        assert isinstance(snapshot["conversations"], list)
        assert isinstance(snapshot["requests"], dict)
    finally:
        web_server.shutdown()
        web_server.server_close()
        chat_server.stop()


def test_web_session_header_keeps_browser_tabs_independent(tmp_path: Path) -> None:
    chat_port = free_port()
    web_port = free_port()
    chat_server = ChatServer(
        host="127.0.0.1",
        port=chat_port,
        db_path=tmp_path / "ochat.db",
        db_backend="sqlite",
        upload_dir=tmp_path / "uploads",
    )
    web_server = WebClientServer(("127.0.0.1", web_port), "127.0.0.1", chat_port)
    threading.Thread(target=chat_server.serve_forever, daemon=True).start()
    threading.Thread(target=web_server.serve_forever, daemon=True).start()
    wait_for_port(chat_port)
    wait_for_port(web_port)

    try:
        base_url = f"http://127.0.0.1:{web_port}"
        tab_one = "tab-one"
        tab_two = "tab-two"

        _, shared_cookie = post_json(base_url, "register", {"username": "alice_web_tab", "password": "secret1"}, web_session_id=tab_one)
        post_json(base_url, "register", {"username": "bob_web_tab", "password": "secret2"}, shared_cookie, tab_two)

        alice_login, shared_cookie = post_json(
            base_url,
            "login",
            {"username": "alice_web_tab", "password": "secret1"},
            shared_cookie,
            tab_one,
        )
        bob_login, shared_cookie = post_json(
            base_url,
            "login",
            {"username": "bob_web_tab", "password": "secret2"},
            shared_cookie,
            tab_two,
        )
        alice_snapshot, _ = post_json(base_url, "bridge.state", cookie=shared_cookie, web_session_id=tab_one)
        bob_snapshot, _ = post_json(base_url, "bridge.state", cookie=shared_cookie, web_session_id=tab_two)
        alice_profile, _ = post_json(base_url, "profile.update", {"nickname": "Alice Tab"}, shared_cookie, tab_one)
        bob_profile, _ = post_json(base_url, "profile.update", {"nickname": "Bob Tab"}, shared_cookie, tab_two)

        assert alice_login["user"]["username"] == "alice_web_tab"
        assert bob_login["user"]["username"] == "bob_web_tab"
        assert alice_snapshot["ok"]
        assert bob_snapshot["ok"]
        assert alice_profile["user"]["username"] == "alice_web_tab"
        assert bob_profile["user"]["username"] == "bob_web_tab"
    finally:
        web_server.shutdown()
        web_server.server_close()
        chat_server.stop()


def test_web_health_and_readiness_endpoints(tmp_path: Path) -> None:
    chat_port = free_port()
    web_port = free_port()
    chat_server = ChatServer(
        host="127.0.0.1",
        port=chat_port,
        db_path=tmp_path / "ochat.db",
        db_backend="sqlite",
        upload_dir=tmp_path / "uploads",
    )
    web_server = WebClientServer(("127.0.0.1", web_port), "127.0.0.1", chat_port, production=True)
    threading.Thread(target=chat_server.serve_forever, daemon=True).start()
    threading.Thread(target=web_server.serve_forever, daemon=True).start()
    wait_for_port(chat_port)
    wait_for_port(web_port)

    try:
        base_url = f"http://127.0.0.1:{web_port}"
        health_status, health, headers = get_json(base_url, "/healthz")
        ready_status, ready, _ = get_json(base_url, "/readyz")

        assert health_status == 200
        assert health["ok"]
        assert health["production"]
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert ready_status == 200
        assert ready["ok"]
        assert ready["chat"]["service"] == "ochat-tcp"
    finally:
        web_server.shutdown()
        web_server.server_close()
        chat_server.stop()


def test_production_web_server_locks_bridge_configuration(tmp_path: Path) -> None:
    chat_port = free_port()
    web_port = free_port()
    chat_server = ChatServer(
        host="127.0.0.1",
        port=chat_port,
        db_path=tmp_path / "ochat.db",
        db_backend="sqlite",
        upload_dir=tmp_path / "uploads",
    )
    web_server = WebClientServer(
        ("127.0.0.1", web_port),
        "127.0.0.1",
        chat_port,
        production=True,
        allowed_origins={"https://chat.example.com"},
    )
    threading.Thread(target=chat_server.serve_forever, daemon=True).start()
    threading.Thread(target=web_server.serve_forever, daemon=True).start()
    wait_for_port(chat_port)
    wait_for_port(web_port)

    try:
        base_url = f"http://127.0.0.1:{web_port}"
        config, _ = post_json(base_url, "bridge.config")
        status, locked = post_json_response(
            base_url,
            "bridge.config.update",
            {"host": "127.0.0.1", "port": chat_port},
            origin="https://chat.example.com",
        )
        forbidden_status, forbidden = post_json_response(base_url, "bridge.config", origin="https://evil.example.com")

        assert config["locked"] is True
        assert status == 400
        assert not locked["ok"]
        assert "fixed in production" in locked["message"]
        assert forbidden_status == 403
        assert not forbidden["ok"]
    finally:
        web_server.shutdown()
        web_server.server_close()
        chat_server.stop()
