import copy
import unittest
from pathlib import Path
from unittest.mock import patch

from auto_wifi import (
    FetchResult,
    build_login_submission,
    choose_target,
    choose_targets,
    cqupt_account,
    deep_update,
    dpapi_decrypt_error,
    default_config,
    has_higher_priority_network,
    is_connected,
    is_existing_profile_error,
    network_uses_portal,
    normalize_isp,
    parse_cqupt_params,
    parse_available_networks,
    parse_profiles,
    parse_status,
    run_once,
    WifiError,
)


class NetshParsingTests(unittest.TestCase):
    def test_parse_available_networks(self):
        output = """
SSID 1 : HomeWiFi
    Network type            : Infrastructure
SSID 2 : OfficeWiFi
SSID 3 :
SSID 4 : HomeWiFi
"""
        self.assertEqual(parse_available_networks(output), ["HomeWiFi", "OfficeWiFi"])

    def test_parse_profiles_with_chinese_output(self):
        output = """
    所有用户配置文件 : HomeWiFi
    所有用户配置文件 : OfficeWiFi
"""
        self.assertEqual(parse_profiles(output), ["HomeWiFi", "OfficeWiFi"])

    def test_parse_status_with_chinese_output(self):
        output = """
    名称                   : WLAN
    状态                   : 已连接
    SSID                   : HomeWiFi
"""
        status = parse_status(output)

        self.assertEqual(status["interface"], "WLAN")
        self.assertEqual(status["ssid"], "HomeWiFi")
        self.assertTrue(is_connected(status))

    def test_existing_profile_error_is_reusable(self):
        exc = WifiError(
            "无法添加配置文件“HONOR GT”。"
            "具有此名称的配置文件已存在于组策略或其他用户范围内，且无法覆盖。"
        )

        self.assertTrue(is_existing_profile_error(exc))

    def test_dpapi_decrypt_error_suggests_resaving_credentials(self):
        exc = dpapi_decrypt_error(-2146893813)

        self.assertIn("Windows error -2146893813", str(exc))
        self.assertIn("credentials", str(exc))


class TargetSelectionTests(unittest.TestCase):
    def test_selects_higher_priority_visible_network(self):
        cfg = {
            "networks": [
                {"ssid": "HomeWiFi", "priority": 100, "enabled": True},
                {"ssid": "OfficeWiFi", "priority": 80, "enabled": True},
            ]
        }
        status = {"ssid": "OfficeWiFi", "state": "connected"}

        target = choose_target(cfg, ["HomeWiFi", "OfficeWiFi"], status)

        self.assertEqual(target["ssid"], "HomeWiFi")

    def test_stays_on_current_when_no_better_network_is_visible(self):
        cfg = {
            "networks": [
                {"ssid": "HomeWiFi", "priority": 100, "enabled": True},
                {"ssid": "OfficeWiFi", "priority": 80, "enabled": True},
            ]
        }
        status = {"ssid": "OfficeWiFi", "state": "connected"}

        target = choose_target(cfg, ["OfficeWiFi"], status)

        self.assertIsNone(target)

    def test_user_priority_rule_prefers_hotspot_then_campus_5g_then_cqupt(self):
        cfg = {
            "blocked_ssids": ["CQUPT2.4G"],
            "networks": [
                {"ssid": "HONOR GT", "priority": 300, "enabled": True, "portal": False},
                {
                    "ssid": "CQUPT-5G",
                    "priority": 200,
                    "enabled": True,
                    "portal": True,
                },
                {"ssid": "CQUPT", "priority": 100, "enabled": True, "portal": True},
            ]
        }

        target = choose_target(cfg, ["CQUPT", "HONOR GT", "CQUPT-5G"], {})

        self.assertEqual(target["ssid"], "HONOR GT")
        self.assertFalse(network_uses_portal(target))

        target = choose_target(cfg, ["CQUPT", "CQUPT-5G"], {})

        self.assertEqual(target["ssid"], "CQUPT-5G")
        self.assertTrue(network_uses_portal(target))

        target = choose_target(cfg, ["CQUPT"], {})

        self.assertEqual(target["ssid"], "CQUPT")
        self.assertTrue(network_uses_portal(target))

    def test_cqupt_is_allowed_but_cqupt_24g_is_blocked(self):
        cfg = {
            "blocked_ssids": ["CQUPT2.4G"],
            "networks": [
                {"ssid": "HONOR GT", "priority": 300, "enabled": True, "portal": False},
                {
                    "ssid": "CQUPT-5G",
                    "priority": 200,
                    "enabled": True,
                    "portal": True,
                },
                {"ssid": "CQUPT", "priority": 100, "enabled": True, "portal": True},
                {"ssid": "CQUPT2.4G", "priority": 90, "enabled": True, "portal": True},
            ]
        }

        targets = choose_targets(cfg, ["CQUPT2.4G"], {})

        self.assertEqual(targets, [])

        targets = choose_targets(cfg, ["CQUPT"], {})

        self.assertEqual([target["ssid"] for target in targets], ["CQUPT"])

    def test_highest_priority_network_does_not_wait_for_more_candidates(self):
        cfg = {
            "networks": [
                {"ssid": "HONOR GT", "priority": 300, "enabled": True, "portal": False},
                {"ssid": "CQUPT-5G", "priority": 200, "enabled": True, "portal": True},
            ]
        }
        current = {"ssid": "HONOR GT", "priority": 300, "enabled": True, "portal": False}

        self.assertFalse(has_higher_priority_network(cfg, current))


