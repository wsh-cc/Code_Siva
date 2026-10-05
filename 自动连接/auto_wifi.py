#!/usr/bin/env python3
"""Auto-connect to preferred Windows Wi-Fi networks.

This tool uses the built-in `netsh wlan` command. It does not discover,
recover, or crack passwords; it only connects to profiles already known to
Windows, or to profiles created from a password you explicitly provide.
"""

from __future__ import annotations

import argparse
import base64
import copy
import ctypes
import getpass
import json
import locale
import logging
import os
import re
import subprocess
import sys
import tempfile
import time
from ctypes import wintypes
from dataclasses import dataclass
from html.parser import HTMLParser
from http.cookiejar import CookieJar
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urljoin, urlparse
from urllib.request import HTTPCookieProcessor, Request, build_opener
from xml.sax.saxutils import escape


DEFAULT_CONFIG: dict[str, Any] = {
    "interval_seconds": 30,
    "scan_wait_seconds": 60,
    "scan_retry_seconds": 5,
    "connect_timeout_seconds": 20,
    "disconnect_before_connect": False,
    "interface": "",
    "log_file": "logs/auto_wifi.log",
    "blocked_ssids": [],
    "networks": [],
    "portal": {
        "enabled": False,
        "mode": "generic",
        "isp": "",
        "connectivity_check_url": "http://www.msftconnecttest.com/connecttest.txt",
        "expected_status": 200,
        "expected_content": "Microsoft Connect Test",
        "login_url": "",
        "method": "",
        "username_field": "",
        "password_field": "",
        "extra_fields": {},
        "success_contains": "",
        "failure_contains": "",
        "credential_file": "credentials/campus_portal.json",
        "portal_wait_seconds": 60,
        "retry_seconds": 3,
        "max_login_attempts": 3,
        "request_timeout_seconds": 10,
        "verify_after_login": True,
        "verify_delay_seconds": 3,
        "cqupt_portal_url": "http://192.168.200.2:801/eportal",
        "cqupt_referer": "http://192.168.200.2/",
        "cqupt_mac": "",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
    },
}

SSID_RE = re.compile(r"^\s*SSID\s+\d+\s*:\s*(.*?)\s*$", re.IGNORECASE)
PROFILE_HINTS = ("profile", "profile", "configuration file", "配置文件", "設定檔")
CONNECTED_WORDS = ("connected", "已连接", "已連線")
DISCONNECTED_WORDS = ("disconnected", "not connected", "未连接", "未連線")
CQUPT_ISP_ALIASES = {
    "cmcc": "cmcc",
    "mobile": "cmcc",
    "移动": "cmcc",
    "中国移动": "cmcc",
    "telecom": "telecom",
    "电信": "telecom",
    "中国电信": "telecom",
    "unicom": "unicom",
    "联通": "unicom",
    "中国联通": "unicom",
    "xyw": "xyw",
    "校园网": "xyw",
    "教师": "xyw",
}


class WifiError(RuntimeError):
    """Raised when a Wi-Fi operation fails."""


def deep_update(base: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_update(base[key], value)
        else:
            base[key] = value
    return base


def default_config() -> dict[str, Any]:
    return copy.deepcopy(DEFAULT_CONFIG)


def preferred_encoding() -> str:
    return locale.getpreferredencoding(False) or "utf-8"


def netsh_executable() -> str:
    windir = os.environ.get("WINDIR") or r"C:\Windows"
    netsh_path = Path(windir) / "System32" / "netsh.exe"
    if netsh_path.exists():
        return str(netsh_path)
    return "netsh"


def run_netsh(*args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
    command = [netsh_executable(), *args]
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding=preferred_encoding(),
        errors="replace",
    )
    if check and result.returncode != 0:
        details = (result.stderr or result.stdout or "").strip()
        raise WifiError(f"netsh failed: {' '.join(command)}\n{details}")
    return result


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise WifiError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise WifiError("Config root must be a JSON object.")

    cfg = deep_update(default_config(), data)
    if not isinstance(cfg.get("networks"), list):
        raise WifiError("Config field 'networks' must be a list.")
    if not isinstance(cfg.get("blocked_ssids"), list):
        raise WifiError("Config field 'blocked_ssids' must be a list.")
    if not isinstance(cfg.get("portal"), dict):
        raise WifiError("Config field 'portal' must be an object.")
    return cfg


def write_config(path: Path, cfg: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def init_config(path: Path, force: bool) -> None:
    if path.exists() and not force:
        raise WifiError(f"Config already exists: {path}")
    write_config(path, default_config())


def setup_logging(cfg: dict[str, Any], config_path: Path, verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    handlers: list[logging.Handler] = [logging.StreamHandler()]

    log_file = str(cfg.get("log_file") or "").strip()
    if log_file:
        log_path = Path(log_file)
        if not log_path.is_absolute():
            log_path = config_path.parent / log_path
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_path, encoding="utf-8"))

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=handlers,
    )


class DataBlob(ctypes.Structure):
    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_ubyte)),
    ]


@dataclass
class FetchResult:
    status: int
    url: str
    text: str
    headers: Any


@dataclass
class LoginSubmission:
    url: str
    method: str
    fields: dict[str, str]
    username_field: str
    password_field: str


class LoginFormParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.forms: list[dict[str, Any]] = []
        self._current_form: dict[str, Any] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attr_map = {name.lower(): value or "" for name, value in attrs}
        if tag == "form":
            self._current_form = {"attrs": attr_map, "inputs": []}
            return
        if self._current_form is None:
            return
        if tag in {"input", "button", "select"}:
            attr_map["tag"] = tag
            self._current_form["inputs"].append(attr_map)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "form" and self._current_form is not None:
            self.forms.append(self._current_form)
            self._current_form = None

    def finish(self) -> list[dict[str, Any]]:
        if self._current_form is not None:
            self.forms.append(self._current_form)
            self._current_form = None
        return self.forms


