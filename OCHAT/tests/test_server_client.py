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
        conversations = bob.request("conversations.list")["conversations"]
        group_chat = next(item for item in conversations if item["conversation_type"] == "group")
        assert group_chat["title"] == "TCP Test"
        assert group_chat["preview"] == "group hello"
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


def test_profile_update_includes_extended_fields(tmp_path: Path) -> None:
    server, port = start_test_server(tmp_path)
    client = OchatClient(port=port)
    try:
        client.request("register", username="profile_tcp", password="secret1")
        client.request("login", username="profile_tcp", password="secret1")

        updated = client.request(
            "profile.update",
            nickname="Profile User",
            signature="hello",
            contact="profile@example.com",
            avatar="avatar.png",
            birthday="2000-01-02",
            gender="男",
            address="Beijing",
            age=26,
        )["user"]

        assert updated["id"]
        assert updated["birthday"] == "2000-01-02"
        assert updated["gender"] == "男"
        assert updated["address"] == "Beijing"
        assert updated["age"] == 26

        with pytest.raises(RuntimeError, match="age must be between 0 and 150"):
            client.request("profile.update", nickname="Profile User", age=151)
    finally:
        client.close()
        server.stop()


def test_friend_request_flow_over_tcp(tmp_path: Path) -> None:
    server, port = start_test_server(tmp_path)
    alice = OchatClient(port=port)
    bob = OchatClient(port=port)
    try:
        alice.request("register", username="alice_req_tcp", password="secret1", nickname="Alice")
        bob.request("register", username="bob_req_tcp", password="secret2", nickname="Bob")
        alice_login = alice.request("login", username="alice_req_tcp", password="secret1")
        bob_login = bob.request("login", username="bob_req_tcp", password="secret2")

        request = alice.request("friends.request", username="bob_req_tcp", message="加个好友")["friend_request"]
        incoming = bob.request("friends.requests.list")["requests"]["friend_requests"]["incoming"]
        assert incoming[0]["id"] == request["id"]
        assert incoming[0]["requester_username"] == "alice_req_tcp"

        with pytest.raises(RuntimeError, match="receiver is not your friend"):
            alice.request("messages.direct.send", receiver_id=bob_login["user"]["id"], content="too early")

        bob.request("friends.requests.respond", friend_request_id=request["id"], accept=True, remark="Alice")
        friends = bob.request("friends.list")["friends"]
        assert friends[0]["username"] == "alice_req_tcp"
        sent = alice.request("messages.direct.send", receiver_id=bob_login["user"]["id"], content="now hello")
        assert sent["message"]["content"] == "now hello"
        assert alice_login["user"]["username"] == "alice_req_tcp"
    finally:
        alice.close()
        bob.close()
        server.stop()


def test_group_invitation_flow_over_tcp(tmp_path: Path) -> None:
    server, port = start_test_server(tmp_path)
    alice = OchatClient(port=port)
    bob = OchatClient(port=port)
    try:
        alice.request("register", username="alice_group_req_tcp", password="secret1")
        bob.request("register", username="bob_group_req_tcp", password="secret2")
        alice.request("login", username="alice_group_req_tcp", password="secret1")
        bob.request("login", username="bob_group_req_tcp", password="secret2")
        group = alice.request("groups.create", name="Need Approval")["group"]

        invitation = alice.request("groups.invite.request", group_id=group["id"], username="bob_group_req_tcp", message="来讨论")["invitation"]
        incoming = bob.request("groups.invitations.list")["requests"]["group_invitations"]["incoming"]
        assert incoming[0]["id"] == invitation["id"]
        assert incoming[0]["group_name"] == "Need Approval"

        with pytest.raises(RuntimeError, match="not a group member"):
            bob.request("messages.group.send", group_id=group["id"], content="too early")

        bob.request("groups.invitations.respond", invitation_id=invitation["id"], accept=True)
        groups = bob.request("groups.list")["groups"]
        assert groups[0]["name"] == "Need Approval"
        sent = bob.request("messages.group.send", group_id=group["id"], content="joined")
        assert sent["message"]["content"] == "joined"
    finally:
        alice.close()
        bob.close()
        server.stop()


