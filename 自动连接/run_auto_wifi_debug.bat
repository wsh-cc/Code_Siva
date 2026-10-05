@echo off
setlocal

set "ROOT=%~dp0"
"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "%ROOT%scripts\run_auto_wifi.ps1"

set "EXITCODE=%ERRORLEVEL%"
if not "%EXITCODE%"=="0" (
    echo.
    echo Auto Wi-Fi connector exited with code %EXITCODE%.
    pause
)
exit /b %EXITCODE%
