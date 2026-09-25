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


def test_direct_unread_count_is_cleared_when_conversation_is_read(tmp_path: Path) -> None:
    storage = ChatStorage(tmp_path / "ochat.db")
    alice = storage.create_user("alice_unread", "secret1")
    bob = storage.create_user("bob_unread", "secret2")
    storage.add_friend(alice["id"], "bob_unread")

    storage.save_direct_message(alice["id"], bob["id"], "one")
    storage.save_direct_message(alice["id"], bob["id"], "two")

    assert storage.direct_unread_count(bob["id"], alice["id"]) == 2
    assert storage.direct_unread_count(alice["id"], bob["id"]) == 0
    assert storage.mark_conversation_read(bob["id"], "direct", alice["id"]) == 2
    assert storage.direct_unread_count(bob["id"], alice["id"]) == 0


def test_group_unread_count_ignores_sender_and_clears_on_read(tmp_path: Path) -> None:
    storage = ChatStorage(tmp_path / "ochat.db")
    alice = storage.create_user("alice_group_unread", "secret1")
    bob = storage.create_user("bob_group_unread", "secret2")
    group = storage.create_group(alice["id"], "Unread Group")
    storage.invite_group_member(group["id"], alice["id"], "bob_group_unread")

    storage.save_group_message(alice["id"], group["id"], "group one")
    storage.save_group_message(alice["id"], group["id"], "group two")

    assert storage.group_unread_count(alice["id"], group["id"]) == 0
    assert storage.group_unread_count(bob["id"], group["id"]) == 2
    assert storage.mark_conversation_read(bob["id"], "group", group["id"]) == 2
    assert storage.group_unread_count(bob["id"], group["id"]) == 0


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


def test_friend_request_acceptance_creates_friendship(tmp_path: Path) -> None:
    storage = ChatStorage(tmp_path / "ochat.db")
    alice = storage.create_user("alice_req", "secret1")
    bob = storage.create_user("bob_req", "secret2")

    request = storage.create_friend_request(alice["id"], "bob_req", "我是 Alice")
    assert request["status"] == "pending"
    assert storage.list_friend_requests(bob["id"])["incoming"][0]["requester_username"] == "alice_req"
    assert not storage.are_friends(alice["id"], bob["id"])

    handled = storage.respond_friend_request(bob["id"], request["id"], True, remark="Alice")
    assert handled["status"] == "accepted"
    assert storage.are_friends(alice["id"], bob["id"])
    assert storage.are_friends(bob["id"], alice["id"])


def test_friend_request_rejection_does_not_create_friendship(tmp_path: Path) -> None:
    storage = ChatStorage(tmp_path / "ochat.db")
    alice = storage.create_user("alice_reject", "secret1")
    bob = storage.create_user("bob_reject", "secret2")

    request = storage.create_friend_request(alice["id"], "bob_reject")
    handled = storage.respond_friend_request(bob["id"], request["id"], False)

    assert handled["status"] == "rejected"
    assert not storage.are_friends(alice["id"], bob["id"])


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


def test_group_invitation_acceptance_adds_member(tmp_path: Path) -> None:
    storage = ChatStorage(tmp_path / "ochat.db")
    alice = storage.create_user("alice_invite", "secret1")
    bob = storage.create_user("bob_invite", "secret2")
    group = storage.create_group(alice["id"], "Invite Project")

    invitation = storage.create_group_invitation(group["id"], alice["id"], "bob_invite", "进群讨论")
    assert invitation["status"] == "pending"
    assert storage.list_group_invitations(bob["id"])["incoming"][0]["group_name"] == "Invite Project"
    with pytest.raises(PermissionError):
        storage.save_group_message(bob["id"], group["id"], "not yet")

    handled = storage.respond_group_invitation(bob["id"], invitation["id"], True)
    assert handled["status"] == "accepted"
    storage.save_group_message(bob["id"], group["id"], "now joined")


