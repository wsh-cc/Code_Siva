# OCHAT 使用说明

OCHAT 是一个 Python 课程项目聊天系统，包含多线程 TCP 服务端、Tkinter 桌面客户端、MySQL 数据持久化、密码哈希、好友管理、私聊、群聊、消息历史、消息搜索、消息撤回、文件/图片上传和文件保存。

## 运行

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

检查运行环境：

```powershell
python tools/check_env.py
```

确认 MySQL 服务正在运行。当前机器检测到 MySQL 服务名为 `MySQL97`，状态是 `Running`。

启动服务端：

```powershell
python start_server.py --host 127.0.0.1 --port 8765 --mysql-user root --mysql-password 你的MySQL密码
```

在另一个终端启动客户端：

```powershell
python start_client.py --host 127.0.0.1 --port 8765
```

上传的文件会保存到 `database/uploads/`。

如果只是快速演示，不想连接 MySQL，可以使用 SQLite 备用模式：

```powershell
python start_server.py --db-backend sqlite --db database/ochat.db
```

## 演示流程

1. 启动服务端。
2. 打开两个客户端窗口。
3. 分别注册 `alice_1` 和 `bob_1`，密码至少 6 位。
4. 两个用户分别登录。
5. 在 Alice 客户端添加 `bob_1` 为好友。
6. 选择 Bob，发送私聊消息。
7. Alice 创建群聊，邀请 `bob_1`，然后发送群聊消息。
8. 使用“文件/图片”按钮发送允许类型的文件。
9. 使用“保存文件”按钮保存当前聊天中最新的文件。
10. 使用“撤回”按钮撤回当前聊天中自己最后发送的消息。
11. 使用“搜索消息”查看历史消息。

## 安全设计

- 密码使用 PBKDF2-SHA256 和随机盐保存。
- 用户名、昵称、签名、联系方式等字段在服务端校验。
- MySQL 和 SQLite 操作都使用参数化查询。
- 文件上传限制常见文档、图片、压缩包后缀，大小限制 10 MB。
- 群聊邀请、移除成员、发群消息都会在服务端检查权限。
- 未登录用户不能访问好友、聊天、文件等核心功能。
