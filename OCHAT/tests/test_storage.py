from pathlib import Path

import pytest

from server.storage import ChatStorage, PermissionError, StorageError


def test_register_login_friend_and_direct_message(tmp_path: Path) -> None:
    storage = ChatStorage(tmp_path / "ochat.db")
    alice = storage.create_user("alice_1", "secret1", nickname="Alice")
    bob = storage.create_user("bob_1", "secret2", nickname="Bob")

    assert storage.authenticate("alice_1", "secret1")["id"] == alice["id"]
    assert storage.authenticate("alice_1", "wrong") is None

    friend = storage.add_friend(alice["id"], "bob_1", remark="Bobby", group_name="Classmates")
    assert friend["id"] == bob["id"]
    assert storage.are_friends(alice["id"], bob["id"])

    message = storage.save_direct_message(alice["id"], bob["id"], "hello")
    history = storage.list_direct_history(alice["id"], bob["id"])
    assert history[-1]["id"] == message["id"]
    assert history[-1]["content"] == "hello"

    recalled = storage.recall_message(alice["id"], message["id"])
    assert recalled["status"] == "recalled"


def test_remove_friend_is_bidirectional(tmp_path: Path) -> None:
    storage = ChatStorage(tmp_path / "ochat.db")
    alice = storage.create_user("alice_rm", "secret1")
    bob = storage.create_user("bob_rm", "secret2")
    storage.add_friend(alice["id"], "bob_rm")

    storage.remove_friend(alice["id"], bob["id"])

    assert not storage.are_friends(alice["id"], bob["id"])
    assert not storage.are_friends(bob["id"], alice["id"])


def test_direct_message_requires_friendship(tmp_path: Path) -> None:
    storage = ChatStorage(tmp_path / "ochat.db")
    alice = storage.create_user("alice_2", "secret1")
    bob = storage.create_user("bob_2", "secret2")

    with pytest.raises(PermissionError):
        storage.save_direct_message(alice["id"], bob["id"], "hello")


def test_groups_and_search(tmp_path: Path) -> None:
    storage = ChatStorage(tmp_path / "ochat.db")
    alice = storage.create_user("alice_3", "secret1")
    bob = storage.create_user("bob_3", "secret2")

    group = storage.create_group(alice["id"], "Project")
    storage.invite_group_member(group["id"], alice["id"], "bob_3")
    storage.save_group_message(alice["id"], group["id"], "milestone ready")

    members = storage.list_group_members(group["id"], bob["id"])
    assert {member["username"] for member in members} == {"alice_3", "bob_3"}

    results = storage.search_messages(bob["id"], "milestone")
    assert len(results) == 1
    assert results[0]["conversation_type"] == "group"


def test_file_download_permission(tmp_path: Path) -> None:
    storage = ChatStorage(tmp_path / "ochat.db")
    alice = storage.create_user("alice_file", "secret1")
    bob = storage.create_user("bob_file", "secret2")
    carol = storage.create_user("carol_file", "secret3")
    storage.add_friend(alice["id"], "bob_file")
    file_record = storage.save_file(alice["id"], "note.txt", "stored_note.txt", 5, "text/plain")
    storage.save_direct_message(alice["id"], bob["id"], "已发送 note.txt", "file", file_record["id"])

    assert storage.get_file_for_user(alice["id"], file_record["id"])["id"] == file_record["id"]
    assert storage.get_file_for_user(bob["id"], file_record["id"])["id"] == file_record["id"]
    with pytest.raises(PermissionError):
        storage.get_file_for_user(carol["id"], file_record["id"])


def test_duplicate_user_is_rejected(tmp_path: Path) -> None:
    storage = ChatStorage(tmp_path / "ochat.db")
    storage.create_user("alice_4", "secret1")
    with pytest.raises(StorageError):
        storage.create_user("alice_4", "secret2")