def test_group_management_flow_over_tcp(tmp_path: Path) -> None:
    server, port = start_test_server(tmp_path)
    owner = OchatClient(port=port)
    admin = OchatClient(port=port)
    member = OchatClient(port=port)
    try:
        owner.request("register", username="owner_group_tcp", password="secret1")
        admin.request("register", username="admin_group_tcp", password="secret2")
        member.request("register", username="member_group_tcp", password="secret3")
        owner.request("login", username="owner_group_tcp", password="secret1")
        admin_login = admin.request("login", username="admin_group_tcp", password="secret2")
        member_login = member.request("login", username="member_group_tcp", password="secret3")

        group = owner.request("groups.create", name="Manage TCP")["group"]
        owner.request("groups.invite", group_id=group["id"], username="admin_group_tcp")
        owner.request("groups.invite", group_id=group["id"], username="member_group_tcp")
        owner.request("groups.member_role.update", group_id=group["id"], member_id=admin_login["user"]["id"], role="admin")

        with pytest.raises(RuntimeError, match="only owner can change group roles"):
            admin.request("groups.member_role.update", group_id=group["id"], member_id=member_login["user"]["id"], role="admin")

        admin.request("groups.remove_member", group_id=group["id"], member_id=member_login["user"]["id"])
        members = owner.request("groups.members", group_id=group["id"])["members"]
        assert {item["username"] for item in members} == {"owner_group_tcp", "admin_group_tcp"}

        owner.request("groups.leave", group_id=group["id"])
        admin_group = admin.request("groups.list")["groups"][0]
        assert admin_group["my_role"] == "owner"
        assert int(admin_group["owner_id"]) == int(admin_login["user"]["id"])

        admin.request("groups.dismiss", group_id=group["id"])
        assert admin.request("groups.list")["groups"] == []
    finally:
        owner.close()
        admin.close()
        member.close()
        server.stop()


def test_group_alias_and_remark_over_tcp(tmp_path: Path) -> None:
    server, port = start_test_server(tmp_path)
    owner = OchatClient(port=port)
    admin = OchatClient(port=port)
    member = OchatClient(port=port)
    try:
        owner.request("register", username="owner_alias_tcp", password="secret1")
        admin.request("register", username="admin_alias_tcp", password="secret2")
        member.request("register", username="member_alias_tcp", password="secret3")
        owner_login = owner.request("login", username="owner_alias_tcp", password="secret1")
        admin_login = admin.request("login", username="admin_alias_tcp", password="secret2")
        member_login = member.request("login", username="member_alias_tcp", password="secret3")

        group = owner.request("groups.create", name="Alias TCP")["group"]
        owner.request("groups.invite", group_id=group["id"], username="admin_alias_tcp")
        owner.request("groups.invite", group_id=group["id"], username="member_alias_tcp")
        owner.request("groups.member_role.update", group_id=group["id"], member_id=admin_login["user"]["id"], role="admin")

        self_alias = member.request("groups.member_alias.update", group_id=group["id"], member_id=member_login["user"]["id"], alias="Me")
        assert self_alias["member"]["alias"] == "Me"

        with pytest.raises(RuntimeError, match="only owner or admin can change other group nicknames"):
            member.request("groups.member_alias.update", group_id=group["id"], member_id=owner_login["user"]["id"], alias="Boss")

        admin.request("groups.member_alias.update", group_id=group["id"], member_id=member_login["user"]["id"], alias="Monitor")
        members = owner.request("groups.members", group_id=group["id"])["members"]
        assert next(item for item in members if item["username"] == "member_alias_tcp")["alias"] == "Monitor"
        sent = member.request("messages.group.send", group_id=group["id"], content="alias over tcp")
        assert sent["message"]["sender_group_alias"] == "Monitor"

        member.request("groups.remark.update", group_id=group["id"], group_remark="Study group")
        member_group = member.request("groups.list")["groups"][0]
        owner_group = owner.request("groups.list")["groups"][0]
        assert member_group["group_remark"] == "Study group"
        assert owner_group["group_remark"] == ""
    finally:
        owner.close()
        admin.close()
        member.close()
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


def test_unread_counts_update_over_tcp(tmp_path: Path) -> None:
    server, port = start_test_server(tmp_path)
    alice = OchatClient(port=port)
    bob = OchatClient(port=port)
    try:
        alice.request("register", username="alice_unread_tcp", password="secret1")
        bob.request("register", username="bob_unread_tcp", password="secret2")
        alice.request("login", username="alice_unread_tcp", password="secret1")
        bob_login = bob.request("login", username="bob_unread_tcp", password="secret2")
        alice.request("friends.add", username="bob_unread_tcp")

        alice.request("messages.direct.send", receiver_id=bob_login["user"]["id"], content="please read")
        conversations = bob.request("conversations.list")["conversations"]
        direct_chat = next(item for item in conversations if item["conversation_type"] == "direct")
        assert direct_chat["title"] == "alice_unread_tcp"
        assert direct_chat["preview"] == "please read"
        assert direct_chat["unread_count"] == 1

        friends = bob.request("friends.list")["friends"]
        alice_friend = next(friend for friend in friends if friend["username"] == "alice_unread_tcp")
        assert alice_friend["unread_count"] == 1

        bob.request("messages.direct.history", friend_id=alice_friend["id"])
        friends = bob.request("friends.list")["friends"]
        alice_friend = next(friend for friend in friends if friend["username"] == "alice_unread_tcp")
        assert alice_friend["unread_count"] == 0
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