def resolve_config_path(config_path: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return config_path.parent / path


def _blob_from_bytes(data: bytes) -> tuple[DataBlob, ctypes.Array[Any]]:
    buffer = ctypes.create_string_buffer(data)
    blob = DataBlob(len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte)))
    return blob, buffer


def _last_windows_error(prefix: str) -> WifiError:
    return WifiError(f"{prefix}: Windows error {ctypes.get_last_error()}")


def dpapi_decrypt_error(error_code: int) -> WifiError:
    return WifiError(
        "Could not decrypt credential: "
        f"Windows error {error_code}. "
        "This credential was encrypted by a different Windows logon context. "
        "Re-save it from your own PowerShell with: "
        '& "E:\\python312\\python.exe" .\\auto_wifi.py credentials '
        '--username "1693070" --isp unicom --mode cqupt --enable-portal'
    )


def dpapi_protect(text: str) -> str:
    if os.name != "nt" or not hasattr(ctypes, "WinDLL"):
        raise WifiError("Encrypted credential storage requires Windows DPAPI.")

    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    crypt32.CryptProtectData.argtypes = [
        ctypes.POINTER(DataBlob),
        wintypes.LPCWSTR,
        ctypes.POINTER(DataBlob),
        wintypes.LPVOID,
        wintypes.LPVOID,
        wintypes.DWORD,
        ctypes.POINTER(DataBlob),
    ]
    crypt32.CryptProtectData.restype = wintypes.BOOL
    kernel32.LocalFree.argtypes = [wintypes.HLOCAL]
    kernel32.LocalFree.restype = wintypes.HLOCAL

    in_blob, _buffer = _blob_from_bytes(text.encode("utf-8"))
    out_blob = DataBlob()
    ok = crypt32.CryptProtectData(
        ctypes.byref(in_blob),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(out_blob),
    )
    if not ok:
        raise _last_windows_error("Could not encrypt credential")
    try:
        protected = ctypes.string_at(out_blob.pbData, out_blob.cbData)
        return base64.b64encode(protected).decode("ascii")
    finally:
        kernel32.LocalFree(ctypes.cast(out_blob.pbData, wintypes.HLOCAL))


def dpapi_unprotect(token: str) -> str:
    if os.name != "nt" or not hasattr(ctypes, "WinDLL"):
        raise WifiError("Encrypted credential storage requires Windows DPAPI.")

    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    crypt32.CryptUnprotectData.argtypes = [
        ctypes.POINTER(DataBlob),
        ctypes.POINTER(wintypes.LPWSTR),
        ctypes.POINTER(DataBlob),
        wintypes.LPVOID,
        wintypes.LPVOID,
        wintypes.DWORD,
        ctypes.POINTER(DataBlob),
    ]
    crypt32.CryptUnprotectData.restype = wintypes.BOOL
    kernel32.LocalFree.argtypes = [wintypes.HLOCAL]
    kernel32.LocalFree.restype = wintypes.HLOCAL

    raw = base64.b64decode(token.encode("ascii"))
    in_blob, _buffer = _blob_from_bytes(raw)
    out_blob = DataBlob()
    ok = crypt32.CryptUnprotectData(
        ctypes.byref(in_blob),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(out_blob),
    )
    if not ok:
        raise dpapi_decrypt_error(ctypes.get_last_error())
    try:
        unprotected = ctypes.string_at(out_blob.pbData, out_blob.cbData)
        return unprotected.decode("utf-8")
    finally:
        kernel32.LocalFree(ctypes.cast(out_blob.pbData, wintypes.HLOCAL))


def portal_config(cfg: dict[str, Any]) -> dict[str, Any]:
    portal = cfg.get("portal")
    if not isinstance(portal, dict):
        return {}
    return portal


def portal_enabled(cfg: dict[str, Any]) -> bool:
    return bool(portal_config(cfg).get("enabled"))


def portal_credentials_path(cfg: dict[str, Any], config_path: Path) -> Path:
    portal = portal_config(cfg)
    raw_path = str(portal.get("credential_file") or "").strip()
    if not raw_path:
        raw_path = DEFAULT_CONFIG["portal"]["credential_file"]
    return resolve_config_path(config_path, raw_path)


def normalize_isp(value: str) -> str:
    key = value.strip().lower()
    if not key:
        return ""
    return CQUPT_ISP_ALIASES.get(key, value.strip())


def save_portal_credentials(path: Path, username: str, password: str, isp: str = "") -> None:
    username = username.strip()
    if not username:
        raise WifiError("Username cannot be empty.")
    if not password:
        raise WifiError("Password cannot be empty.")

    normalized_isp = normalize_isp(isp)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "username": username,
        "password_dpapi": dpapi_protect(password),
    }
    if normalized_isp:
        payload["isp"] = normalized_isp
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def load_portal_credentials(path: Path) -> dict[str, str]:
    if not path.exists():
        raise WifiError(
            "Campus portal credentials are missing. "
            "Run: python .\\auto_wifi.py credentials --username YOUR_ACCOUNT"
        )
    with path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    username = str(payload.get("username") or "").strip()
    token = str(payload.get("password_dpapi") or "").strip()
    if not username or not token:
        raise WifiError(f"Credential file is incomplete: {path}")
    credentials = {"username": username, "password": dpapi_unprotect(token)}
    isp = normalize_isp(str(payload.get("isp") or ""))
    if isp:
        credentials["isp"] = isp
    return credentials


def decode_response_body(raw: bytes, headers: Any) -> str:
    charset = None
    if hasattr(headers, "get_content_charset"):
        charset = headers.get_content_charset()
    if not charset:
        charset = "utf-8"
    return raw.decode(charset, errors="replace")


