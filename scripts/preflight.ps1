param(
    [switch]$SkipTests,
    [switch]$SkipCompile,
    [int]$Port = 3000,
    [string]$DatabasePath = ""
)

$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $repo ".venv\Scripts\python.exe"

function Write-Step([string]$message) {
    Write-Host "[OK] $message" -ForegroundColor Green
}

function Get-LocalEnvValue([string]$name) {
    $processValue = [Environment]::GetEnvironmentVariable($name, "Process")
    if (-not [string]::IsNullOrWhiteSpace($processValue)) {
        return $processValue.Trim()
    }

    $envPath = Join-Path $repo ".env"
    if (-not (Test-Path $envPath)) {
        return $null
    }

    foreach ($line in Get-Content $envPath) {
        if ($line -match "^\s*$([regex]::Escape($name))\s*=\s*(.*)\s*$") {
            return $Matches[1].Trim().Trim('"').Trim("'")
        }
    }
    return $null
}

Set-Location $repo

if (-not (Test-Path $python)) {
    throw "Ambiente ausente. Crie .venv e instale requirements.txt."
}
Write-Step "Python local encontrado."

& $python -m pip check
if ($LASTEXITCODE -ne 0) {
    throw "Dependencias inconsistentes. Execute: .\.venv\Scripts\python.exe -m pip install -r requirements.txt"
}
Write-Step "Dependencias consistentes."

$xanoUrl = Get-LocalEnvValue "XANO_API_URL"
if ([string]::IsNullOrWhiteSpace($xanoUrl)) {
    throw "XANO_API_URL ausente. Copie .env.example para .env e configure a URL."
}
if ($xanoUrl -notmatch "^https://") {
    throw "XANO_API_URL deve usar HTTPS."
}
Write-Step "Configuracao obrigatoria presente."

$listener = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue |
    Select-Object -First 1
if ($null -ne $listener) {
    $process = Get-Process -Id $listener.OwningProcess -ErrorAction SilentlyContinue
    $processName = "desconhecido"
    if ($null -ne $process) {
        $processName = $process.ProcessName
    }
    throw "Porta $Port ocupada pelo PID $($listener.OwningProcess) ($processName). Use Get-Process -Id $($listener.OwningProcess) para diagnosticar; nenhum processo foi encerrado."
}
Write-Step "Porta $Port livre."

$expectedRevision = (
    & $python -c "from alembic.config import Config; from alembic.script import ScriptDirectory; print(ScriptDirectory.from_config(Config('alembic.ini')).get_current_head())"
).Trim()
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($expectedRevision)) {
    throw "Nao foi possivel determinar o head Alembic versionado."
}

if ([string]::IsNullOrWhiteSpace($DatabasePath)) {
    $databasePath = Join-Path $repo "gestao_hospitalar.db"
} else {
    $databasePath = (Resolve-Path $DatabasePath).Path
}

& $python -c "import sqlite3, sys; c=sqlite3.connect(sys.argv[1]); revision=c.execute('SELECT version_num FROM alembic_version').fetchone(); usuario=c.execute('SELECT 1 FROM sqlite_master WHERE type=? AND name=?', ('table', 'usuario')).fetchone(); c.close(); raise SystemExit(0 if revision == (sys.argv[2],) and usuario is None else 1)" $databasePath $expectedRevision
if ($LASTEXITCODE -ne 0) {
    throw "Banco local fora da revisao esperada ou ainda contem a tabela usuario. Execute: .\.venv\Scripts\alembic.exe upgrade head"
}
& $python -c "from alembic.config import Config; from alembic.script import ScriptDirectory; import sys; raise SystemExit(0 if ScriptDirectory.from_config(Config('alembic.ini')).get_current_head() == sys.argv[1] else 1)" $expectedRevision
if ($LASTEXITCODE -ne 0) {
    throw "Historico Alembic inconsistente."
}
Write-Step "Migracoes locais alinhadas."

if (-not $SkipTests) {
    & $python -m unittest discover -s tests
    if ($LASTEXITCODE -ne 0) {
        throw "Suite de testes falhou. Corrija as falhas antes da apresentacao."
    }
    Write-Step "Suite de testes aprovada."
}

if (-not $SkipCompile) {
    & $python -m reflex compile --dry
    if ($LASTEXITCODE -ne 0) {
        throw "Compilacao Reflex falhou."
    }
    Write-Step "Compilacao Reflex aprovada."
}

try {
    $response = Invoke-WebRequest -UseBasicParsing -Uri $xanoUrl -Method Get -TimeoutSec 10
    if ($response.StatusCode -ge 500) {
        throw "Xano respondeu HTTP $($response.StatusCode)."
    }
} catch [System.Net.WebException] {
    if ($null -eq $_.Exception.Response) {
        throw "Xano inacessivel: $($_.Exception.Message)"
    }
    $statusCode = [int]$_.Exception.Response.StatusCode
    if ($statusCode -ge 500) {
        throw "Xano respondeu HTTP $statusCode."
    }
}
Write-Step "Conectividade Xano confirmada."

$dirty = (& git status --porcelain | Out-String).Trim()
if (-not [string]::IsNullOrWhiteSpace($dirty)) {
    Write-Warning "O working tree possui alteracoes locais. Elas nao impedem o inicio, mas devem estar respaldadas."
} else {
    Write-Step "Working tree limpo."
}

Write-Host ""
Write-Host "PREFLIGHT APROVADO: sistema pronto para iniciar em http://localhost:$Port" -ForegroundColor Green
