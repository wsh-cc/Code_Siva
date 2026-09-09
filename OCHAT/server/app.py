"""Threaded TCP server for OCHAT."""

from __future__ import annotations

import argparse
import base64
import logging
import socket
import sys
import threading
import traceback
import uuid
from pathlib import Path
from typing import Any

from .protocol import LineReader, ProtocolError, fail, ok, send_packet
from .security import (
    create_token,
    is_allowed_file,
    sanitize_filename,
    validate_display_text,
    validate_message,
    validate_password,
    validate_search_keyword,
    validate_username,
)
from .storage import ChatStorage, NotFoundError, PermissionError, StorageError


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765

LOGGER = logging.getLogger("ochat.server")


class ClientSession:
    def __init__(self, sock: socket.socket, address: tuple[str, int], server: "ChatServer") -> None:
        self.sock = sock
        self.address = address
        self.server = server
        self.user: dict[str, Any] | None = None
        self.token: str | None = None
        self.lock = threading.Lock()

    @property
    def user_id(self) -> int | None:
        return int(self.user["id"]) if self.user else None

    def send(self, action: str, **payload: Any) -> None:
        with self.lock:
            send_packet(self.sock, action, **payload)

    def require_user(self) -> dict[str, Any]:
        if not self.user:
            raise PermissionError("please login first")
        return self.user


