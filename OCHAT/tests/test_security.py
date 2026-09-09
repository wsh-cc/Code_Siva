from server.protocol import MAX_LINE_BYTES
from server.security import (
    MAX_TEXT_MESSAGE_LENGTH,
    is_allowed_file,
    sanitize_filename,
    validate_message,
    validate_password,
    validate_search_keyword,
    validate_username,
)


def test_login_field_validation_helpers() -> None:
    assert validate_username("user_123")
    assert not validate_username("")
    assert not validate_username("ab")
    assert not validate_username("bad-name")
    assert validate_password("123456")
    assert not validate_password("")
    assert not validate_password("12345")


def test_message_validation_limits() -> None:
    assert validate_message("text", "hello")
    assert not validate_message("text", "")
    assert not validate_message("text", "x" * (MAX_TEXT_MESSAGE_LENGTH + 1))
    assert validate_message("file", "已发送 a.txt", 1)
    assert not validate_message("file", "已发送 a.txt")
    assert not validate_message("unknown", "hello")


def test_file_and_search_validation() -> None:
    assert sanitize_filename("../../危险?.txt") == "危险_.txt"
    assert is_allowed_file("note.txt", 10)
    assert not is_allowed_file("run.exe", 10)
    assert not is_allowed_file("empty.txt", 0)
    assert validate_search_keyword("hello")
    assert not validate_search_keyword("")
    assert not validate_search_keyword("x" * 100)


def test_protocol_limit_matches_file_payload_size() -> None:
    assert MAX_LINE_BYTES >= 16 * 1024 * 1024
