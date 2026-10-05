@echo off
setlocal

set "ROOT=%~dp0"
"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "%ROOT%scripts\uninstall_task.ps1"

set "EXITCODE=%ERRORLEVEL%"
echo.
if "%EXITCODE%"=="0" (
    echo Auto-start has been removed.
) else (
    echo Failed to remove auto-start. Exit code %EXITCODE%.
)
pause
exit /b %EXITCODE%
