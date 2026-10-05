"""Network helpers for LAN-friendly OCHAT startup."""

from __future__ import annotations

import ipaddress
import socket


ALL_INTERFACES_HOST = "0.0.0.0"
LOCALHOST = "127.0.0.1"


def resolve_bind_host(explicit_host: str | None, lan: bool, default_host: str = LOCALHOST) -> str:
    """Return the host a service should bind to."""
    host = (explicit_host or "").strip()
    if host:
        return host
    return ALL_INTERFACES_HOST if lan else default_host


def local_lan_ipv4_addresses() -> list[str]:
    """Best-effort list of non-loopback IPv4 addresses for user-facing hints."""
    candidates: list[str] = []

    try:
        hostname = socket.gethostname()
        for item in socket.getaddrinfo(hostname, None, socket.AF_INET, socket.SOCK_STREAM):
            candidates.append(str(item[4][0]))
    except OSError:
        pass

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.connect(("8.8.8.8", 80))
            candidates.append(str(probe.getsockname()[0]))
    except OSError:
        pass

    result: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        try:
            address = ipaddress.ip_address(candidate)
        except ValueError:
            continue
        if address.version != 4 or address.is_loopback or address.is_unspecified or address.is_link_local:
            continue
        if candidate not in seen:
            seen.add(candidate)
            result.append(candidate)
    return result


def endpoint_hints(
    bind_host: str,
    port: int,
    *,
    scheme: str | None = None,
    lan_addresses: list[str] | None = None,
) -> dict[str, list[str]]:
    """Build local and LAN endpoints to print after startup."""
    host = bind_host.strip() or ALL_INTERFACES_HOST
    lan_mode = host in {ALL_INTERFACES_HOST, "::"}
    local_host = LOCALHOST if lan_mode else host
    local = [_format_endpoint(local_host, port, scheme)]

    lan: list[str] = []
    if lan_mode:
        for address in lan_addresses if lan_addresses is not None else local_lan_ipv4_addresses():
            lan.append(_format_endpoint(address, port, scheme))
    return {"local": local, "lan": lan}


def _format_endpoint(host: str, port: int, scheme: str | None) -> str:
    value = f"{host}:{port}"
    return f"{scheme}://{value}" if scheme else value
