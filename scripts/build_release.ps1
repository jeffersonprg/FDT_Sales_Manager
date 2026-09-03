$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
    throw "O ambiente .venv não foi encontrado. Execute primeiro scripts\setup_environment.ps1."
}

$pythonValido = $true
try {
    & $python --version *> $null
    $pythonValido = $LASTEXITCODE -eq 0
}
catch {
    $pythonValido = $false
}
if (-not $pythonValido) {
    throw "O ambiente .venv está inválido ou aponta para um Python removido. Recrie-o antes do build."
}

$pyInstallerDisponivel = $true
try {
    & $python -c "import PyInstaller" *> $null
    $pyInstallerDisponivel = $LASTEXITCODE -eq 0
}
catch {
    $pyInstallerDisponivel = $false
}
if (-not $pyInstallerDisponivel) {
    throw "PyInstaller não está instalado. Execute: .\.venv\Scripts\python.exe -m pip install pyinstaller"
}

Push-Location $projectRoot
try {
    & $python -m PyInstaller --noconfirm --clean "FDT_Sales_Manager.spec"
    if ($LASTEXITCODE -ne 0) {
        throw "A geração da aplicação terminou com erro."
    }
}
finally {
    Pop-Location
}

Write-Host "Aplicação gerada em dist\FDT Sales Manager"
