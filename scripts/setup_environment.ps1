param(
    [string]$PythonLauncher = "py",
    [string]$PythonVersion = "-3.14"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$environmentPath = Join-Path $projectRoot ".venv"
$pythonPath = Join-Path $environmentPath "Scripts\python.exe"

& $PythonLauncher $PythonVersion -m venv $environmentPath
& $pythonPath -m pip install --upgrade pip
& $pythonPath -m pip install -r (Join-Path $projectRoot "requirements.txt")

Write-Output "Ambiente criado em $environmentPath"
Write-Output "Execute os testes com: $pythonPath -m pytest -q"