class RunOnceConnectivityTests(unittest.TestCase):
    def test_connected_wifi_without_internet_is_not_success(self):
        cfg = {
            "scan_wait_seconds": 0,
            "scan_retry_seconds": 1,
            "networks": [
                {"ssid": "HONOR GT", "priority": 300, "enabled": True, "portal": False}
            ],
            "portal": {"enabled": False},
        }
        status = {"ssid": "HONOR GT", "state": "connected"}

        with (
            patch("auto_wifi.get_status", return_value=status),
            patch("auto_wifi.scan_until_target", return_value=(["HONOR GT"], [])),
            patch("auto_wifi.make_http_opener", return_value=object()),
            patch("auto_wifi.internet_is_available", return_value=(False, None)),
        ):
            self.assertFalse(run_once(cfg, Path("wifi_config.json"), dry_run=False))

    def test_connected_wifi_succeeds_when_internet_is_available(self):
        cfg = {
            "scan_wait_seconds": 0,
            "scan_retry_seconds": 1,
            "networks": [
                {"ssid": "HONOR GT", "priority": 300, "enabled": True, "portal": False}
            ],
            "portal": {"enabled": False},
        }
        status = {"ssid": "HONOR GT", "state": "connected"}
        check_result = FetchResult(status=200, url="http://check.example", text="ok", headers={})

        with (
            patch("auto_wifi.get_status", return_value=status),
            patch("auto_wifi.scan_until_target", return_value=(["HONOR GT"], [])),
            patch("auto_wifi.make_http_opener", return_value=object()),
            patch("auto_wifi.internet_is_available", return_value=(True, check_result)),
        ):
            self.assertTrue(run_once(cfg, Path("wifi_config.json"), dry_run=False))


class PortalLoginTests(unittest.TestCase):
    def test_build_login_submission_uses_form_action_and_hidden_fields(self):
        page = FetchResult(
            status=200,
            url="http://portal.example.edu/index.html",
            text="""
<form action="/login" method="post">
  <input type="hidden" name="service" value="internet">
  <input type="text" name="userId">
  <input type="password" name="userPassword">
</form>
""",
            headers={},
        )
        portal = {"extra_fields": {"operator": "campus"}}
        credentials = {"username": "student01", "password": "secret"}

        submission = build_login_submission(page, portal, credentials)

        self.assertEqual(submission.url, "http://portal.example.edu/login")
        self.assertEqual(submission.method, "POST")
        self.assertEqual(submission.username_field, "userId")
        self.assertEqual(submission.password_field, "userPassword")
        self.assertEqual(submission.fields["service"], "internet")
        self.assertEqual(submission.fields["operator"], "campus")
        self.assertEqual(submission.fields["userId"], "student01")
        self.assertEqual(submission.fields["userPassword"], "secret")

    def test_config_deep_update_keeps_portal_defaults(self):
        cfg = deep_update(copy.deepcopy(default_config()), {"portal": {"enabled": True}})

        self.assertTrue(cfg["portal"]["enabled"])
        self.assertIn("connectivity_check_url", cfg["portal"])
        self.assertIn("request_timeout_seconds", cfg["portal"])

    def test_cqupt_account_uses_unicom_suffix(self):
        self.assertEqual(normalize_isp("联通"), "unicom")
        self.assertEqual(cqupt_account("1693070", "联通"), ",0,1693070@unicom")

    def test_parse_cqupt_redirect_params(self):
        result = FetchResult(
            status=200,
            url=(
                "http://192.168.200.2/a79.htm?wlanuserip=10.17.21.13"
                "&wlanacname=NE40E-X16A&wlanacip=192.168.200.1"
                "&mac=60:45:2e:14:26:1b"
            ),
            text="",
            headers={},
        )

        params = parse_cqupt_params(result)

        self.assertEqual(params["wlan_user_ip"], "10.17.21.13")
        self.assertEqual(params["wlan_ac_name"], "NE40E-X16A")
        self.assertEqual(params["wlan_ac_ip"], "192.168.200.1")
        self.assertEqual(params["wlan_user_mac"], "60452e14261b")


if __name__ == "__main__":
    unittest.main()
