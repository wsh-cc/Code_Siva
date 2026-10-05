# OCHAT 上线部署说明

这份说明面向真正上线运行，而不是本机演示。上线形态建议是：

- 浏览器用户只访问 Web 服务。
- TCP 聊天服务只暴露在内网或 Docker 网络中。
- 数据使用 MySQL 持久化。
- 上传文件目录单独挂载 volume，并纳入备份。
- 公网入口放在 Nginx、HTTPS 证书或云负载均衡之后。

## 生产模式

Web 服务上线时必须开启生产模式：

```powershell
python start_web_client.py --host 0.0.0.0 --port 8080 --chat-host 127.0.0.1 --chat-port 8765 --production
```

生产模式会做这些限制：

- 禁止浏览器端修改后端 TCP 服务地址。
- 给 HTTP 响应增加基础安全头。
- Web 会话 Cookie 增加 `HttpOnly`。
- 支持 `OCHAT_ALLOWED_ORIGINS` 限制浏览器 POST 请求来源。
- 提供 `/healthz` 和 `/readyz` 给容器、反向代理或云平台探活。

## Docker Compose 部署

推荐先用仓库里的 `deploy/docker-compose.yml` 启动一套可上线的基础环境：

```powershell
cd deploy
docker compose up -d --build
```

第一次上线前，至少设置这些环境变量：

```powershell
$env:MYSQL_ROOT_PASSWORD="换成强密码"
$env:OCHAT_DB_PASSWORD="换成强密码"
$env:OCHAT_ALLOWED_ORIGINS="https://你的域名"
$env:OCHAT_SECURE_COOKIES="true"
docker compose up -d --build
```

默认只把 Web 端口暴露到宿主机：

```text
http://服务器IP:8080
```

如果前面有 Nginx 或 HTTPS 网关，把外部域名写进 `OCHAT_ALLOWED_ORIGINS`。例如：

```text
OCHAT_ALLOWED_ORIGINS=https://chat.example.com
```

## 健康检查

Web 存活检查：

```text
GET /healthz
```

Web 就绪检查，会同时检查后端 TCP 聊天服务：

```text
GET /readyz
```

返回 `ok: true` 才表示 Web 服务和聊天服务都可用。

## 反向代理

`deploy/nginx.conf` 提供了基础反向代理示例。正式上线时建议：

- 在 Nginx 或云负载均衡上终止 HTTPS。
- 把 `client_max_body_size` 保持在 20 MB 左右，匹配系统 10 MB 文件上传限制和 base64 开销。
- 不要把 `chat-server:8765` 直接映射到公网。

## 持久化和备份

需要备份两类数据：

- MySQL 数据库：用户、好友、群聊、消息、文件元数据。
- `uploads` volume：真实上传文件。

只备份数据库不够，文件消息会丢失内容；只备份文件也不够，聊天记录和权限关系会丢失。

## 当前上线边界

这次改造让 OCHAT 具备基础上线形态，但还不是大型商业 IM 架构。后续如果要继续扩展，应优先做：

- 把长轮询升级为 WebSocket。
- 把会话 token 持久化并增加过期时间。
- 增加注册限流、登录失败限流和审计日志。
- 文件上传改为对象存储。
- 增加管理员后台和用户封禁能力。
- 多实例部署时把在线状态和消息推送迁移到 Redis 或消息队列。