def fetch_url(
    opener: Any,
    url: str,
    method: str = "GET",
    fields: dict[str, str] | None = None,
    timeout: int = 10,
    headers: dict[str, str] | None = None,
) -> FetchResult:
    method = method.upper()
    request_headers = {
        "User-Agent": "Mozilla/5.0 AutoWiFiConnector/1.0",
        "Accept": "text/html,application/xhtml+xml,application/xml,text/plain;q=0.9,*/*;q=0.8",
    }
    if headers:
        request_headers.update(headers)
    request_url = url
    data = None
    if fields is not None:
        encoded = urlencode(fields).encode("utf-8")
        if method == "GET":
            separator = "&" if "?" in request_url else "?"
            request_url = f"{request_url}{separator}{encoded.decode('utf-8')}"
        else:
            data = encoded
            request_headers["Content-Type"] = "application/x-www-form-urlencoded"

    request = Request(request_url, data=data, headers=request_headers, method=method)
    try:
        with opener.open(request, timeout=timeout) as response:
            raw = response.read()
            return FetchResult(
                status=response.getcode(),
                url=response.geturl(),
                text=decode_response_body(raw, response.headers),
                headers=response.headers,
            )
    except HTTPError as exc:
        raw = exc.read()
        return FetchResult(
            status=exc.code,
            url=exc.geturl(),
            text=decode_response_body(raw, exc.headers),
            headers=exc.headers,
        )
    except URLError as exc:
        raise WifiError(f"HTTP request failed for {url}: {exc.reason}") from exc


def parse_login_forms(html: str) -> list[dict[str, Any]]:
    parser = LoginFormParser()
    parser.feed(html)
    return parser.finish()


def form_input_names(form: dict[str, Any]) -> set[str]:
    return {
        str(input_item.get("name") or "")
        for input_item in form.get("inputs", [])
        if input_item.get("name")
    }


def choose_login_form(
    forms: list[dict[str, Any]],
    username_field: str,
    password_field: str,
) -> dict[str, Any] | None:
    if not forms:
        return None

    def score(form: dict[str, Any]) -> int:
        names = form_input_names(form)
        attrs = form.get("attrs", {})
        searchable = " ".join(
            str(attrs.get(key, "")) for key in ("action", "name", "id", "class")
        ).lower()
        points = 0
        if username_field and username_field in names:
            points += 4
        if password_field and password_field in names:
            points += 5
        if any(str(item.get("type", "")).lower() == "password" for item in form.get("inputs", [])):
            points += 6
        if "login" in searchable or "auth" in searchable:
            points += 2
        return points

    return max(forms, key=score)


def infer_username_field(form: dict[str, Any] | None, configured: str) -> str:
    if configured:
        return configured
    if not form:
        return "username"
    for item in form.get("inputs", []):
        input_type = str(item.get("type", "")).lower()
        name = str(item.get("name") or "")
        if name and input_type in {"", "text", "email", "tel", "number"}:
            return name
    return "username"


def infer_password_field(form: dict[str, Any] | None, configured: str) -> str:
    if configured:
        return configured
    if not form:
        return "password"
    for item in form.get("inputs", []):
        input_type = str(item.get("type", "")).lower()
        name = str(item.get("name") or "")
        if name and input_type == "password":
            return name
    return "password"


def build_login_submission(
    login_page: FetchResult,
    portal: dict[str, Any],
    credentials: dict[str, str],
) -> LoginSubmission:
    username_field = str(portal.get("username_field") or "").strip()
    password_field = str(portal.get("password_field") or "").strip()
    forms = parse_login_forms(login_page.text)
    form = choose_login_form(forms, username_field, password_field)

    configured_login_url = str(portal.get("login_url") or "").strip()
    configured_method = str(portal.get("method") or "").strip().upper()
    method = configured_method or "POST"
    action_url = configured_login_url or login_page.url

    fields: dict[str, str] = {}
    if form:
        attrs = form.get("attrs", {})
        method = configured_method or str(attrs.get("method") or "POST").upper()
        action = str(attrs.get("action") or "").strip()
        if action and not configured_login_url:
            action_url = urljoin(login_page.url, action)

        for item in form.get("inputs", []):
            name = str(item.get("name") or "")
            if not name:
                continue
            input_type = str(item.get("type", "")).lower()
            if input_type in {"button", "file", "image", "reset", "submit"}:
                continue
            fields[name] = str(item.get("value") or "")

    extra_fields = portal.get("extra_fields") or {}
    if not isinstance(extra_fields, dict):
        raise WifiError("portal.extra_fields must be an object.")
    fields.update({str(key): str(value) for key, value in extra_fields.items()})

    username_field = infer_username_field(form, username_field)
    password_field = infer_password_field(form, password_field)
    fields[username_field] = credentials["username"]
    fields[password_field] = credentials["password"]

    return LoginSubmission(
        url=action_url,
        method=method,
        fields=fields,
        username_field=username_field,
        password_field=password_field,
    )


def make_http_opener() -> Any:
    return build_opener(HTTPCookieProcessor(CookieJar()))


def internet_is_available(opener: Any, portal: dict[str, Any]) -> tuple[bool, FetchResult | None]:
    check_url = str(portal.get("connectivity_check_url") or "").strip()
    if not check_url:
        return False, None

    timeout = int(portal.get("request_timeout_seconds") or 10)
    try:
        result = fetch_url(opener, check_url, timeout=timeout)
    except WifiError as exc:
        logging.debug("Connectivity check failed: %s", exc)
        return False, None

    expected_status = portal.get("expected_status")
    if expected_status not in (None, "") and result.status != int(expected_status):
        return False, result

    expected_content = str(portal.get("expected_content") or "")
    if expected_content and expected_content not in result.text:
        return False, result

    if not expected_content and not (200 <= result.status < 400):
        return False, result

    return True, result


def verify_internet_connectivity(cfg: dict[str, Any]) -> bool:
    online, result = internet_is_available(make_http_opener(), portal_config(cfg))
    if online:
        logging.info("Internet connectivity check succeeded.")
        return True

    if result is None:
        logging.warning("Internet connectivity check failed; no response was received.")
    else:
        logging.warning(
            "Internet connectivity check failed; status=%s url=%s.",
            result.status,
            result.url,
        )
    return False


