# Auto Wi-Fi Connector

这是一个 Windows/Python 自动联网小系统：先连接指定 WiFi，再处理校园网
Captive Portal 网页认证，自动提交校园网账号密码，最后用连通性检测确认外网可用。

它只会连接你配置的网络，并提交你保存的校园网账号密码；不会破解、恢复或猜测
WiFi 密码。

## 环境要求

- Windows
- Python 3.9+
- 一块 Windows 可识别的无线网卡

## 校园网快速配置

当前默认规则已经写入 `wifi_config.json`：

- 优先连接 `HONOR GT`，连上后不执行校园网网页登录。
- 如果没有 `HONOR GT`，等待并优先连接扫描到的 `CQUPT-5G`；连上后执行校园网网页登录。
- 如果没有 `CQUPT-5G`，连接 `CQUPT`，连上后执行校园网网页登录。
- 明确禁止连接 `CQUPT2.4G`。
- 程序只会连接配置里的 SSID；超过 `scan_wait_seconds` 仍找不到配置网络，就退出本轮检索。

## 一键运行

双击项目根目录里的这个文件即可后台自动连接一次，不显示黑窗口：

```text
run_auto_wifi.vbs
```

它会自动使用 `E:\python312\python.exe`，必要时弹出管理员权限确认，然后在后台执行：

```powershell
.\auto_wifi.py run --once --verbose
```

如果你想让它一直后台循环检测连接，双击：

```text
run_auto_wifi_loop.vbs
```

如果连接失败，需要看到窗口和输出，双击调试入口：

```text
run_auto_wifi_debug.bat
```

## 开机自启动

双击安装登录后后台自启动：

```text
install_autostart.bat
```

它会注册一个 Windows 计划任务 `AutoWiFiConnector`，当前用户登录后自动后台运行，
并持续循环检测连接。

卸载自启动：

```text
uninstall_autostart.bat
```

也可以用命令安装：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_task.ps1
```

如果这些 WiFi 配置已经存在于 Windows，直接保存校园网账号密码并运行：

```powershell
python .\auto_wifi.py credentials --username "你的学号或账号" --isp unicom --mode cqupt --enable-portal
python .\auto_wifi.py run --once --verbose
```

如果 `HONOR GT` 还没有在 Windows 里保存过密码，请先手动连一次，或用
Windows 设置保存它的 WiFi 密码。程序不会猜测或破解热点密码。

如果校园 WiFi 是开放网络，先添加 SSID，并启用门户登录：

```powershell
python .\auto_wifi.py add "校园网SSID" --open --portal --priority 100
```

如果校园 WiFi 本身也有 WiFi 密码：

```powershell
python .\auto_wifi.py add "校园网SSID" --ask-password --portal --priority 100
```

如果你已经在 Windows 里手动连过这个 WiFi，直接登记 SSID 即可：

```powershell
python .\auto_wifi.py add "校园网SSID" --portal --priority 100
```

保存校园网网页登录账号密码。密码会用 Windows DPAPI 加密，只能由当前
Windows 用户解密：

```powershell
python .\auto_wifi.py credentials --username "你的学号或账号" --enable-portal
```

先只测试网页登录认证：

```powershell
python .\auto_wifi.py login --dry-run --verbose
python .\auto_wifi.py login --verbose
```

再测试完整流程：

```powershell
python .\auto_wifi.py run --once --verbose
```

测试成功后，安装为登录 Windows 后自动运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_task.ps1
```

卸载自动运行任务：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\uninstall_task.ps1
```

## 门户页面适配

默认会请求：

```text
http://www.msftconnecttest.com/connecttest.txt
```

如果没认证成功，校园网通常会把这个请求重定向或替换成登录页。程序会尝试
解析登录页里的 `<form>`，自动识别用户名和密码输入框，并保留隐藏字段。

CQUPT 当前观察到的跳转页面类似：

```text
http://192.168.200.2/a79.htm?wlanuserip=...&wlanacname=...&wlanacip=...&mac=...
```

这些查询参数包含本机当次连接的 IP、AC 和 MAC 信息，可能每次变化，所以程序默认
不把它写死，而是使用实际被重定向后的 URL。

CQUPT 模式会把运营商转换成接口需要的后缀，例如联通会提交为：

```text
,0,账号@unicom
```

可用运营商值：`unicom`/`联通`、`cmcc`/`移动`、`telecom`/`电信`、`xyw`/`校园网`。

如果你的学校字段名比较特殊，编辑 `wifi_config.json` 里的 `portal`：

```json
{
  "portal": {
    "enabled": true,
    "login_url": "",
    "method": "",
    "username_field": "",
    "password_field": "",
    "extra_fields": {},
    "success_contains": "",
    "failure_contains": ""
  }
}
```

常见需要改的字段：

- `login_url`：学校固定登录接口地址；留空则使用被拦截后的页面表单地址。
- `username_field`：账号输入框的 `name`，比如 `username`、`userId`、`DDDDD`。
- `password_field`：密码输入框的 `name`，比如 `password`、`upass`。
- `extra_fields`：学校要求一起提交的隐藏参数或运营商字段。
- `success_contains`：登录成功页面会出现的文字。
- `failure_contains`：登录失败页面会出现的文字。

如果学校页面需要验证码、短信验证、复杂 JavaScript 加密或动态 token，请把登录页
HTML 或浏览器开发者工具里的 Network 登录请求发给我，我可以继续给这个系统加
专门适配器。

## 常用命令

```powershell
python .\auto_wifi.py scan
python .\auto_wifi.py status
python .\auto_wifi.py list
python .\auto_wifi.py login --verbose
python .\auto_wifi.py run --dry-run --once
python .\auto_wifi.py run
```

## 配置文件

默认配置文件是 `wifi_config.json`。多个 WiFi 同时可见时，`priority` 数值越高
越优先。

如果电脑有多个无线网卡，把 `interface` 设置成 `python .\auto_wifi.py status`
里显示的网卡名称。
