param(
    [Parameter(Mandatory = $true)]
    [string]$DestinationRoot
)

$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$destinationParent = [System.IO.Path]::GetFullPath($DestinationRoot)
$repoPrefix = $repo.TrimEnd("\") + "\"
if ($destinationParent.StartsWith($repoPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "O backup deve ser salvo fora do repositorio."
}

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backup = Join-Path $destinationParent "gestao-hospitalar-$timestamp"
$configDirectory = Join-Path $backup "config"
$alembicDirectory = Join-Path $configDirectory "alembic"
$gitDirectory = Join-Path $backup "git"
$xanoDirectory = Join-Path $backup "xano-workspace"

New-Item -ItemType Directory -Force -Path $alembicDirectory, $gitDirectory | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $alembicDirectory "versions") | Out-Null
Set-Location $repo

$database = Join-Path $repo "gestao_hospitalar.db"
if (Test-Path $database) {
    Copy-Item $database (Join-Path $backup "gestao_hospitalar.db")
}

Copy-Item (Join-Path $repo "requirements.txt") (Join-Path $configDirectory "requirements.txt")
Copy-Item (Join-Path $repo "rxconfig.py") (Join-Path $configDirectory "rxconfig.py")
Copy-Item (Join-Path $repo "alembic.ini") (Join-Path $configDirectory "alembic.ini")
Copy-Item (Join-Path $repo ".env.example") (Join-Path $configDirectory ".env.example")
Get-ChildItem (Join-Path $repo "alembic\versions") -File -Filter "*.py" |
    Copy-Item -Destination (Join-Path $alembicDirectory "versions")

git rev-parse HEAD | Set-Content -Encoding ASCII (Join-Path $gitDirectory "commit.txt")
git status --short | Set-Content -Encoding UTF8 (Join-Path $gitDirectory "status.txt")
git diff --binary | Set-Content -Encoding UTF8 (Join-Path $gitDirectory "working-tree.diff")

$xano = Get-Command "xano.cmd" -ErrorAction SilentlyContinue
if ($null -eq $xano) {
    throw "Xano CLI nao encontrado. Instale/configure o CLI antes do backup."
}
& $xano.Source workspace pull -d $xanoDirectory
if ($LASTEXITCODE -ne 0) {
    throw "Falha ao exportar o workspace Xano."
}

$forbidden = Get-ChildItem $backup -Recurse -File | Where-Object {
    $_.Name -eq ".env" -or
    $_.Extension -in @(".log", ".pyc") -or
    $_.FullName -match "\\(__pycache__|\.venv|\.web)\\"
}
if ($forbidden) {
    throw "Backup contem arquivos proibidos: $($forbidden.FullName -join ', ')"
}

$manifestPath = Join-Path $backup "SHA256SUMS.txt"
Get-ChildItem $backup -Recurse -File |
    Where-Object { $_.FullName -ne $manifestPath } |
    Sort-Object FullName |
    ForEach-Object {
        $relative = $_.FullName.Substring($backup.Length + 1).Replace("\", "/")
        $hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        "$hash  $relative"
    } | Set-Content -Encoding ASCII $manifestPath

Write-Host "Backup criado em: $backup"
Write-Output $backup
