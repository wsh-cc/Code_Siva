param(
    [string]$Python = "",
    [switch]$Loop,
    [switch]$NoPause,
    [switch]$Background
)

$ErrorActionPreference = "Stop"

function Test-IsAdministrator {
    $Identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $Principal = New-Object Security.Principal.WindowsPrincipal($Identity)
    return $Principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Resolve-Python {
    param([string]$Override)

    if ($Override -and (Test-Path -LiteralPath $Override)) {
        return (Resolve-Path -LiteralPath $Override).Path
    }

    $Candidates = @(
        "E:\python312\python.exe",
        "E:\Anaconda\python.exe"
    )

    foreach ($Candidate in $Candidates) {
        if (Test-Path -LiteralPath $Candidate) {
            return $Candidate
        }
    }

    $Commands = Get-Command python -All -ErrorAction SilentlyContinue
    foreach ($Command in $Commands) {
        if ($Command.Source -and $Command.Source -notlike "*\Microsoft\WindowsApps\python.exe") {
            return $Command.Source
        }
    }

    throw "Could not find a real Python executable. Expected E:\python312\python.exe."
}

if (-not (Test-IsAdministrator)) {
    $PowerShellPath = Join-Path $env:WINDIR "System32\WindowsPowerShell\v1.0\powershell.exe"
    if (-not (Test-Path -LiteralPath $PowerShellPath)) {
        $PowerShellPath = "powershell.exe"
    }

    $ArgumentList = @(
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        "`"$PSCommandPath`""
    )
    if ($Python) {
        $ArgumentList += @("-Python", "`"$Python`"")
    }
    if ($Loop) {
        $ArgumentList += "-Loop"
    }
    if ($NoPause) {
        $ArgumentList += "-NoPause"
    }
    if ($Background) {
        $ArgumentList += "-Background"
    }

    $StartParams = @{
        FilePath = $PowerShellPath
        ArgumentList = $ArgumentList
        Verb = "RunAs"
    }
    if ($Background) {
        $StartParams["WindowStyle"] = "Hidden"
    }

    Start-Process @StartParams
    exit 0
}

$Root = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$ScriptPath = Join-Path $Root "auto_wifi.py"
$ConfigPath = Join-Path $Root "wifi_config.json"
$PythonPath = Resolve-Python -Override $Python

if (-not (Test-Path -LiteralPath $ScriptPath)) {
    throw "auto_wifi.py was not found at $ScriptPath"
}
if (-not (Test-Path -LiteralPath $ConfigPath)) {
    throw "wifi_config.json was not found at $ConfigPath"
}

if (-not $Background) {
    Write-Host "Auto Wi-Fi connector"
    Write-Host "Python: $PythonPath"
    Write-Host "Config: $ConfigPath"
    Write-Host ""
}

$RunArgs = @($ScriptPath, "--config", $ConfigPath, "run", "--verbose")
if (-not $Loop) {
    $RunArgs += "--once"
}

& $PythonPath @RunArgs
$ExitCode = $LASTEXITCODE

if (-not $NoPause -and -not $Background) {
    Write-Host ""
    Read-Host "Press Enter to close"
}

exit $ExitCode