def wait_for_portal_page(opener: Any, portal: dict[str, Any]) -> tuple[bool, FetchResult | None]:
    deadline = time.monotonic() + int(portal.get("portal_wait_seconds") or 60)
    retry_seconds = int(portal.get("retry_seconds") or 3)
    last_result: FetchResult | None = None

    while time.monotonic() < deadline:
        online, result = internet_is_available(opener, portal)
        if online:
            return True, None
        if result and result.text:
            last_result = result
            break
        time.sleep(retry_seconds)

    login_url = str(portal.get("login_url") or "").strip()
    if login_url:
        timeout = int(portal.get("request_timeout_seconds") or 10)
        return False, fetch_url(opener, login_url, timeout=timeout)
    if last_result:
        return False, last_result
    raise WifiError("Timed out waiting for the campus portal login page.")


def portal_mode(portal: dict[str, Any]) -> str:
    return str(portal.get("mode") or "generic").strip().lower()


def cqupt_account(username: str, isp: str) -> str:
    username = username.strip()
    isp = normalize_isp(isp)
    if username.startswith(",0,"):
        return username
    if "@" in username:
        return f",0,{username}"
    if not isp:
        raise WifiError("CQUPT portal requires an ISP. Use --isp unicom/cmcc/telecom/xyw.")
    return f",0,{username}@{isp}"


def parse_cqupt_params(result: FetchResult | None) -> dict[str, str]:
    if result is None:
        return {}

    params: dict[str, str] = {}
    query = parse_qs(urlparse(result.url).query, keep_blank_values=True)
    aliases = {
        "wlanuserip": "wlan_user_ip",
        "wlan_user_ip": "wlan_user_ip",
        "wlanacip": "wlan_ac_ip",
        "wlan_ac_ip": "wlan_ac_ip",
        "wlanacname": "wlan_ac_name",
        "wlan_ac_name": "wlan_ac_name",
        "mac": "wlan_user_mac",
        "wlan_user_mac": "wlan_user_mac",
    }
    for raw_key, values in query.items():
        key = aliases.get(raw_key.lower())
        if key and values:
            params[key] = values[0]

    patterns = {
        "wlan_user_ip": [
            r"wlanuserip=([0-9.]+)",
            r"wlan_user_ip['\"]?\s*[:=]\s*['\"]([^'\"]+)",
            r"v4(?:6)?ip['\"]?\s*[:=]\s*['\"]([^'\"]+)",
        ],
        "wlan_user_mac": [
            r"mac=([0-9a-fA-F:-]+)",
            r"wlan_user_mac['\"]?\s*[:=]\s*['\"]([^'\"]+)",
        ],
    }
    for key, key_patterns in patterns.items():
        if params.get(key):
            continue
        for pattern in key_patterns:
            match = re.search(pattern, result.text)
            if match:
                params[key] = match.group(1)
                break

    if "wlan_user_mac" in params:
        params["wlan_user_mac"] = params["wlan_user_mac"].replace(":", "").replace("-", "")
    return params


def cqupt_login_result_ok(text: str) -> bool:
    lowered = text.lower()
    success_markers = (
        '"result":"1"',
        '"result":1',
        '"ret_code":1',
        '"ret_code":"1"',
        "login_ok",
        "认证成功",
        "登录成功",
    )
    failure_markers = (
        '"result":"0"',
        '"ret_code":2',
        '"ret_code":"2"',
        "password is error",
        "密码错误",
        "认证失败",
        "登录失败",
    )
    if any(marker in lowered for marker in failure_markers):
        return False
    return any(marker in lowered for marker in success_markers)


def perform_cqupt_login(
    cfg: dict[str, Any],
    config_path: Path,
    opener: Any,
    dry_run: bool,
) -> bool:
    portal = portal_config(cfg)
    credentials = load_portal_credentials(portal_credentials_path(cfg, config_path))
    isp = normalize_isp(str(portal.get("isp") or credentials.get("isp") or ""))
    account = cqupt_account(credentials["username"], isp)
    timeout = int(portal.get("request_timeout_seconds") or 10)
    retry_seconds = int(portal.get("retry_seconds") or 3)
    attempts = int(portal.get("max_login_attempts") or 3)

    headers = {
        "User-Agent": str(portal.get("user_agent") or DEFAULT_CONFIG["portal"]["user_agent"]),
        "Referer": str(portal.get("cqupt_referer") or DEFAULT_CONFIG["portal"]["cqupt_referer"]),
        "Host": "192.168.200.2:801",
    }

    for attempt in range(1, attempts + 1):
        logging.info("CQUPT portal login attempt %s/%s.", attempt, attempts)
        became_online, login_page = wait_for_portal_page(opener, portal)
        if became_online:
            logging.info("Internet connectivity became available before login.")
            return True

        params = parse_cqupt_params(login_page)
        if not params.get("wlan_user_ip"):
            referer = str(portal.get("cqupt_referer") or DEFAULT_CONFIG["portal"]["cqupt_referer"])
            try:
                referer_page = fetch_url(opener, referer, timeout=timeout, headers=headers)
                params.update(parse_cqupt_params(referer_page))
            except WifiError as exc:
                logging.debug("Could not fetch CQUPT referer page: %s", exc)

        wlan_user_ip = params.get("wlan_user_ip", "")
        if not wlan_user_ip:
            raise WifiError("Could not find CQUPT wlanuserip from the portal redirect page.")

        mac = str(portal.get("cqupt_mac") or params.get("wlan_user_mac") or "000000000000")
        mac = mac.replace(":", "").replace("-", "")
        fields = {
            "c": "Portal",
            "a": "login",
            "callback": "dr1003",
            "login_method": "1",
            "user_account": account,
            "user_password": credentials["password"],
            "wlan_user_ip": wlan_user_ip,
            "wlan_user_mac": mac,
            "wlan_ac_ip": params.get("wlan_ac_ip", ""),
            "wlan_ac_name": params.get("wlan_ac_name", ""),
            "jsVersion": "3.3.3",
        }
        portal_url = str(portal.get("cqupt_portal_url") or DEFAULT_CONFIG["portal"]["cqupt_portal_url"])
        logging.info("Submitting CQUPT portal login for account suffix '@%s'.", isp)

        if dry_run:
            safe_fields = dict(fields)
            safe_fields["user_password"] = "***"
            logging.info("Dry run enabled; CQUPT login fields: %s", safe_fields)
            return True

        response = fetch_url(opener, portal_url, fields=fields, timeout=timeout, headers=headers)
        if not cqupt_login_result_ok(response.text):
            logging.warning("CQUPT portal response did not contain a clear success marker.")
            logging.debug("CQUPT portal response: %s", response.text[:500])

        if not bool(portal.get("verify_after_login", True)):
            return cqupt_login_result_ok(response.text)

        time.sleep(int(portal.get("verify_delay_seconds") or 3))
        online, _result = internet_is_available(opener, portal)
        if online:
            logging.info("CQUPT portal login succeeded.")
            return True

        logging.warning("Connectivity check still failed after CQUPT portal login.")
        time.sleep(retry_seconds)

    logging.error("CQUPT portal login failed after %s attempts.", attempts)
    return False


