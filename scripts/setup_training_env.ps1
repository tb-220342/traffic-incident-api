$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$defaultDataRoot = Join-Path (Split-Path -Parent $projectRoot) "traffic-incident-data"
$dataRoot = if ($env:TRAFFIC_DATASETS_ROOT) { $env:TRAFFIC_DATASETS_ROOT } else { $defaultDataRoot }
$cacheRoot = if ($env:TRAFFIC_CACHE_ROOT) { $env:TRAFFIC_CACHE_ROOT } else { Join-Path $dataRoot "cache" }
$torchHome = Join-Path $cacheRoot "torch"
$pipCache = Join-Path $cacheRoot "pip"
$ultralyticsCache = Join-Path $cacheRoot "ultralytics"

New-Item -ItemType Directory -Force -Path $cacheRoot, $torchHome, $pipCache, $ultralyticsCache | Out-Null

$env:PIP_CACHE_DIR = $pipCache
$env:TRAFFIC_DATASETS_ROOT = $dataRoot
$env:TRAFFIC_CACHE_ROOT = $cacheRoot
$env:TRAFFIC_RUNS_ROOT = if ($env:TRAFFIC_RUNS_ROOT) { $env:TRAFFIC_RUNS_ROOT } else { Join-Path $dataRoot "runs" }
$env:TORCH_HOME = $torchHome
$env:ULTRALYTICS_CACHE_DIR = $ultralyticsCache

Write-Host "Using external ML data/cache directory:"
Write-Host "  TRAFFIC_DATASETS_ROOT=$env:TRAFFIC_DATASETS_ROOT"
Write-Host "  TRAFFIC_CACHE_ROOT=$env:TRAFFIC_CACHE_ROOT"
Write-Host "  TRAFFIC_RUNS_ROOT=$env:TRAFFIC_RUNS_ROOT"
Write-Host "  PIP_CACHE_DIR=$env:PIP_CACHE_DIR"
Write-Host "  TORCH_HOME=$env:TORCH_HOME"
Write-Host "  ULTRALYTICS_CACHE_DIR=$env:ULTRALYTICS_CACHE_DIR"

& "$projectRoot\.venv\Scripts\python.exe" -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
& "$projectRoot\.venv\Scripts\python.exe" -m pip install -r "$projectRoot\requirements-ml.txt"

Write-Host ""
Write-Host "Training environment is ready."
