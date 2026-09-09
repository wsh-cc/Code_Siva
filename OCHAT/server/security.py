"""Validation and security helpers for OCHAT."""

from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets
from pathlib import Path


USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")
SAFE_FILENAME_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]+')
ALLOWED_FILE_SUFFIXES = {
    ".txt",
    ".md",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".zip",
}
ALLOWED_MESSAGE_TYPES = {"text", "file", "image"}
MAX_TEXT_MESSAGE_LENGTH = 2000
MAX_META_MESSAGE_LENGTH = 240
MAX_SEARCH_KEYWORD_LENGTH = 80


def validate_username(username: str) -> bool:
    return bool(USERNAME_RE.fullmatch(username or ""))


def validate_password(password: str) -> bool:
    return isinstance(password, str) and 6 <= len(password) <= 64


def validate_display_text(value: str, max_length: int) -> bool:
    return isinstance(value, str) and 0 <= len(value.strip()) <= max_length


def validate_message(message_type: str, content: str, file_id: object = None) -> bool:
    if message_type not in ALLOWED_MESSAGE_TYPES:
        return False
    if message_type == "text":
        return bool(content.strip()) and len(content) <= MAX_TEXT_MESSAGE_LENGTH and file_id in (None, "")
    return bool(content.strip()) and len(content) <= MAX_META_MESSAGE_LENGTH and file_id not in (None, "")


def validate_search_keyword(keyword: str) -> bool:
    return 0 < len(keyword.strip()) <= MAX_SEARCH_KEYWORD_LENGTH


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return f"pbkdf2_sha256$120000${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, rounds_text, salt_hex, digest_hex = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        rounds = int(rounds_text)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
    except (ValueError, TypeError):
        return False

    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, rounds)
    return hmac.compare_digest(actual, expected)


def create_token() -> str:
    return secrets.token_urlsafe(32)


def sanitize_filename(filename: str) -> str:
    name = Path(filename or "").name.strip().strip(".")
    cleaned = SAFE_FILENAME_RE.sub("_", name)
    return cleaned[:120] or "upload.bin"


def is_allowed_file(filename: str, size: int, max_size: int = 10 * 1024 * 1024) -> bool:
    suffix = Path(filename or "").suffix.lower()
    return 0 < int(size) <= max_size and suffix in ALLOWED_FILE_SUFFIXES