def test_group_invitation_rejection_does_not_add_member(tmp_path: Path) -> None:
    storage = ChatStorage(tmp_path / "ochat.db")
    alice = storage.create_user("alice_invite_reject", "secret1")
    bob = storage.create_user("bob_invite_reject", "secret2")
    group = storage.create_group(alice["id"], "Reject Project")

    invitation = storage.create_group_invitation(group["id"], alice["id"], "bob_invite_reject")
    handled = storage.respond_group_invitation(bob["id"], invitation["id"], False)

    assert handled["status"] == "rejected"
    with pytest.raises(PermissionError):
        storage.save_group_message(bob["id"], group["id"], "still outside")


def test_group_owner_can_manage_admins_and_admin_can_remove_members(tmp_path: Path) -> None:
    storage = ChatStorage(tmp_path / "ochat.db")
    owner = storage.create_user("owner_manage", "secret1")
    admin = storage.create_user("admin_manage", "secret2")
    member = storage.create_user("member_manage", "secret3")
    group = storage.create_group(owner["id"], "Managed Group")
    storage.invite_group_member(group["id"], owner["id"], "admin_manage")
    storage.invite_group_member(group["id"], owner["id"], "member_manage")

    with pytest.raises(PermissionError):
        storage.update_group_member_role(group["id"], member["id"], admin["id"], "admin")

    updated = storage.update_group_member_role(group["id"], owner["id"], admin["id"], "admin")
    assert updated["role"] == "admin"

    with pytest.raises(PermissionError):
        storage.remove_group_member(group["id"], admin["id"], owner["id"])
    storage.remove_group_member(group["id"], admin["id"], member["id"])

    members = storage.list_group_members(group["id"], owner["id"])
    assert {item["username"] for item in members} == {"owner_manage", "admin_manage"}


def test_group_alias_allows_self_update_and_group_remark_is_personal(tmp_path: Path) -> None:
    storage = ChatStorage(tmp_path / "ochat.db")
    owner = storage.create_user("owner_alias", "secret1")
    admin = storage.create_user("admin_alias", "secret2")
    member = storage.create_user("member_alias", "secret3")
    group = storage.create_group(owner["id"], "Alias Group")
    storage.invite_group_member(group["id"], owner["id"], "admin_alias")
    storage.invite_group_member(group["id"], owner["id"], "member_alias")
    storage.update_group_member_role(group["id"], owner["id"], admin["id"], "admin")

    updated_self = storage.update_group_member_alias(group["id"], member["id"], member["id"], "Me")
    assert updated_self["alias"] == "Me"

    with pytest.raises(PermissionError):
        storage.update_group_member_alias(group["id"], member["id"], owner["id"], "Teacher")

    updated_member = storage.update_group_member_alias(group["id"], admin["id"], member["id"], "Monitor")
    assert updated_member["alias"] == "Monitor"
    members = storage.list_group_members(group["id"], owner["id"])
    assert next(item for item in members if item["username"] == "member_alias")["alias"] == "Monitor"

    owner_group = storage.update_group_remark(group["id"], owner["id"], "Course project team")
    assert owner_group["group_remark"] == "Course project team"
    assert storage.get_group(group["id"], member["id"])["group_remark"] == ""
    assert storage.list_groups(owner["id"])[0]["group_remark"] == "Course project team"

    storage.save_group_message(member["id"], group["id"], "alias message")
    history = storage.list_group_history(owner["id"], group["id"])
    assert history[-1]["sender_group_alias"] == "Monitor"


