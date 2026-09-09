# 数据库说明

OCHAT 正常运行时使用 MySQL。测试代码使用 SQLite 临时库，避免自动测试污染真实数据库。

## 默认连接配置

| Setting | Default |
| --- | --- |
| Host | `127.0.0.1` |
| Port | `3306` |
| User | `root` |
| Password | empty |
| Database | `ochat` |

## 本机 MySQL 检查结果

当前机器上检测到：

| 项目 | 值 |
| --- | --- |
| 服务名 | `MySQL97` |
| 服务状态 | `Running` |
| MySQL 服务程序 | `C:\Program Files\MySQL\MySQL Server 9.7\bin\mysqld.exe` |
| MySQL 客户端 | `C:\Program Files\MySQL\MySQL Server 9.7\bin\mysql.exe` |
| 配置文件/数据目录 | `E:\MySQL\ProgramData\my.ini` / `E:\MySQL\ProgramData\Data` |

注意：`E:\MySQL\ProgramData\Data` 是 MySQL 数据目录，不是 Python 项目直接读写的目录。OCHAT 通过
`127.0.0.1:3306` 连接正在运行的 MySQL 服务。

## 启动服务端

先安装依赖：

```powershell
python -m pip install -r requirements.txt
```

如果 root 有密码，启动服务端时传入密码：

```powershell
python start_server.py --mysql-user root --mysql-password 你的MySQL密码 --mysql-database ochat
```

也可以用环境变量：

```powershell
$env:OCHAT_DB_HOST="127.0.0.1"
$env:OCHAT_DB_PORT="3306"
$env:OCHAT_DB_USER="root"
$env:OCHAT_DB_PASSWORD="your_password"
$env:OCHAT_DB_NAME="ochat"
python start_server.py
```

## 检查 MySQL

可以手动运行：

```powershell
.\scripts\check_mysql.ps1
```

脚本会调用 MySQL 自带的 `mysql.exe`，提示输入密码，然后执行版本检查并创建 `ochat` 数据库。

## 表结构文件

- MySQL 表结构：`database/schema_mysql.sql`
- SQLite 测试表结构：`database/schema_sqlite.sql`
