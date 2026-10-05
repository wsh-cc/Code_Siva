from server.app import DEFAULT_HOST, build_arg_parser as build_server_arg_parser
from server.network import ALL_INTERFACES_HOST, endpoint_hints, resolve_bind_host
from web_client.server import DEFAULT_WEB_HOST, build_arg_parser as build_web_arg_parser


def test_resolve_bind_host_defaults_to_localhost() -> None:
    assert resolve_bind_host(None, lan=False, default_host=DEFAULT_HOST) == "127.0.0.1"


def test_resolve_bind_host_uses_all_interfaces_for_lan_mode() -> None:
    assert resolve_bind_host(None, lan=True, default_host=DEFAULT_HOST) == ALL_INTERFACES_HOST


def test_resolve_bind_host_keeps_explicit_host() -> None:
    assert resolve_bind_host("192.168.1.20", lan=True, default_host=DEFAULT_HOST) == "192.168.1.20"


def test_endpoint_hints_include_local_and_lan_urls() -> None:
    hints = endpoint_hints(ALL_INTERFACES_HOST, 8080, scheme="http", lan_addresses=["192.168.1.20"])

    assert hints["local"] == ["http://127.0.0.1:8080"]
    assert hints["lan"] == ["http://192.168.1.20:8080"]


def test_server_lan_arg_switches_default_bind_host() -> None:
    args = build_server_arg_parser().parse_args(["--lan"])

    assert resolve_bind_host(args.host, args.lan, DEFAULT_HOST) == ALL_INTERFACES_HOST


def test_web_lan_arg_switches_default_bind_host() -> None:
    args = build_web_arg_parser().parse_args(["--lan"])

    assert resolve_bind_host(args.host, args.lan, DEFAULT_WEB_HOST) == ALL_INTERFACES_HOST