def test_owner_leave_promotes_first_admin_by_assignment_order(tmp_path: Path) -> None:
    storage = ChatStorage(tmp_path / "ochat.db")
    owner = storage.create_user("owner_leave_admin", "secret1")
    first_joined = storage.create_user("first_joined_admin", "secret2")
    first_admin = storage.create_user("first_admin", "secret3")
    second_admin = storage.create_user("second_admin", "secret4")
    group = storage.create_group(owner["id"], "Admin Succession")
    storage.invite_group_member(group["id"], owner["id"], "first_joined_admin")
    storage.invite_group_member(group["id"], owner["id"], "first_admin")
    storage.invite_group_member(group["id"], owner["id"], "second_admin")
    storage.update_group_member_role(group["id"], owner["id"], first_admin["id"], "admin")
    storage.update_group_member_role(group["id"], owner["id"], second_admin["id"], "admin")

    storage.leave_group(group["id"], owner["id"])

    promoted_group = storage.get_group(group["id"], first_admin["id"])
    assert int(promoted_group["owner_id"]) == first_admin["id"]
    assert promoted_group["my_role"] == "owner"
    assert storage.get_group(group["id"], second_admin["id"])["my_role"] == "admin"
    with pytest.raises(PermissionError):
        storage.get_group(group["id"], owner["id"])


def test_owner_leave_promotes_first_joined_member_when_no_admin(tmp_path: Path) -> None:
    storage = ChatStorage(tmp_path / "ochat.db")
    owner = storage.create_user("owner_leave_member", "secret1")
    first = storage.create_user("first_member", "secret2")
    second = storage.create_user("second_member", "secret3")
    group = storage.create_group(owner["id"], "Member Succession")
    storage.invite_group_member(group["id"], owner["id"], "first_member")
    storage.invite_group_member(group["id"], owner["id"], "second_member")

    storage.leave_group(group["id"], owner["id"])

    promoted_group = storage.get_group(group["id"], first["id"])
    assert int(promoted_group["owner_id"]) == first["id"]
    assert promoted_group["my_role"] == "owner"
    assert storage.get_group(group["id"], second["id"])["my_role"] == "member"


def test_only_owner_can_dismiss_group(tmp_path: Path) -> None:
    storage = ChatStorage(tmp_path / "ochat.db")
    owner = storage.create_user("owner_dismiss", "secret1")
    member = storage.create_user("member_dismiss", "secret2")
    group = storage.create_group(owner["id"], "Dismiss Group")
    storage.invite_group_member(group["id"], owner["id"], "member_dismiss")

    with pytest.raises(PermissionError):
        storage.dismiss_group(group["id"], member["id"])

    storage.dismiss_group(group["id"], owner["id"])
    with pytest.raises(PermissionError):
        storage.get_group(group["id"], owner["id"])


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


def test_avatar_file_can_be_downloaded_by_other_users(tmp_path: Path) -> None:
    storage = ChatStorage(tmp_path / "ochat.db")
    alice = storage.create_user("alice_avatar", "secret1")
    bob = storage.create_user("bob_avatar", "secret2")
    avatar = storage.save_file(alice["id"], "avatar.png", "stored_avatar.png", 6, "image/png")
    private_file = storage.save_file(alice["id"], "private.png", "private_avatar.png", 6, "image/png")

    storage.update_profile(
        alice["id"],
        nickname="Alice Avatar",
        signature="",
        contact="",
        avatar=f"file:{avatar['id']}",
    )

    assert storage.get_file_for_user(bob["id"], avatar["id"])["id"] == avatar["id"]
    with pytest.raises(PermissionError):
        storage.get_file_for_user(bob["id"], private_file["id"])


def test_duplicate_user_is_rejected(tmp_path: Path) -> None:
    storage = ChatStorage(tmp_path / "ochat.db")
    storage.create_user("alice_4", "secret1")
    with pytest.raises(StorageError):
        storage.create_user("alice_4", "secret2")


def test_update_extended_profile_fields(tmp_path: Path) -> None:
    storage = ChatStorage(tmp_path / "ochat.db")
    user = storage.create_user("profile_user", "secret1", nickname="Old")

    updated = storage.update_profile(
        user["id"],
        nickname="New Name",
        signature="Keep moving",
        contact="profile@example.com",
        avatar="avatar.png",
        birthday="2001-02-03",
        gender="女",
        address="Shanghai",
        age=25,
    )

    assert updated["nickname"] == "New Name"
    assert updated["birthday"] == "2001-02-03"
    assert updated["gender"] == "女"
    assert updated["address"] == "Shanghai"
    assert updated["age"] == 25
