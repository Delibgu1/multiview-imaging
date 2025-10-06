param(
  [Parameter(Mandatory=$true)][string]$In,
  [Parameter(Mandatory=$true)][string]$Out
)
$ErrorActionPreference = "Stop"

# localizar 'rio' (prioriza o do venv multiview)
$rio = $null
$try = @(
  (Join-Path $env:USERPROFILE "Envs\multiview\Scripts\rio.exe"),
  "rio"
)
foreach ($c in $try) {
  try { $cmd = Get-Command $c -ErrorAction Stop; $rio = $cmd.Path; break } catch {}
}
if (-not $rio) { Write-Error "Não encontrei 'rio'. Instale: pip install rasterio rio-cogeo"; exit 1 }

# validar caminhos
if (-not (Test-Path -LiteralPath $In)) { Write-Error "Arquivo de entrada não encontrado: $In"; exit 1 }
$inPath = (Resolve-Path -LiteralPath $In).Path

$OutDir  = Split-Path -Parent $Out
$OutLeaf = Split-Path -Leaf  $Out
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = "." }
if (-not (Test-Path -LiteralPath $OutDir)) { Write-Error "Diretório de saída não existe: $OutDir"; exit 1 }
$outPath = Join-Path (Resolve-Path -LiteralPath $OutDir).Path $OutLeaf

# se In e Out forem o mesmo arquivo, renomeia saída p/ *_cog.tif
if ($inPath -eq $outPath) {
  $outPath = [IO.Path]::Combine(
    [IO.Path]::GetDirectoryName($inPath),
    [IO.Path]::GetFileNameWithoutExtension($inPath) + "_cog.tif"
  )
  Write-Host "Saída igual à entrada; ajustando para: $outPath"
}

# executar
$argsRio = @("cogeo","create",$inPath,$outPath,"--overview-level","5","--overview-resampling","nearest","--web-optimized")
Write-Host ">> $rio $($argsRio -join ' ')"
& $rio @argsRio
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host ("OK: {0}" -f $outPath)
