param(
    [Parameter(Mandatory = $true)]
    [string]$BackupPath,
    [Parameter(Mandatory = $true)]
    [string]$RestorePath
)

$ErrorActionPreference = "Stop"
$backup = (Resolve-Path $BackupPath).Path
$restore = [System.IO.Path]::GetFullPath($RestorePath)
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$repoPrefix = $repo.TrimEnd("\") + "\"
if ($restore.StartsWith($repoPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "O ensaio de restauracao deve usar um diretorio fora do repositorio."
}
if (Test-Path $restore) {
    throw "O diretorio de restauracao ja existe: $restore"
}

$manifestPath = Join-Path $backup "SHA256SUMS.txt"
if (-not (Test-Path $manifestPath)) {
    throw "Manifesto SHA256SUMS.txt ausente."
}

foreach ($line in Get-Content $manifestPath) {
    if ($line -notmatch "^([0-9a-fA-F]{64})\s{2}(.+)$") {
        throw "Linha invalida no manifesto."
    }
    $expected = $Matches[1].ToLowerInvariant()
    $relative = $Matches[2].Replace("/", "\")
    $source = Join-Path $backup $relative
    if (-not (Test-Path $source)) {
        throw "Arquivo ausente no backup: $relative"
    }
    $actual = (Get-FileHash $source -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $expected) {
        throw "Hash invalido: $relative"
    }
}

New-Item -ItemType Directory -Force -Path $restore | Out-Null
Get-ChildItem $backup -Force | Where-Object { $_.Name -ne "SHA256SUMS.txt" } |
    Copy-Item -Destination $restore -Recurse -Force
Copy-Item $manifestPath (Join-Path $restore "SHA256SUMS.txt")

Write-Host "Restauracao ensaiada e validada em: $restore"
