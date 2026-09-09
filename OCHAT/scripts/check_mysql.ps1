param(
    [string]$MysqlExe = "C:\Program Files\MySQL\MySQL Server 9.7\bin\mysql.exe",
    [string]$User = "root",
    [string]$Database = "ochat"
)

if (-not (Test-Path -LiteralPath $MysqlExe)) {
    Write-Error "mysql.exe not found: $MysqlExe"
    exit 1
}

if ($Database -notmatch '^[A-Za-z0-9_]+$') {
    Write-Error "Database name may only contain letters, numbers, and underscores."
    exit 1
}

& $MysqlExe -u $User -p -e "SELECT VERSION(); CREATE DATABASE IF NOT EXISTS ``$Database`` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; SHOW DATABASES LIKE '$Database';"