def perform_portal_login(cfg: dict[str, Any], config_path: Path, dry_run: bool = False) -> bool:
    portal = portal_config(cfg)
    if not portal.get("enabled"):
        return True

    opener = make_http_opener()
    online, _result = internet_is_available(opener, portal)
    if online:
        logging.info("Internet connectivity is already available.")
        return True

    if portal_mode(portal) == "cqupt":
        return perform_cqupt_login(cfg, config_path, opener, dry_run)

    credentials = load_portal_credentials(portal_credentials_path(cfg, config_path))
    attempts = int(portal.get("max_login_attempts") or 3)
    timeout = int(portal.get("request_timeout_seconds") or 10)
    retry_seconds = int(portal.get("retry_seconds") or 3)

    for attempt in range(1, attempts + 1):
        logging.info("Campus portal login attempt %s/%s.", attempt, attempts)
        became_online, login_page = wait_for_portal_page(opener, portal)
        if became_online:
            logging.info("Internet connectivity became available before login.")
            return True
        if login_page is None:
            raise WifiError("Campus portal login page is empty.")

        submission = build_login_submission(login_page, portal, credentials)
        masked_fields = sorted(
            field for field in submission.fields if field != submission.password_field
        )
        logging.info(
            "Submitting portal login to %s with username field '%s'. Fields: %s",
            submission.url,
            submission.username_field,
            ", ".join(masked_fields),
        )

        if dry_run:
            logging.info("Dry run enabled; portal login form was not submitted.")
            return True

        response = fetch_url(
            opener,
            submission.url,
            method=submission.method,
            fields=submission.fields,
            timeout=timeout,
        )

        failure_contains = str(portal.get("failure_contains") or "")
        if failure_contains and failure_contains in response.text:
            logging.error("Portal login response matched failure marker.")
            return False

        success_contains = str(portal.get("success_contains") or "")
        if success_contains and success_contains not in response.text:
            logging.warning("Portal login response did not include success marker.")

        if not bool(portal.get("verify_after_login", True)):
            return True

        time.sleep(int(portal.get("verify_delay_seconds") or 3))
        online, _result = internet_is_available(opener, portal)
        if online:
            logging.info("Campus portal login succeeded.")
            return True

        logging.warning("Connectivity check still failed after portal login.")
        time.sleep(retry_seconds)

    logging.error("Campus portal login failed after %s attempts.", attempts)
    return False


def parse_available_networks(output: str) -> list[str]:
    ssids: list[str] = []
    seen: set[str] = set()
    for line in output.splitlines():
        match = SSID_RE.match(line)
        if not match:
            continue
        ssid = match.group(1).strip()
        if ssid and ssid not in seen:
            ssids.append(ssid)
            seen.add(ssid)
    return ssids


def scan_networks() -> list[str]:
    result = run_netsh("wlan", "show", "networks", "mode=bssid", check=True)
    return parse_available_networks(result.stdout)


def parse_profiles(output: str) -> list[str]:
    profiles: list[str] = []
    seen: set[str] = set()
    for line in output.splitlines():
        if ":" not in line:
            continue
        left, right = line.split(":", 1)
        left_normalized = left.strip().lower()
        if not any(hint in left_normalized for hint in PROFILE_HINTS):
            continue
        name = right.strip()
        if name and name not in seen:
            profiles.append(name)
            seen.add(name)
    return profiles


def list_windows_profiles() -> list[str]:
    result = run_netsh("wlan", "show", "profiles", check=True)
    return parse_profiles(result.stdout)


def parse_status(output: str) -> dict[str, str]:
    status: dict[str, str] = {}
    for line in output.splitlines():
        if ":" not in line:
            continue
        left, right = line.split(":", 1)
        key = left.strip().lower()
        value = right.strip()
        if key in {"name", "名称", "名稱"}:
            status["interface"] = value
        elif key in {"state", "状态", "狀態"}:
            status["state"] = value
        elif key == "ssid":
            status["ssid"] = value
        elif key in {"profile", "配置文件", "設定檔"}:
            status["profile"] = value
    return status


def get_status() -> dict[str, str]:
    result = run_netsh("wlan", "show", "interfaces", check=True)
    return parse_status(result.stdout)


def is_connected(status: dict[str, str]) -> bool:
    state = status.get("state", "").strip().lower()
    if any(word in state for word in DISCONNECTED_WORDS):
        return False
    return any(word in state for word in CONNECTED_WORDS)


