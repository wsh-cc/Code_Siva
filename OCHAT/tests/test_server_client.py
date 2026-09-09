import socket
import threading
import time
from pathlib import Path

import pytest

from client.api import OchatClient
from server.app import ChatServer


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def start_test_server(tmp_path: Path) -> tuple[ChatServer, int]:
    port = free_port()
    server = ChatServer(
        host="127.0.0.1",
        port=port,
        db_path=tmp_path / "ochat.db",
        db_backend="sqlite",
        upload_dir=tmp_path / "uploads",
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    deadline = time.time() + 3
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                break
        except OSError:
            time.sleep(0.05)
    return server, port


def test_server_client_direct_and_group_flow(tmp_path: Path) -> None:
    server, port = start_test_server(tmp_path)
    alice = OchatClient(port=port)
    bob = OchatClient(port=port)
    try:
        alice.request("register", username="alice_tcp", password="secret1", nickname="Alice")
        bob.request("register", username="bob_tcp", password="secret2", nickname="Bob")

        alice_login = alice.request("login", username="alice_tcp", password="secret1")
        bob_login = bob.request("login", username="bob_tcp", password="secret2")
        bob_id = int(bob_login["user"]["id"])

        alice.request("friends.add", username="bob_tcp", remark="Bob")
        direct = alice.request("messages.direct.send", receiver_id=bob_id, content="hello over tcp")
        assert direct["message"]["content"] == "hello over tcp"

        group = alice.request("groups.create", name="TCP Test")["group"]
        alice.request("groups.invite", group_id=group["id"], username="bob_tcp")
        group_message = bob.request("messages.group.send", group_id=group["id"], content="group hello")
        assert group_message["message"]["conversation_type"] == "group"

        search = alice.request("messages.search", keyword="group hello")
        assert search["messages"][0]["content"] == "group hello"
        assert alice_login["user"]["username"] == "alice_tcp"
    finally:
        alice.close()
        bob.close()
        server.stop()


def test_login_requirements_and_auth_guard(tmp_path: Path) -> None:
    server, port = start_test_server(tmp_path)
    client = OchatClient(port=port)
    try:
        with pytest.raises(RuntimeError, match="username and password cannot be empty"):
            client.request("login", username="", password="")
        with pytest.raises(RuntimeError, match="please login first"):
            client.request("friends.list")
        with pytest.raises(RuntimeError, match="please login first"):
            client.request("messages.search", keyword="anything")

        client.request("register", username="login_req", password="secret1")
        with pytest.raises(RuntimeError, match="invalid username or password"):
            client.request("login", username="login_req", password="wrong")
        login = client.request("login", username="login_req", password="secret1")
        assert login["user"]["username"] == "login_req"
        client.request("logout")
        with pytest.raises(RuntimeError, match="please login first"):
            client.request("friends.list")
    finally:
        client.close()
        server.stop()


def test_file_upload_send_and_download(tmp_path: Path) -> None:
    server, port = start_test_server(tmp_path)
    alice = OchatClient(port=port)
    bob = OchatClient(port=port)
    source = tmp_path / "hello.txt"
    target = tmp_path / "downloaded.txt"
    source.write_text("hello file", encoding="utf-8")
    try:
        alice.request("register", username="alice_dl", password="secret1")
        bob.request("register", username="bob_dl", password="secret2")
        alice.request("login", username="alice_dl", password="secret1")
        bob_login = bob.request("login", username="bob_dl", password="secret2")
        alice.request("friends.add", username="bob_dl")

        upload = alice.upload_file(source)["file"]
        alice.request(
            "messages.direct.send",
            receiver_id=bob_login["user"]["id"],
            content="已发送 hello.txt",
            message_type="file",
            file_id=upload["id"],
        )
        downloaded = bob.download_file(upload["id"], target)

        assert downloaded["filename"] == "hello.txt"
        assert target.read_text(encoding="utf-8") == "hello file"
    finally:
        alice.close()
        bob.close()
        server.stop()


def test_message_and_file_guards(tmp_path: Path) -> None:
    server, port = start_test_server(tmp_path)
    alice = OchatClient(port=port)
    bob = OchatClient(port=port)
    evil = tmp_path / "bad.exe"
    evil.write_text("not allowed", encoding="utf-8")
    try:
        alice.request("register", username="alice_guard", password="secret1")
        bob.request("register", username="bob_guard", password="secret2")
        alice.request("login", username="alice_guard", password="secret1")
        bob_login = bob.request("login", username="bob_guard", password="secret2")
        alice.request("friends.add", username="bob_guard")

        with pytest.raises(RuntimeError, match="invalid message content"):
            alice.request("messages.direct.send", receiver_id=bob_login["user"]["id"], content="")
        with pytest.raises(RuntimeError, match="file type or size is not allowed"):
            alice.upload_file(evil)
        with pytest.raises(RuntimeError, match="invalid message content"):
            alice.request("messages.direct.send", receiver_id=bob_login["user"]["id"], content="fake file", message_type="file")
        with pytest.raises(RuntimeError, match="search keyword is too long"):
            alice.request("messages.search", keyword="x" * 100)
        with pytest.raises(RuntimeError, match="remark is too long"):
            alice.request("friends.add", username="bob_guard", remark="x" * 40)
    finally:
        alice.close()
        bob.close()
        server.stop()