class ChatServer:
    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        db_path: str | Path = "database/ochat.db",
        db_backend: str = "mysql",
        mysql_config: dict[str, Any] | None = None,
        upload_dir: str | Path = "database/uploads",
    ) -> None:
        self.host = host
        self.port = port
        self.storage = ChatStorage(db_path if db_backend == "sqlite" else None, backend=db_backend, mysql_config=mysql_config)
        self.upload_dir = Path(upload_dir).resolve()
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_by_user: dict[int, set[ClientSession]] = {}
        self.tokens: dict[str, int] = {}
        self.sessions_lock = threading.RLock()
        self.server_socket: socket.socket | None = None
        self._stopped = threading.Event()

    def serve_forever(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            self.server_socket = sock
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.host, self.port))
            sock.listen(100)
            LOGGER.info("OCHAT server listening on %s:%s", self.host, self.port)
            while not self._stopped.is_set():
                try:
                    client_sock, address = sock.accept()
                except OSError:
                    break
                thread = threading.Thread(target=self.handle_client, args=(client_sock, address), daemon=True)
                thread.start()

    def stop(self) -> None:
        self._stopped.set()
        if self.server_socket:
            self.server_socket.close()
        self.storage.close()

    def handle_client(self, sock: socket.socket, address: tuple[str, int]) -> None:
        session = ClientSession(sock, address, self)
        reader = LineReader(sock)
        try:
            while True:
                packet = reader.read_packet()
                if packet is None:
                    break
                if not packet:
                    continue
                action = str(packet.get("action", ""))
                response = self.dispatch(session, action, packet)
                if response is not None:
                    session.send("response", request=action, request_id=packet.get("request_id"), **response)
        except (ConnectionError, OSError, ProtocolError) as exc:
            LOGGER.debug("client %s disconnected: %s", address, exc)
        finally:
            self.unregister_session(session)
            try:
                sock.close()
            except OSError:
                pass

    def dispatch(self, session: ClientSession, action: str, packet: dict[str, Any]) -> dict[str, Any] | None:
        try:
            handlers = {
                "register": self.handle_register,
                "login": self.handle_login,
                "resume": self.handle_resume,
                "logout": self.handle_logout,
                "profile.update": self.handle_profile_update,
                "users.search": self.handle_users_search,
                "friends.list": self.handle_friends_list,
                "friends.add": self.handle_friends_add,
                "friends.update": self.handle_friends_update,
                "friends.remove": self.handle_friends_remove,
                "groups.list": self.handle_groups_list,
                "groups.create": self.handle_groups_create,
                "groups.invite": self.handle_groups_invite,
                "groups.remove_member": self.handle_groups_remove_member,
                "groups.members": self.handle_groups_members,
                "messages.direct.send": self.handle_direct_send,
                "messages.group.send": self.handle_group_send,
                "messages.direct.history": self.handle_direct_history,
                "messages.group.history": self.handle_group_history,
                "messages.search": self.handle_message_search,
                "messages.recall": self.handle_message_recall,
                "files.download": self.handle_file_download,
                "files.upload": self.handle_file_upload,
            }
            handler = handlers.get(action)
            if handler is None:
                return fail(f"unknown action: {action}", code="UNKNOWN_ACTION")
            return handler(session, packet)
        except PermissionError as exc:
            return fail(str(exc), code="PERMISSION_DENIED")
        except NotFoundError as exc:
            return fail(str(exc), code="NOT_FOUND")
        except StorageError as exc:
            return fail(str(exc), code="BAD_REQUEST")
        except ValueError as exc:
            return fail(str(exc), code="BAD_REQUEST")
        except Exception:
            LOGGER.exception("unhandled error while processing action %s", action)
            return fail("internal server error", code="INTERNAL_ERROR")

    def handle_register(self, session: ClientSession, packet: dict[str, Any]) -> dict[str, Any]:
        username = str(packet.get("username", "")).strip()
        password = str(packet.get("password", ""))
        nickname = str(packet.get("nickname", "")).strip()
        if not validate_username(username):
            raise ValueError("username must be 3-20 letters, numbers or underscores")
        if not validate_password(password):
            raise ValueError("password must be 6-64 characters")
        if nickname and not validate_display_text(nickname, 32):
            raise ValueError("nickname is too long")
        user = self.storage.create_user(username, password, nickname=nickname or username)
        return ok(user=user)

    def handle_login(self, session: ClientSession, packet: dict[str, Any]) -> dict[str, Any]:
        username = str(packet.get("username", "")).strip()
        password = str(packet.get("password", ""))
        if not username or not password:
            raise ValueError("username and password cannot be empty")
        user = self.storage.authenticate(username, password)
        if not user:
            raise PermissionError("invalid username or password")
        self.register_session(session, user)
        return ok(user=user, token=session.token, friends=self.friends_payload(user["id"]), groups=self.storage.list_groups(user["id"]))

    def handle_resume(self, session: ClientSession, packet: dict[str, Any]) -> dict[str, Any]:
        token = str(packet.get("token", ""))
        with self.sessions_lock:
            user_id = self.tokens.get(token)
        if not user_id:
            raise PermissionError("invalid session token")
        user = self.storage.get_user_by_id(user_id)
        self.register_session(session, user, token)
        return ok(user=user, token=token, friends=self.friends_payload(user_id), groups=self.storage.list_groups(user_id))

    def handle_logout(self, session: ClientSession, packet: dict[str, Any]) -> dict[str, Any]:
        self.unregister_session(session, forget_token=True)
        return ok()

    def handle_profile_update(self, session: ClientSession, packet: dict[str, Any]) -> dict[str, Any]:
        user = session.require_user()
        nickname = str(packet.get("nickname", "")).strip() or user["username"]
        signature = str(packet.get("signature", "")).strip()
        contact = str(packet.get("contact", "")).strip()
        avatar = str(packet.get("avatar", "")).strip()
        if not validate_display_text(nickname, 32):
            raise ValueError("nickname is too long")
        if not validate_display_text(signature, 120):
            raise ValueError("signature is too long")
        if not validate_display_text(contact, 80):
            raise ValueError("contact is too long")
        if not validate_display_text(avatar, 255):
            raise ValueError("avatar is too long")
        updated = self.storage.update_profile(user["id"], nickname, signature, contact, avatar)
        session.user = updated
        self.broadcast_to_user(user["id"], "profile.updated", user=updated)
        return ok(user=updated)

    def handle_users_search(self, session: ClientSession, packet: dict[str, Any]) -> dict[str, Any]:
        session.require_user()
        keyword = str(packet.get("keyword", "")).strip()
        if not keyword:
            return ok(users=[])
        if not validate_search_keyword(keyword):
            raise ValueError("search keyword is too long")
        return ok(users=self.storage.find_users(keyword))

    def handle_friends_list(self, session: ClientSession, packet: dict[str, Any]) -> dict[str, Any]:
        user = session.require_user()
        return ok(friends=self.friends_payload(user["id"]))

    def handle_friends_add(self, session: ClientSession, packet: dict[str, Any]) -> dict[str, Any]:
        user = session.require_user()
        friend_username = str(packet.get("username", "")).strip()
        remark = str(packet.get("remark", "")).strip()
        group_name = str(packet.get("group_name", "Friends")).strip() or "Friends"
        if not validate_username(friend_username):
            raise ValueError("invalid friend username")
        if not validate_display_text(remark, 32):
            raise ValueError("remark is too long")
        if not validate_display_text(group_name, 32):
            raise ValueError("group name is too long")
        friend = self.storage.add_friend(user["id"], friend_username, remark, group_name)
        self.broadcast_to_user(user["id"], "friends.updated", friends=self.friends_payload(user["id"]))
        self.broadcast_to_user(friend["id"], "friends.updated", friends=self.friends_payload(friend["id"]))
        return ok(friend=friend)

    def handle_friends_update(self, session: ClientSession, packet: dict[str, Any]) -> dict[str, Any]:
        user = session.require_user()
        friend_id = int(packet.get("friend_id", 0))
        remark = str(packet.get("remark", "")).strip()
        group_name = str(packet.get("group_name", "Friends")).strip() or "Friends"
        if not validate_display_text(remark, 32):
            raise ValueError("remark is too long")
        if not validate_display_text(group_name, 32):
            raise ValueError("group name is too long")
        friend = self.storage.update_friend(user["id"], friend_id, remark, group_name)
        self.broadcast_to_user(user["id"], "friends.updated", friends=self.friends_payload(user["id"]))
        return ok(friend=friend)

    def handle_friends_remove(self, session: ClientSession, packet: dict[str, Any]) -> dict[str, Any]:
        user = session.require_user()
        friend_id = int(packet.get("friend_id", 0))
        friend = self.storage.get_friend(user["id"], friend_id)
        self.storage.remove_friend(user["id"], friend_id)
        self.broadcast_to_user(user["id"], "friends.updated", friends=self.friends_payload(user["id"]))
        self.broadcast_to_user(friend["id"], "friends.updated", friends=self.friends_payload(friend["id"]))
        return ok()

    def handle_groups_list(self, session: ClientSession, packet: dict[str, Any]) -> dict[str, Any]:
        user = session.require_user()
        return ok(groups=self.storage.list_groups(user["id"]))

    def handle_groups_create(self, session: ClientSession, packet: dict[str, Any]) -> dict[str, Any]:
        user = session.require_user()
        name = str(packet.get("name", "")).strip()
        if not 1 <= len(name) <= 40:
            raise ValueError("group name must be 1-40 characters")
        group = self.storage.create_group(user["id"], name)
        self.broadcast_to_user(user["id"], "groups.updated", groups=self.storage.list_groups(user["id"]))
        return ok(group=group)

    def handle_groups_invite(self, session: ClientSession, packet: dict[str, Any]) -> dict[str, Any]:
        user = session.require_user()
        group_id = int(packet.get("group_id", 0))
        username = str(packet.get("username", "")).strip()
        if not validate_username(username):
            raise ValueError("invalid username")
        group = self.storage.invite_group_member(group_id, user["id"], username)
        for member_id in self.storage.group_member_ids(group_id):
            self.broadcast_to_user(member_id, "groups.updated", groups=self.storage.list_groups(member_id))
        return ok(group=group, members=self.storage.list_group_members(group_id, user["id"]))

    def handle_groups_remove_member(self, session: ClientSession, packet: dict[str, Any]) -> dict[str, Any]:
        user = session.require_user()
        group_id = int(packet.get("group_id", 0))
        member_id = int(packet.get("member_id", 0))
        self.storage.remove_group_member(group_id, user["id"], member_id)
        for uid in {user["id"], member_id, *self.storage.group_member_ids(group_id)}:
            self.broadcast_to_user(uid, "groups.updated", groups=self.storage.list_groups(uid))
        return ok()

    def handle_groups_members(self, session: ClientSession, packet: dict[str, Any]) -> dict[str, Any]:
        user = session.require_user()
        group_id = int(packet.get("group_id", 0))
        return ok(members=self.storage.list_group_members(group_id, user["id"]))

    def handle_direct_send(self, session: ClientSession, packet: dict[str, Any]) -> dict[str, Any]:
        user = session.require_user()
        receiver_id = int(packet.get("receiver_id", 0))
        content = str(packet.get("content", "")).strip()
        message_type = str(packet.get("message_type", "text"))
        file_id = self._optional_int(packet.get("file_id"))
        if not validate_message(message_type, content, file_id):
            raise ValueError("invalid message content")
        message = self.storage.save_direct_message(user["id"], receiver_id, content, message_type, file_id)
        self.broadcast_to_user(user["id"], "message.new", message=message)
        self.broadcast_to_user(receiver_id, "message.new", message=message)
        return ok(message=message)

    def handle_group_send(self, session: ClientSession, packet: dict[str, Any]) -> dict[str, Any]:
        user = session.require_user()
        group_id = int(packet.get("group_id", 0))
        content = str(packet.get("content", "")).strip()
        message_type = str(packet.get("message_type", "text"))
        file_id = self._optional_int(packet.get("file_id"))
        if not validate_message(message_type, content, file_id):
            raise ValueError("invalid message content")
        message = self.storage.save_group_message(user["id"], group_id, content, message_type, file_id)
        for member_id in self.storage.group_member_ids(group_id):
            self.broadcast_to_user(member_id, "message.new", message=message)
        return ok(message=message)

    def handle_direct_history(self, session: ClientSession, packet: dict[str, Any]) -> dict[str, Any]:
        user = session.require_user()
        friend_id = int(packet.get("friend_id", 0))
        limit = self._limit(packet.get("limit", 100))
        return ok(messages=self.storage.list_direct_history(user["id"], friend_id, limit))

    def handle_group_history(self, session: ClientSession, packet: dict[str, Any]) -> dict[str, Any]:
        user = session.require_user()
        group_id = int(packet.get("group_id", 0))
        limit = self._limit(packet.get("limit", 100))
        return ok(messages=self.storage.list_group_history(user["id"], group_id, limit))

    def handle_message_search(self, session: ClientSession, packet: dict[str, Any]) -> dict[str, Any]:
        user = session.require_user()
        keyword = str(packet.get("keyword", "")).strip()
        if not keyword:
            return ok(messages=[])
        if not validate_search_keyword(keyword):
            raise ValueError("search keyword is too long")
        return ok(messages=self.storage.search_messages(user["id"], keyword))

    def handle_message_recall(self, session: ClientSession, packet: dict[str, Any]) -> dict[str, Any]:
        user = session.require_user()
        message_id = int(packet.get("message_id", 0))
        message = self.storage.recall_message(user["id"], message_id)
        targets = {user["id"]}
        if message["conversation_type"] == "direct":
            targets.add(int(message["target_id"]))
        else:
            targets.update(self.storage.group_member_ids(int(message["target_id"])))
        for user_id in targets:
            self.broadcast_to_user(user_id, "message.recalled", message=message)
        return ok(message=message)

    def handle_file_download(self, session: ClientSession, packet: dict[str, Any]) -> dict[str, Any]:
        user = session.require_user()
        file_id = int(packet.get("file_id", 0))
        file_record = self.storage.get_file_for_user(user["id"], file_id)
        path = self._safe_upload_path(str(file_record["storage_name"]))
        if not path.exists() or not path.is_file():
            raise NotFoundError("file content not found on server")
        data = path.read_bytes()
        return ok(
            file={
                "id": file_record["id"],
                "filename": file_record["original_name"],
                "size": file_record["size"],
                "mime_type": file_record["mime_type"],
                "content_b64": base64.b64encode(data).decode("ascii"),
            }
        )

    def handle_file_upload(self, session: ClientSession, packet: dict[str, Any]) -> dict[str, Any]:
        user = session.require_user()
        original_name = sanitize_filename(str(packet.get("filename", "")))
        content_b64 = str(packet.get("content_b64", ""))
        mime_type = str(packet.get("mime_type", "application/octet-stream"))[:80]
        try:
            data = base64.b64decode(content_b64.encode("ascii"), validate=True)
        except Exception as exc:
            raise ValueError("invalid file payload") from exc
        if not is_allowed_file(original_name, len(data)):
            raise ValueError("file type or size is not allowed")
        storage_name = f"{uuid.uuid4().hex}_{original_name}"
        path = self._safe_upload_path(storage_name)
        path.write_bytes(data)
        try:
            file_record = self.storage.save_file(user["id"], original_name, storage_name, len(data), mime_type)
        except Exception:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                LOGGER.debug("failed to remove orphan upload %s", path, exc_info=True)
            raise
        return ok(file=file_record)

    def _safe_upload_path(self, storage_name: str) -> Path:
        filename = Path(storage_name).name
        path = (self.upload_dir / filename).resolve()
        upload_root = self.upload_dir.resolve()
        if upload_root != path.parent:
            raise PermissionError("invalid file path")
        return path

    @staticmethod
    def _optional_int(value: Any) -> int | None:
        if value in (None, ""):
            return None
        return int(value)

    @staticmethod
    def _limit(value: Any, default: int = 100, maximum: int = 300) -> int:
        try:
            limit = int(value)
        except (TypeError, ValueError):
            return default
        return max(1, min(limit, maximum))

    def register_session(self, session: ClientSession, user: dict[str, Any], token: str | None = None) -> None:
        self.unregister_session(session)
        session.user = user
        session.token = token or create_token()
        with self.sessions_lock:
            self.tokens[session.token] = user["id"]
            self.sessions_by_user.setdefault(user["id"], set()).add(session)
        self.broadcast_presence()

    def unregister_session(self, session: ClientSession, forget_token: bool = False) -> None:
        user_id = session.user_id
        token = session.token
        if user_id is not None:
            with self.sessions_lock:
                sessions = self.sessions_by_user.get(user_id)
                if sessions:
                    sessions.discard(session)
                    if not sessions:
                        self.sessions_by_user.pop(user_id, None)
                if forget_token and token:
                    self.tokens.pop(token, None)
        session.user = None
        session.token = None
        if user_id is not None:
            self.broadcast_presence()

    def friends_payload(self, user_id: int) -> list[dict[str, Any]]:
        friends = self.storage.list_friends(user_id)
        online_ids = self.online_user_ids()
        for friend in friends:
            friend["online"] = friend["id"] in online_ids
        return friends

    def online_user_ids(self) -> set[int]:
        with self.sessions_lock:
            return {user_id for user_id, sessions in self.sessions_by_user.items() if sessions}

    def broadcast_presence(self) -> None:
        online_ids = sorted(self.online_user_ids())
        with self.sessions_lock:
            sessions = [session for sessions in self.sessions_by_user.values() for session in sessions]
        for session in sessions:
            try:
                user = session.require_user()
                session.send("presence", online_user_ids=online_ids, friends=self.friends_payload(user["id"]))
            except Exception:
                LOGGER.debug("failed to broadcast presence", exc_info=True)

    def broadcast_to_user(self, user_id: int, action: str, **payload: Any) -> None:
        with self.sessions_lock:
            sessions = list(self.sessions_by_user.get(user_id, set()))
        for session in sessions:
            try:
                session.send(action, **payload)
            except OSError:
                LOGGER.debug("failed to send event to user %s", user_id)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the OCHAT server.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", default=DEFAULT_PORT, type=int)
    parser.add_argument("--db-backend", choices=("mysql", "sqlite"), default="mysql")
    parser.add_argument("--db", default=str(Path("database") / "ochat.db"), help="SQLite database path when --db-backend sqlite")
    parser.add_argument("--mysql-host", default=None)
    parser.add_argument("--mysql-port", default=None, type=int)
    parser.add_argument("--mysql-user", default=None)
    parser.add_argument("--mysql-password", default=None)
    parser.add_argument("--mysql-database", default=None)
    parser.add_argument("--upload-dir", default=str(Path("database") / "uploads"))
    parser.add_argument("--debug", action="store_true")
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    mysql_config = {
        key: value
        for key, value in {
            "host": args.mysql_host,
            "port": args.mysql_port,
            "user": args.mysql_user,
            "password": args.mysql_password,
            "database": args.mysql_database,
        }.items()
        if value is not None
    }
    print(f"Starting OCHAT server on {args.host}:{args.port} using {args.db_backend}...", flush=True)
    try:
        server = ChatServer(
            args.host,
            args.port,
            args.db,
            db_backend=args.db_backend,
            mysql_config=mysql_config,
            upload_dir=args.upload_dir,
        )
    except Exception:
        print("OCHAT server failed to start:", file=sys.stderr, flush=True)
        traceback.print_exc()
        raise SystemExit(1)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        LOGGER.info("server stopped")
    finally:
        server.stop()


if __name__ == "__main__":
    main()