def enabled_networks(cfg: dict[str, Any]) -> list[dict[str, Any]]:
    networks = []
    blocked = {str(ssid).strip().lower() for ssid in cfg.get("blocked_ssids", [])}
    for raw in cfg.get("networks", []):
        if not isinstance(raw, dict):
            continue
        ssid = str(raw.get("ssid", "")).strip()
        if not ssid or raw.get("enabled") is False:
            continue
        if ssid.lower() in blocked:
            continue
        item = dict(raw)
        item["ssid"] = ssid
        item["profile"] = str(item.get("profile") or ssid).strip()
        item["priority"] = int(item.get("priority", 0))
        networks.append(item)
    return sorted(networks, key=lambda network: network["priority"], reverse=True)


def network_uses_portal(network: dict[str, Any] | None) -> bool:
    if network is None:
        return True
    return bool(network.get("portal", True))


def network_can_be_attempted(network: dict[str, Any], available: set[str]) -> bool:
    return network["ssid"] in available or bool(network.get("hidden"))


def find_configured_network(cfg: dict[str, Any], ssid: str | None) -> dict[str, Any] | None:
    if not ssid:
        return None
    for network in enabled_networks(cfg):
        if network["ssid"] == ssid:
            return network
    return None


def has_higher_priority_network(cfg: dict[str, Any], current_network: dict[str, Any]) -> bool:
    current_priority = int(current_network.get("priority", 0))
    return any(network["priority"] > current_priority for network in enabled_networks(cfg))


def choose_targets(
    cfg: dict[str, Any],
    available_ssids: list[str],
    current_status: dict[str, str],
) -> list[dict[str, Any]]:
    current_ssid = current_status.get("ssid")
    current_network = find_configured_network(cfg, current_ssid)
    current_priority = current_network["priority"] if current_network else None
    available = set(available_ssids)
    connected = is_connected(current_status)
    targets: list[dict[str, Any]] = []

    for network in enabled_networks(cfg):
        if current_ssid == network["ssid"] and connected:
            return targets
        if not network_can_be_attempted(network, available):
            continue
        if current_priority is None or network["priority"] > current_priority:
            targets.append(network)
            continue
        if connected:
            return targets

    return targets


def choose_target(
    cfg: dict[str, Any],
    available_ssids: list[str],
    current_status: dict[str, str],
) -> dict[str, Any] | None:
    targets = choose_targets(cfg, available_ssids, current_status)
    return targets[0] if targets else None


def wifi_profile_xml(
    ssid: str,
    profile_name: str,
    password: str | None,
    hidden: bool,
    auth: str,
    encryption: str,
) -> str:
    non_broadcast = "true" if hidden else "false"
    ssid_xml = escape(ssid)
    profile_xml = escape(profile_name)

    if password is None:
        security = """
    <security>
      <authEncryption>
        <authentication>open</authentication>
        <encryption>none</encryption>
        <useOneX>false</useOneX>
      </authEncryption>
    </security>"""
    else:
        security = f"""
    <security>
      <authEncryption>
        <authentication>{escape(auth)}</authentication>
        <encryption>{escape(encryption)}</encryption>
        <useOneX>false</useOneX>
      </authEncryption>
      <sharedKey>
        <keyType>passPhrase</keyType>
        <protected>false</protected>
        <keyMaterial>{escape(password)}</keyMaterial>
      </sharedKey>
    </security>"""

    return f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
  <name>{profile_xml}</name>
  <SSIDConfig>
    <SSID>
      <name>{ssid_xml}</name>
    </SSID>
    <nonBroadcast>{non_broadcast}</nonBroadcast>
  </SSIDConfig>
  <connectionType>ESS</connectionType>
  <connectionMode>auto</connectionMode>
  <MSM>{security}
  </MSM>
