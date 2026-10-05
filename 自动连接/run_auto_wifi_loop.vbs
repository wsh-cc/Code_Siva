Option Explicit

Dim fso, shell, root, powershellPath, scriptPath, arguments

Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("Shell.Application")

root = fso.GetParentFolderName(WScript.ScriptFullName)
powershellPath = "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
scriptPath = fso.BuildPath(root, "scripts\run_auto_wifi.ps1")

arguments = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & scriptPath & """ -Loop -Background -NoPause"
shell.ShellExecute powershellPath, arguments, root, "open", 0
