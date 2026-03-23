$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$specPath = Join-Path $scriptDir 'release/windows/pyinstaller-windows.spec'

if (-not (Test-Path -LiteralPath $specPath)) {
    throw "Spec file not found: $specPath"
}

pyinstaller $specPath @args
