param(
    [string]$TaskName = "AutoWiFiConnector",
    [string]$Python = "E:\python312\python.exe",
    [string]$ConfigPath = "",
    [switch]$RunOnce
)

$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$ScriptPath = Join-Path $Root "auto_wifi.py"

if (-not $ConfigPath) {
    $ConfigPath = Join-Path $Root "wifi_config.json"
}

if (-not (Test-Path -LiteralPath $Python)) {
    $FallbackPython = "E:\Anaconda\python.exe"
    if (Test-Path -LiteralPath $FallbackPython) {
        $Python = $FallbackPython
    }
}

if (-not (Test-Path -LiteralPath $ScriptPath)) {
    throw "auto_wifi.py was not found at $ScriptPath"
}

if (-not (Test-Path -LiteralPath $ConfigPath)) {
    throw "Config file was not found at $ConfigPath. Run: & `"$Python`" .\auto_wifi.py init"
}

if (-not (Test-Path -LiteralPath $Python)) {
    throw "Python was not found at $Python"
}

$Arguments = "`"$ScriptPath`" --config `"$ConfigPath`" run --verbose"
if ($RunOnce) {
    $Arguments = "$Arguments --once"
}

$Action = New-ScheduledTaskAction -Execute $Python -Argument $Arguments
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Days 0)
$Principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Highest

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description "Auto-connect this user to preferred Wi-Fi networks." `
    -Force | Out-Null

Write-Host "Installed scheduled task: $TaskName"
Write-Host "Python: $Python"
Write-Host "Config: $ConfigPath"
if ($RunOnce) {
    Write-Host "Mode: run once at user logon"
} else {
    Write-Host "Mode: keep running in the background after user logon"
}