</WLANProfile>
"""


def install_profile(
    ssid: str,
    profile_name: str,
    password: str | None,
    hidden: bool,
    auth: str,
    encryption: str,
) -> None:
    xml = wifi_profile_xml(ssid, profile_name, password, hidden, auth, encryption)
    temp_name = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".xml",
            delete=False,
        ) as fh:
            temp_name = fh.name
            fh.write(xml)
        run_netsh("wlan", "add", "profile", f"filename={temp_name}", "user=current", check=True)
    finally:
        if temp_name:
            try:
                os.remove(temp_name)
            except OSError:
                pass


def is_existing_profile_error(exc: WifiError) -> bool:
    text = str(exc).lower()
    markers = (
        "already exists",
        "cannot overwrite",
        "无法添加配置文件",
        "具有此名称的配置文件已存在",
        "无法覆盖",
        "已存在",
    )
    return any(marker in text for marker in markers)


def update_network_config(
    cfg: dict[str, Any],
    ssid: str,
    profile: str,
    priority: int,
    hidden: bool,
    portal: bool | None = None,
) -> dict[str, Any]:
    data = {
        "ssid": ssid,
        "profile": profile,
        "priority": priority,
        "hidden": hidden,
        "enabled": True,
    }
    if portal is not None:
        data["portal"] = portal

    networks = [n for n in cfg.get("networks", []) if isinstance(n, dict)]
    updated = False
    for network in networks:
        if network.get("ssid") == ssid:
            network.update(data)
            updated = True
            break

    if not updated:
        networks.append(data)

    cfg["networks"] = sorted(
        networks,
        key=lambda network: int(network.get("priority", 0)),
        reverse=True,
    )
    return cfg


def scan_until_target(
    cfg: dict[str, Any],
    status: dict[str, str],
    wait_seconds: int,
    retry_seconds: int,
) -> tuple[list[str], list[dict[str, Any]]]:
    deadline = time.monotonic() + max(wait_seconds, 0)
    last_available: list[str] = []
    last_targets: list[dict[str, Any]] = []
    current_network = find_configured_network(cfg, status.get("ssid"))
    if current_network and is_connected(status) and not has_higher_priority_network(cfg, current_network):
        return scan_networks(), []

    while True:
        available = scan_networks()
        last_available = available
        targets = choose_targets(cfg, available, status)
        if targets:
            last_targets = targets
            best = targets[0]
            if not best.get("wait_for_higher_priority"):
                return available, targets
            higher = [
                network
                for network in enabled_networks(cfg)
                if network["priority"] > best["priority"]
                and network["ssid"] not in set(available)
            ]
            if not higher:
                return available, targets

        if time.monotonic() >= deadline:
            return last_available, last_targets

        preferred = ", ".join(network["ssid"] for network in enabled_networks(cfg))
        if targets:
            preferred = ", ".join(network["ssid"] for network in higher)
        logging.info(
            "No configured Wi-Fi found yet. Waiting %ss before scanning again. Preferred: %s",
            retry_seconds,
            preferred,
        )
        time.sleep(max(retry_seconds, 1))


def connect_to_network(
    network: dict[str, Any],
    cfg: dict[str, Any],
    dry_run: bool,
) -> bool:
    ssid = network["ssid"]
    profile = network.get("profile") or ssid
    interface = str(cfg.get("interface") or "").strip()
    timeout = int(cfg.get("connect_timeout_seconds") or 20)

    command = ["wlan", "connect", f"name={profile}", f"ssid={ssid}"]
    if interface:
        command.append(f"interface={interface}")

    if dry_run:
        logging.info("Would connect to SSID '%s' using profile '%s'.", ssid, profile)
        return True

    if cfg.get("disconnect_before_connect"):
        disconnect_args = ["wlan", "disconnect"]
        if interface:
            disconnect_args.append(f"interface={interface}")
        run_netsh(*disconnect_args)
        time.sleep(1)

    result = run_netsh(*command)
    if result.returncode != 0:
        logging.error(
            "Connect command failed for SSID '%s': %s",
            ssid,
            (result.stderr or result.stdout).strip(),
        )
        return False

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        status = get_status()
        if status.get("ssid") == ssid and is_connected(status):
            logging.info("Connected to SSID '%s'.", ssid)
            return True
        time.sleep(1)

    logging.warning("Timed out waiting for SSID '%s' to connect.", ssid)
    return False


def run_once(cfg: dict[str, Any], config_path: Path, dry_run: bool) -> bool:
    status = get_status()
    current_ssid = status.get("ssid") or "(none)"
    current_network = find_configured_network(cfg, status.get("ssid"))
    active_network = current_network
    logging.info("Current SSID: %s", current_ssid)
    scan_wait_seconds = int(cfg.get("scan_wait_seconds") or 0)
    scan_retry_seconds = int(cfg.get("scan_retry_seconds") or 5)
    available, targets = scan_until_target(cfg, status, scan_wait_seconds, scan_retry_seconds)
    logging.debug("Available SSIDs: %s", ", ".join(available) or "(none)")

    wifi_ready = is_connected(status)

    if targets:
        wifi_ready = False
        for target in targets:
            logging.info(
                "Selected SSID '%s' with priority %s.",
                target["ssid"],
                target.get("priority", 0),
            )
            wifi_ready = connect_to_network(target, cfg, dry_run=dry_run)
            if wifi_ready:
                active_network = target
                break
            logging.warning("Could not connect to SSID '%s'; trying next visible candidate.", target["ssid"])
    else:
        logging.info("No Wi-Fi network change needed.")

    if not targets and current_network is None:
        logging.warning(
            "Not connected to a configured Wi-Fi and no configured SSID was found before timeout."
        )
        return False

    if not wifi_ready:
        return False

    if portal_enabled(cfg):
        if network_uses_portal(active_network):
            if not perform_portal_login(cfg, config_path, dry_run=dry_run):
                return False
            if dry_run:
                return True
            return verify_internet_connectivity(cfg)
        active_ssid = active_network.get("ssid") if active_network else current_ssid
        logging.info("Skipping campus portal login for SSID '%s'.", active_ssid)

    if dry_run:
        return True
    return verify_internet_connectivity(cfg)


def command_init(args: argparse.Namespace) -> int:
    init_config(args.config, args.force)
    print(f"Created config: {args.config}")
    return 0


def command_add(args: argparse.Namespace) -> int:
    cfg = load_config(args.config) if args.config.exists() else default_config()
    profile = args.profile or args.ssid

    if args.open and args.ask_password:
        raise WifiError("Use either --open or --ask-password, not both.")
    if args.portal and args.no_portal:
        raise WifiError("Use either --portal or --no-portal, not both.")

    if args.ask_password:
        password = getpass.getpass(f"Password for {args.ssid}: ")
        if len(password) < 8:
            raise WifiError("WPA/WPA2 passphrases must be at least 8 characters.")
        try:
            install_profile(args.ssid, profile, password, args.hidden, args.auth, args.encryption)
            print(f"Installed Windows Wi-Fi profile: {profile}")
        except WifiError as exc:
            if not is_existing_profile_error(exc):
                raise
            print(
                f"Windows Wi-Fi profile already exists: {profile}. "
                "Reusing it without overwriting.",
                file=sys.stderr,
            )
    elif args.open:
        try:
            install_profile(args.ssid, profile, None, args.hidden, args.auth, args.encryption)
            print(f"Installed open Windows Wi-Fi profile: {profile}")
        except WifiError as exc:
            if not is_existing_profile_error(exc):
                raise
            print(
                f"Windows Wi-Fi profile already exists: {profile}. "
                "Reusing it without overwriting.",
                file=sys.stderr,
            )
    elif profile not in list_windows_profiles():
        print(
            "Warning: this Windows Wi-Fi profile does not exist yet. "
            "Use --ask-password, --open, or connect once through Windows settings.",
            file=sys.stderr,
        )

    portal = None
    if args.portal:
        portal = True
    elif args.no_portal:
        portal = False

    cfg = update_network_config(
        cfg,
        args.ssid,
        profile,
        args.priority,
        args.hidden,
        portal=portal,
    )
    if args.portal:
        cfg.setdefault("portal", default_config()["portal"])
        cfg["portal"]["enabled"] = True
    write_config(args.config, cfg)
    print(f"Saved network '{args.ssid}' in {args.config}")
    return 0


def command_list(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    networks = enabled_networks(cfg)
    if not networks:
        print("No enabled networks configured.")
        return 0
    for index, network in enumerate(networks, start=1):
        hidden = " hidden" if network.get("hidden") else ""
        portal = " portal" if network_uses_portal(network) else " no-portal"
        print(
            f"{index}. priority={network['priority']} "
            f"ssid={network['ssid']!r} profile={network['profile']!r}"
            f"{hidden}{portal}"
        )
    return 0


def command_scan(_: argparse.Namespace) -> int:
    for ssid in scan_networks():
        print(ssid)
    return 0


def command_status(_: argparse.Namespace) -> int:
    status = get_status()
    if not status:
        print("No Wi-Fi interface status returned.")
        return 1
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0


def command_credentials(args: argparse.Namespace) -> int:
    cfg = load_config(args.config) if args.config.exists() else default_config()
    password = args.password
    if password is None:
        password = getpass.getpass("Campus portal password: ")

    cred_path = portal_credentials_path(cfg, args.config)
    save_portal_credentials(cred_path, args.username, password, isp=args.isp or "")

    if args.enable_portal or args.isp or args.mode:
        cfg.setdefault("portal", default_config()["portal"])
    if args.mode:
        cfg["portal"]["mode"] = args.mode
    if args.isp:
        cfg["portal"]["isp"] = normalize_isp(args.isp)
    if args.enable_portal:
        cfg["portal"]["enabled"] = True
        write_config(args.config, cfg)
    elif args.isp or args.mode:
        write_config(args.config, cfg)

    print(f"Saved encrypted campus portal credentials: {cred_path}")
    return 0


def command_login(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    setup_logging(cfg, args.config, args.verbose)
    return 0 if perform_portal_login(cfg, args.config, dry_run=args.dry_run) else 2


def command_run(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    if args.interval is not None:
        cfg["interval_seconds"] = args.interval
    setup_logging(cfg, args.config, args.verbose)

    if args.once:
        return 0 if run_once(cfg, args.config, args.dry_run) else 2

    interval = int(cfg.get("interval_seconds") or 30)
    logging.info("Auto Wi-Fi connector started. Interval: %ss", interval)
    try:
        while True:
            run_once(cfg, args.config, args.dry_run)
            time.sleep(interval)
    except KeyboardInterrupt:
        logging.info("Stopped by user.")
        return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Auto-connect this Windows machine to preferred Wi-Fi networks.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("wifi_config.json"),
        help="Path to the JSON config file.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create a starter config file.")
    init_parser.add_argument("--force", action="store_true", help="Overwrite an existing config.")
    init_parser.set_defaults(func=command_init)

    add_parser = subparsers.add_parser("add", help="Add or update a preferred Wi-Fi network.")
    add_parser.add_argument("ssid", help="Wi-Fi SSID to prefer.")
    add_parser.add_argument("--profile", help="Windows Wi-Fi profile name. Defaults to SSID.")
    add_parser.add_argument("--priority", type=int, default=100, help="Higher wins.")
    add_parser.add_argument("--hidden", action="store_true", help="Mark this SSID as hidden.")
    add_parser.add_argument("--portal", action="store_true", help="Enable campus portal login.")
    add_parser.add_argument(
        "--no-portal",
        action="store_true",
        help="Skip campus portal login for this SSID.",
    )
    add_parser.add_argument("--open", action="store_true", help="Create an open-network profile.")
    add_parser.add_argument(
        "--ask-password",
        action="store_true",
        help="Prompt once and create a Windows WPA/WPA2 profile.",
    )
    add_parser.add_argument("--auth", default="WPA2PSK", help="Profile authentication mode.")
    add_parser.add_argument("--encryption", default="AES", help="Profile encryption mode.")
    add_parser.set_defaults(func=command_add)

    list_parser = subparsers.add_parser("list", help="List configured preferred networks.")
    list_parser.set_defaults(func=command_list)

    scan_parser = subparsers.add_parser("scan", help="Print visible Wi-Fi SSIDs.")
    scan_parser.set_defaults(func=command_scan)

    status_parser = subparsers.add_parser("status", help="Print current Wi-Fi interface status.")
    status_parser.set_defaults(func=command_status)

    credentials_parser = subparsers.add_parser(
        "credentials",
        help="Save encrypted campus portal credentials for this Windows user.",
    )
    credentials_parser.add_argument("--username", required=True, help="Campus portal username.")
    credentials_parser.add_argument(
        "--password",
        help="Campus portal password. Omit this to type it securely.",
    )
    credentials_parser.add_argument(
        "--isp",
        help="Campus operator/ISP, for example unicom, cmcc, telecom, xyw, or 联通.",
    )
    credentials_parser.add_argument(
        "--mode",
        choices=["generic", "cqupt"],
        help="Portal login mode to save in the config.",
    )
    credentials_parser.add_argument(
        "--enable-portal",
        action="store_true",
        help="Also enable portal login in the config.",
    )
    credentials_parser.set_defaults(func=command_credentials)

    login_parser = subparsers.add_parser("login", help="Run campus portal login only.")
    login_parser.add_argument("--dry-run", action="store_true", help="Do not submit the form.")
    login_parser.add_argument("--verbose", action="store_true", help="Enable debug logs.")
    login_parser.set_defaults(func=command_login)

    run_parser = subparsers.add_parser("run", help="Run the auto-connect loop.")
    run_parser.add_argument("--once", action="store_true", help="Run one scan/connect cycle.")
    run_parser.add_argument("--dry-run", action="store_true", help="Log the chosen action only.")
    run_parser.add_argument("--verbose", action="store_true", help="Enable debug logs.")
    run_parser.add_argument("--interval", type=int, help="Override interval_seconds.")
    run_parser.set_defaults(func=command_run)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except WifiError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON config: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
