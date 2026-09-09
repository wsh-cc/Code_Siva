from __future__ import annotations

import argparse
import socket
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from server.app import ChatServer


def check_import(module_name: str) -> bool:
    try:
        __import__(module_name)
        print(f"[OK] Python module: {module_name}")
        return True
    except Exception as exc:
        print(f"[FAIL] Python module: {module_name} ({exc})")
        return False


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def check_tcp(host: str, port: int, quiet: bool = False) -> bool:
    try:
        with socket.create_connection((host, port), timeout=2):
            if not quiet:
                print(f"[OK] TCP connect: {host}:{port}")
            return True
    except OSError as exc:
        if not quiet:
            print(f"[WARN] TCP connect: {host}:{port} ({exc})")
        return False


def check_sqlite_server() -> bool:
    port = free_port()
    db_path = ROOT / "database" / "ochat_env_check.db"
    upload_dir = ROOT / "database" / "env_check_uploads"
    server = ChatServer(
        host="127.0.0.1",
        port=port,
        db_backend="sqlite",
        db_path=db_path,
        upload_dir=upload_dir,
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        deadline = time.time() + 3
        while time.time() < deadline:
            if check_tcp("127.0.0.1", port, quiet=True):
                print("[OK] OCHAT SQLite server smoke test")
                return True
            time.sleep(0.2)
        print("[FAIL] OCHAT SQLite server smoke test")
        return False
    finally:
        server.stop()
        for suffix in ("", "-shm", "-wal"):
            try:
                db_path.with_name(db_path.name + suffix).unlink(missing_ok=True)
            except OSError:
                pass
        shutil.rmtree(upload_dir, ignore_errors=True)


def check_mysql_cli(mysql_exe: str) -> bool:
    if not Path(mysql_exe).exists():
        print(f"[WARN] mysql.exe not found: {mysql_exe}")
        return False
    result = subprocess.run([mysql_exe, "--version"], capture_output=True, text=True, check=False)
    if result.returncode == 0:
        print(f"[OK] MySQL client: {result.stdout.strip()}")
        return True
    print(f"[WARN] MySQL client check failed: {result.stderr.strip()}")
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Check local OCHAT runtime environment.")
    parser.add_argument("--mysql-exe", default=r"C:\Program Files\MySQL\MySQL Server 9.7\bin\mysql.exe")
    args = parser.parse_args()

    print(f"[INFO] Python: {sys.executable}")
    print(f"[INFO] Version: {sys.version.split()[0]}")
    checks = [
        check_import("pymysql"),
        check_import("tkinter"),
        check_mysql_cli(args.mysql_exe),
        check_tcp("127.0.0.1", 3306),
        check_sqlite_server(),
    ]
    return 0 if all(checks[:2]) and checks[-1] else 1


if __name__ == "__main__":
    raise SystemExit(main())
