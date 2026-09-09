"""Database persistence layer for the OCHAT server.

The course project is intended to use MySQL in normal runs. A SQLite backend is
kept for automated tests and for machines that only need a quick local demo.
"""

from __future__ import annotations

import os
import re
import sqlite3
import threading
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

from .security import hash_password, verify_password


class StorageError(Exception):
    pass


class NotFoundError(StorageError):
    pass


class PermissionError(StorageError):
    pass


MYSQL_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9_]+$")


class ChatStorage:
    def __init__(
        self,
        db_path: str | Path | None = None,
        *,
        backend: str | None = None,
        mysql_config: dict[str, Any] | None = None,
    ) -> None:
        self.backend = (backend or ("sqlite" if db_path else os.getenv("OCHAT_DB_BACKEND", "mysql"))).lower()
        self.db_path = Path(db_path) if db_path else Path("database") / "ochat.db"
        self.mysql_config = {
            "host": os.getenv("OCHAT_DB_HOST", "127.0.0.1"),
            "port": int(os.getenv("OCHAT_DB_PORT", "3306")),
            "user": os.getenv("OCHAT_DB_USER", "root"),
            "password": os.getenv("OCHAT_DB_PASSWORD", ""),
            "database": os.getenv("OCHAT_DB_NAME", "ochat"),
        }
        if mysql_config:
            self.mysql_config.update(mysql_config)
        self._lock = threading.RLock()
        self._connect()
        self.init_schema()

    @classmethod
    def sqlite(cls, db_path: str | Path) -> "ChatStorage":
        return cls(db_path=db_path, backend="sqlite")

    @classmethod
    def mysql(cls, **mysql_config: Any) -> "ChatStorage":
        return cls(backend="mysql", mysql_config=mysql_config)

    def _connect(self) -> None:
        if self.backend == "sqlite":
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA foreign_keys = ON")
            self.conn.execute("PRAGMA journal_mode = WAL")
            return

        if self.backend == "mysql":
            try:
                import pymysql
                from pymysql.cursors import DictCursor
            except ImportError as exc:
                raise RuntimeError(
                    "MySQL backend requires PyMySQL. Install it with: python -m pip install pymysql"
                ) from exc

            database = str(self.mysql_config["database"])
            if not MYSQL_IDENTIFIER_RE.fullmatch(database):
                raise ValueError("MySQL database name may only contain letters, numbers and underscores")

            server_conn = pymysql.connect(
                host=self.mysql_config["host"],
                port=int(self.mysql_config["port"]),
                user=self.mysql_config["user"],
                password=self.mysql_config["password"],
                charset="utf8mb4",
                cursorclass=DictCursor,
                autocommit=True,
                connect_timeout=5,
            )
            try:
                with server_conn.cursor() as cursor:
                    cursor.execute(
                        f"CREATE DATABASE IF NOT EXISTS `{database}` "
                        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                    )
            finally:
                server_conn.close()

            self.conn = pymysql.connect(
                host=self.mysql_config["host"],
                port=int(self.mysql_config["port"]),
                user=self.mysql_config["user"],
                password=self.mysql_config["password"],
                database=database,
                charset="utf8mb4",
                cursorclass=DictCursor,
                autocommit=False,
                connect_timeout=5,
            )
            return

        raise ValueError("backend must be 'mysql' or 'sqlite'")

    def close(self) -> None:
        with self._lock:
            self.conn.close()

    def init_schema(self) -> None:
        schema_file = "schema_mysql.sql" if self.backend == "mysql" else "schema_sqlite.sql"
        schema_path = Path(__file__).resolve().parent.parent / "database" / schema_file
        script = schema_path.read_text(encoding="utf-8")
        with self._lock:
            if self.backend == "sqlite":
                self.conn.executescript(script)
            else:
                for statement in self._split_sql(script):
                    cursor = self.conn.cursor()
                    try:
                        cursor.execute(statement)
                    finally:
                        cursor.close()
            self.conn.commit()

    def _split_sql(self, script: str) -> Iterable[str]:
        for statement in script.split(";"):
            statement = statement.strip()
            if statement:
                yield statement

    def _sql(self, sql: str) -> str:
        if self.backend == "mysql":
            return sql.replace("?", "%s")
        return sql

    def _cursor(self):
        if self.backend == "mysql":
            self.conn.ping(reconnect=True)
        return self.conn.cursor()

    def _fetchone(self, sql: str, params: tuple[Any, ...] = ()) -> Any | None:
        with self._lock:
            cursor = self._cursor()
            try:
                cursor.execute(self._sql(sql), params)
                row = cursor.fetchone()
                return self._row_dict(row) if row else None
            finally:
                cursor.close()

    def _fetchall(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with self._lock:
            cursor = self._cursor()
            try:
                cursor.execute(self._sql(sql), params)
                return [self._row_dict(row) for row in cursor.fetchall()]
            finally:
                cursor.close()

    def _execute(self, sql: str, params: tuple[Any, ...] = ()):
        cursor = self._cursor()
        try:
            cursor.execute(self._sql(sql), params)
            return cursor
        except Exception:
            cursor.close()
            raise

    def _insert_ignore_friendship_sql(self) -> str:
        if self.backend == "mysql":
            return """
                INSERT IGNORE INTO friendships(user_id, friend_id, remark, group_name)
                VALUES (?, ?, ?, ?)
            """
        return """
            INSERT OR IGNORE INTO friendships(user_id, friend_id, remark, group_name)
            VALUES (?, ?, ?, ?)
        """

    def create_user(
        self,
        username: str,
        password: str,
        nickname: str = "",
        signature: str = "",
        contact: str = "",
        avatar: str = "",
    ) -> dict[str, Any]:
        with self._lock:
            cursor = None
            try:
                cursor = self._execute(
                    """
                    INSERT INTO users(username, password_hash, nickname, signature, contact, avatar)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (username, hash_password(password), nickname or username, signature, contact, avatar),
                )
                user_id = int(cursor.lastrowid)
                self.conn.commit()
            except Exception as exc:
                self.conn.rollback()
                if self._is_integrity_error(exc):
                    raise StorageError("username already exists") from exc
                raise
            finally:
                if cursor:
                    cursor.close()
        return self.get_user_by_id(user_id)

    def authenticate(self, username: str, password: str) -> dict[str, Any] | None:
        row = self._fetchone("SELECT * FROM users WHERE username = ?", (username,))
        if row and verify_password(password, row["password_hash"]):
            return self._public_user(row)
        return None

    def get_user_by_id(self, user_id: int) -> dict[str, Any]:
        row = self._fetchone("SELECT * FROM users WHERE id = ?", (user_id,))
        if row is None:
            raise NotFoundError("user not found")
        return self._public_user(row)

    def find_users(self, keyword: str, limit: int = 20) -> list[dict[str, Any]]:
        like = f"%{keyword.strip()}%"
        rows = self._fetchall(
            """
            SELECT * FROM users
            WHERE username LIKE ? OR nickname LIKE ?
            ORDER BY username
            LIMIT ?
            """,
            (like, like, limit),
        )
        return [self._public_user(row) for row in rows]

    def update_profile(
        self,
        user_id: int,
        nickname: str,
        signature: str,
        contact: str,
        avatar: str,
    ) -> dict[str, Any]:
        with self._lock:
            cursor = self._execute(
                """
                UPDATE users
                SET nickname = ?, signature = ?, contact = ?, avatar = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (nickname, signature, contact, avatar, user_id),
            )
            cursor.close()
            self.conn.commit()
        return self.get_user_by_id(user_id)

    def add_friend(self, user_id: int, friend_username: str, remark: str = "", group_name: str = "Friends") -> dict[str, Any]:
        friend_row = self._fetchone("SELECT id FROM users WHERE username = ?", (friend_username,))
        if friend_row is None:
            raise NotFoundError("friend user not found")
        friend_id = int(friend_row["id"])
        if friend_id == user_id:
            raise StorageError("cannot add yourself")

        with self._lock:
            first = second = None
            try:
                first = self._execute(
                    """
                    INSERT INTO friendships(user_id, friend_id, remark, group_name)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_id, friend_id, remark, group_name),
                )
                second = self._execute(
                    self._insert_ignore_friendship_sql(),
                    (friend_id, user_id, "", "Friends"),
                )
                self.conn.commit()
            except Exception as exc:
                self.conn.rollback()
                if self._is_integrity_error(exc):
                    raise StorageError("friendship already exists") from exc
                raise
            finally:
                if first:
                    first.close()
                if second:
                    second.close()
        return self.get_friend(user_id, friend_id)

    def get_friend(self, user_id: int, friend_id: int) -> dict[str, Any]:
        row = self._fetchone(
            """
            SELECT u.id, u.username, u.nickname, u.signature, u.contact, u.avatar,
                   f.remark, f.group_name, f.created_at
            FROM friendships f
            JOIN users u ON u.id = f.friend_id
            WHERE f.user_id = ? AND f.friend_id = ?
            """,
            (user_id, friend_id),
        )
        if row is None:
            raise NotFoundError("friendship not found")
        return row

    def list_friends(self, user_id: int) -> list[dict[str, Any]]:
        return self._fetchall(
            """
            SELECT u.id, u.username, u.nickname, u.signature, u.contact, u.avatar,
                   f.remark, f.group_name, f.created_at
            FROM friendships f
            JOIN users u ON u.id = f.friend_id
            WHERE f.user_id = ?
            ORDER BY f.group_name, COALESCE(NULLIF(f.remark, ''), u.nickname), u.username
            """,
            (user_id,),
        )

    def update_friend(self, user_id: int, friend_id: int, remark: str, group_name: str) -> dict[str, Any]:
        with self._lock:
            cursor = self._execute(
                """
                UPDATE friendships
                SET remark = ?, group_name = ?
                WHERE user_id = ? AND friend_id = ?
                """,
                (remark, group_name, user_id, friend_id),
            )
            rowcount = cursor.rowcount
            cursor.close()
            self.conn.commit()
        if rowcount == 0:
            raise NotFoundError("friendship not found")
        return self.get_friend(user_id, friend_id)

    def remove_friend(self, user_id: int, friend_id: int) -> None:
        with self._lock:
            first = second = None
            try:
                first = self._execute(
                    "DELETE FROM friendships WHERE user_id = ? AND friend_id = ?",
                    (user_id, friend_id),
                )
                rowcount = first.rowcount
                second = self._execute(
                    "DELETE FROM friendships WHERE user_id = ? AND friend_id = ?",
                    (friend_id, user_id),
                )
                self.conn.commit()
            except Exception:
                self.conn.rollback()
                raise
            finally:
                if first:
                    first.close()
                if second:
                    second.close()
        if rowcount == 0:
            raise NotFoundError("friendship not found")

    def are_friends(self, user_a: int, user_b: int) -> bool:
        row = self._fetchone(
            "SELECT 1 AS ok FROM friendships WHERE user_id = ? AND friend_id = ?",
            (user_a, user_b),
        )
        return row is not None

    def create_group(self, owner_id: int, name: str) -> dict[str, Any]:
        with self._lock:
            group_cursor = member_cursor = None
            try:
                group_cursor = self._execute(
                    "INSERT INTO chat_groups(name, owner_id) VALUES (?, ?)",
                    (name, owner_id),
                )
                group_id = int(group_cursor.lastrowid)
                member_cursor = self._execute(
                    "INSERT INTO group_members(group_id, user_id, role, alias) VALUES (?, ?, 'owner', '')",
                    (group_id, owner_id),
                )
                self.conn.commit()
            except Exception:
                self.conn.rollback()
                raise
            finally:
                if group_cursor:
                    group_cursor.close()
                if member_cursor:
                    member_cursor.close()
        return self.get_group(group_id, owner_id)

    def invite_group_member(self, group_id: int, operator_id: int, username: str) -> dict[str, Any]:
        group = self.get_group(group_id, operator_id)
        role = group["my_role"]
        if role not in {"owner", "admin"}:
            raise PermissionError("only owner or admin can invite members")
        user_row = self._fetchone("SELECT id FROM users WHERE username = ?", (username,))
        if user_row is None:
            raise NotFoundError("user not found")
        member_id = int(user_row["id"])
        with self._lock:
            cursor = self._execute(
                self._insert_ignore_group_member_sql(),
                (group_id, member_id),
            )
            cursor.close()
            self.conn.commit()
        return self.get_group(group_id, operator_id)

    def _insert_ignore_group_member_sql(self) -> str:
        if self.backend == "mysql":
            return "INSERT IGNORE INTO group_members(group_id, user_id, role, alias) VALUES (?, ?, 'member', '')"
        return "INSERT OR IGNORE INTO group_members(group_id, user_id, role, alias) VALUES (?, ?, 'member', '')"

    def remove_group_member(self, group_id: int, operator_id: int, member_id: int) -> None:
        group = self.get_group(group_id, operator_id)
        if group["owner_id"] == member_id:
            raise PermissionError("owner cannot be removed")
        if operator_id != group["owner_id"] and operator_id != member_id:
            raise PermissionError("no permission to remove group member")
        with self._lock:
            cursor = self._execute(
                "DELETE FROM group_members WHERE group_id = ? AND user_id = ?",
                (group_id, member_id),
            )
            rowcount = cursor.rowcount
            cursor.close()
            self.conn.commit()
        if rowcount == 0:
            raise NotFoundError("group member not found")

    def list_groups(self, user_id: int) -> list[dict[str, Any]]:
        return self._fetchall(
            """
            SELECT g.id, g.name, g.owner_id, gm.role AS my_role, g.created_at
            FROM group_members gm
            JOIN chat_groups g ON g.id = gm.group_id
            WHERE gm.user_id = ?
            ORDER BY g.created_at DESC
            """,
            (user_id,),
        )

    def get_group(self, group_id: int, user_id: int) -> dict[str, Any]:
        row = self._fetchone(
            """
            SELECT g.id, g.name, g.owner_id, gm.role AS my_role, g.created_at
            FROM chat_groups g
            JOIN group_members gm ON gm.group_id = g.id
            WHERE g.id = ? AND gm.user_id = ?
            """,
            (group_id, user_id),
        )
        if row is None:
            raise PermissionError("not a group member")
        return row

    def list_group_members(self, group_id: int, user_id: int) -> list[dict[str, Any]]:
        self.get_group(group_id, user_id)
        return self._fetchall(
            """
            SELECT u.id, u.username, u.nickname, u.avatar, gm.role, gm.alias, gm.joined_at
            FROM group_members gm
            JOIN users u ON u.id = gm.user_id
            WHERE gm.group_id = ?
            ORDER BY CASE gm.role WHEN 'owner' THEN 0 WHEN 'admin' THEN 1 ELSE 2 END, u.username
            """,
            (group_id,),
        )

    def group_member_ids(self, group_id: int) -> list[int]:
        rows = self._fetchall(
            "SELECT user_id FROM group_members WHERE group_id = ?",
            (group_id,),
        )
        return [int(row["user_id"]) for row in rows]

    def save_direct_message(
        self,
        sender_id: int,
        receiver_id: int,
        content: str,
        message_type: str = "text",
        file_id: int | None = None,
    ) -> dict[str, Any]:
        if not self.are_friends(sender_id, receiver_id):
            raise PermissionError("receiver is not your friend")
        self._ensure_sender_owns_file(sender_id, file_id)
        return self._save_message(sender_id, "direct", receiver_id, content, message_type, file_id)

    def save_group_message(
        self,
        sender_id: int,
        group_id: int,
        content: str,
        message_type: str = "text",
        file_id: int | None = None,
    ) -> dict[str, Any]:
        self.get_group(group_id, sender_id)
        self._ensure_sender_owns_file(sender_id, file_id)
        return self._save_message(sender_id, "group", group_id, content, message_type, file_id)

    def _save_message(
        self,
        sender_id: int,
        conversation_type: str,
        target_id: int,
        content: str,
        message_type: str,
        file_id: int | None,
    ) -> dict[str, Any]:
        with self._lock:
            cursor = self._execute(
                """
                INSERT INTO messages(sender_id, conversation_type, target_id, message_type, content, file_id, status)
                VALUES (?, ?, ?, ?, ?, ?, 'sent')
                """,
                (sender_id, conversation_type, target_id, message_type, content, file_id),
            )
            message_id = int(cursor.lastrowid)
            cursor.close()
            self.conn.commit()
        return self.get_message(message_id)

    def get_message(self, message_id: int) -> dict[str, Any]:
        row = self._fetchone(
            """
            SELECT m.*, u.username AS sender_username, u.nickname AS sender_nickname,
                   f.original_name AS file_name, f.size AS file_size, f.storage_name
            FROM messages m
            JOIN users u ON u.id = m.sender_id
            LEFT JOIN files f ON f.id = m.file_id
            WHERE m.id = ?
            """,
            (message_id,),
        )
        if row is None:
            raise NotFoundError("message not found")
        return row

    def list_direct_history(self, user_id: int, friend_id: int, limit: int = 100) -> list[dict[str, Any]]:
        if not self.are_friends(user_id, friend_id):
            raise PermissionError("not friends")
        return list(
            reversed(
                self._fetchall(
                    """
                    SELECT m.*, u.username AS sender_username, u.nickname AS sender_nickname,
                           f.original_name AS file_name, f.size AS file_size, f.storage_name
                    FROM messages m
                    JOIN users u ON u.id = m.sender_id
                    LEFT JOIN files f ON f.id = m.file_id
                    WHERE m.conversation_type = 'direct'
                      AND ((m.sender_id = ? AND m.target_id = ?) OR (m.sender_id = ? AND m.target_id = ?))
                    ORDER BY m.created_at DESC, m.id DESC
                    LIMIT ?
                    """,
                    (user_id, friend_id, friend_id, user_id, limit),
                )
            )
        )

    def list_group_history(self, user_id: int, group_id: int, limit: int = 100) -> list[dict[str, Any]]:
        self.get_group(group_id, user_id)
        return list(
            reversed(
                self._fetchall(
                    """
                    SELECT m.*, u.username AS sender_username, u.nickname AS sender_nickname,
                           f.original_name AS file_name, f.size AS file_size, f.storage_name
                    FROM messages m
                    JOIN users u ON u.id = m.sender_id
                    LEFT JOIN files f ON f.id = m.file_id
                    WHERE m.conversation_type = 'group' AND m.target_id = ?
                    ORDER BY m.created_at DESC, m.id DESC
                    LIMIT ?
                    """,
                    (group_id, limit),
                )
            )
        )

    def search_messages(self, user_id: int, keyword: str, limit: int = 100) -> list[dict[str, Any]]:
        like = f"%{keyword.strip()}%"
        return self._fetchall(
            """
            SELECT DISTINCT m.*, u.username AS sender_username, u.nickname AS sender_nickname,
                   f.original_name AS file_name, f.size AS file_size, f.storage_name
            FROM messages m
            JOIN users u ON u.id = m.sender_id
            LEFT JOIN files f ON f.id = m.file_id
            LEFT JOIN group_members gm ON gm.group_id = m.target_id AND m.conversation_type = 'group'
            WHERE m.content LIKE ?
              AND (
                    (m.conversation_type = 'direct' AND (m.sender_id = ? OR m.target_id = ?))
                    OR
                    (m.conversation_type = 'group' AND gm.user_id = ?)
                  )
            ORDER BY m.created_at DESC, m.id DESC
            LIMIT ?
            """,
            (like, user_id, user_id, user_id, limit),
        )

    def recall_message(self, user_id: int, message_id: int) -> dict[str, Any]:
        row = self._fetchone("SELECT * FROM messages WHERE id = ?", (message_id,))
        if row is None:
            raise NotFoundError("message not found")
        if int(row["sender_id"]) != user_id:
            raise PermissionError("only sender can recall message")
        with self._lock:
            cursor = self._execute(
                """
                UPDATE messages
                SET status = 'recalled', content = '[message recalled]'
                WHERE id = ?
                """,
                (message_id,),
            )
            cursor.close()
            self.conn.commit()
        return self.get_message(message_id)

    def save_file(
        self,
        uploader_id: int,
        original_name: str,
        storage_name: str,
        size: int,
        mime_type: str,
    ) -> dict[str, Any]:
        with self._lock:
            cursor = self._execute(
                """
                INSERT INTO files(uploader_id, original_name, storage_name, size, mime_type)
                VALUES (?, ?, ?, ?, ?)
                """,
                (uploader_id, original_name, storage_name, size, mime_type),
            )
            file_id = int(cursor.lastrowid)
            cursor.close()
            self.conn.commit()
        row = self._fetchone("SELECT * FROM files WHERE id = ?", (file_id,))
        assert row is not None
        return row

    def get_file_for_user(self, user_id: int, file_id: int) -> dict[str, Any]:
        row = self._fetchone("SELECT * FROM files WHERE id = ?", (file_id,))
        if row is None:
            raise NotFoundError("file not found")
        if int(row["uploader_id"]) == user_id:
            return row
        direct_message = self._fetchone(
            """
            SELECT 1 AS ok
            FROM messages
            WHERE file_id = ?
              AND conversation_type = 'direct'
              AND (sender_id = ? OR target_id = ?)
            LIMIT 1
            """,
            (file_id, user_id, user_id),
        )
        if direct_message:
            return row
        group_message = self._fetchone(
            """
            SELECT 1 AS ok
            FROM messages m
            JOIN group_members gm ON gm.group_id = m.target_id
            WHERE m.file_id = ?
              AND m.conversation_type = 'group'
              AND gm.user_id = ?
            LIMIT 1
            """,
            (file_id, user_id),
        )
        if group_message:
            return row
        raise PermissionError("no permission to download this file")

    def _ensure_sender_owns_file(self, sender_id: int, file_id: int | None) -> None:
        if file_id in (None, ""):
            return
        row = self._fetchone("SELECT uploader_id FROM files WHERE id = ?", (int(file_id),))
        if row is None:
            raise NotFoundError("file not found")
        if int(row["uploader_id"]) != sender_id:
            raise PermissionError("cannot send a file uploaded by another user")

    def _is_integrity_error(self, exc: Exception) -> bool:
        if isinstance(exc, sqlite3.IntegrityError):
            return True
        return exc.__class__.__name__ == "IntegrityError"

    @staticmethod
    def _row_dict(row: Any) -> dict[str, Any]:
        data = dict(row)
        for key, value in list(data.items()):
            if isinstance(value, (datetime, date)):
                data[key] = value.strftime("%Y-%m-%d %H:%M:%S") if isinstance(value, datetime) else value.isoformat()
        return data

    @staticmethod
    def _public_user(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": row["id"],
            "username": row["username"],
            "nickname": row["nickname"],
            "signature": row["signature"],
            "contact": row["contact"],
            "avatar": row["avatar"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
