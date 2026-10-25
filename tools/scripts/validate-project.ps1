$ErrorActionPreference = "Stop"

Write-Host "Validando estrutura do projeto..."

$required = @(
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "docs",
    "evals",
    "skills",
    "tools"
)

foreach ($item in $required) {
    if (-not (Test-Path $item)) {
        throw "Item obrigatório ausente: $item"
    }
}

if (Test-Path "ai-dev-template") {
    Write-Warning "Atenção: existe uma subpasta ai-dev-template dentro da raiz."
}

Write-Host "Estrutura básica válida."