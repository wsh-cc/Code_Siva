# OCHAT 使用说明

这份说明主要记录 OCHAT 在本机如何跑起来，以及演示时可以按什么顺序操作。项目现在有两种客户端：一个是 Tkinter 桌面端，一个是浏览器 Web 端。两者访问的是同一个聊天服务端，注册、登录、好友、群聊、文件和历史消息这些数据也是共用的。

## 运行前准备

先安装依赖：

```powershell
python -m pip install -r requirements.txt
```

可以顺手检查一下本机环境：

```powershell
python tools/check_env.py
```

如果只是演示功能，建议先用 SQLite。它不需要单独配置数据库，启动后会在 `database/ochat.db` 里保存数据。

## 启动服务端

快速启动：

```powershell
python start_server.py
```

上面这条命令默认使用 SQLite，监听地址是 `127.0.0.1:8765`。

需要明确指定参数时，使用完整写法：

```powershell
python start_server.py --host 127.0.0.1 --port 8765 --db-backend sqlite --db database/ochat.db
```

如果要连接 MySQL，需要先确认 MySQL 服务已经启动，再传入账号和密码：

```powershell
python start_server.py --db-backend mysql --mysql-host 127.0.0.1 --mysql-port 3306 --mysql-user root --mysql-password 你的密码 --mysql-database ochat
```

## 启动客户端

桌面端：

```powershell
python start_client.py --host 127.0.0.1 --port 8765
```

Web 端：

```powershell
python start_web_client.py --host 127.0.0.1 --port 8080 --chat-host 127.0.0.1 --chat-port 8765
```

然后在浏览器打开：

```text
http://127.0.0.1:8080
```

Web 端中间多了一层本地 HTTP 桥接服务。浏览器先访问这个桥接服务，桥接服务再连接 OCHAT TCP 服务端，所以 `--chat-port` 要和服务端端口保持一致。

## 基本演示流程

1. 启动服务端。
2. 打开两个客户端，可以是两个桌面端，也可以是两个浏览器会话。
3. 注册两个账号，例如 `alice_1` 和 `bob_1`，密码至少 6 位。
4. 两个账号分别登录。
5. Alice 搜索 Bob，并发送好友申请。
6. Bob 在申请列表中同意。
7. 进入私聊窗口，互相发送文本消息。
8. Alice 创建群聊，邀请 Bob 加入。
9. Bob 同意群聊邀请后，在群里发送消息。
10. 发送一张图片，检查聊天窗口中是否能显示预览。
11. 发送一个文件，再使用下载或保存功能取回文件。
12. 使用搜索消息、撤回消息、修改资料、查看群成员等功能补充演示。

## 文件说明

上传的文件默认保存在：

```text
database/uploads/
```

系统允许常见文档、图片和 zip 压缩包，单个文件最大 10 MB。文件内容不直接放进数据库，数据库只保存文件名、大小、类型和上传者等信息。

## 常见问题

服务端启动失败时，先检查端口是否被占用。如果 `8765` 已经被别的程序使用，可以换一个端口，同时客户端也要改成相同端口。

Web 页面能打开但登录失败时，通常是 Web 桥接服务没有连上 TCP 服务端。确认 `start_server.py` 已经启动，并且 `start_web_client.py` 的 `--chat-host` 和 `--chat-port` 填对了。

MySQL 模式连接失败时，可以先切回 SQLite 模式完成演示。SQLite 模式不影响功能流程，只是数据库换成本地文件。

文件上传失败时，检查文件后缀和大小。系统会在服务端再次校验，不能只靠客户端判断。
