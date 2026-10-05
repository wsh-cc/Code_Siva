@echo off
setlocal

set "ROOT=%~dp0"
"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "%ROOT%scripts\install_task.ps1"

set "EXITCODE=%ERRORLEVEL%"
echo.
if "%EXITCODE%"=="0" (
    echo Auto-start has been installed.
) else (
    echo Failed to install auto-start. Exit code %EXITCODE%.
)
pause
exit /b %EXITCODE%
