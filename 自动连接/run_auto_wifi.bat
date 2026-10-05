@echo off
setlocal

set "ROOT=%~dp0"
"C:\Windows\System32\wscript.exe" "%ROOT%run_auto_wifi.vbs"
exit /b 0
