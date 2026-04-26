$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$cacheRoot = "D:\Datasets\traffic-incident\cache"
$torchHome = Join-Path $cacheRoot "torch"
$pipCache = Join-Path $cacheRoot "pip"
$ultralyticsCache = Join-Path $cacheRoot "ultralytics"

New-Item -ItemType Directory -Force -Path $cacheRoot, $torchHome, $pipCache, $ultralyticsCache | Out-Null

$env:PIP_CACHE_DIR = $pipCache
$env:TORCH_HOME = $torchHome
$env:ULTRALYTICS_CACHE_DIR = $ultralyticsCache

Write-Host "Using caches on D:"
Write-Host "  PIP_CACHE_DIR=$env:PIP_CACHE_DIR"
Write-Host "  TORCH_HOME=$env:TORCH_HOME"
Write-Host "  ULTRALYTICS_CACHE_DIR=$env:ULTRALYTICS_CACHE_DIR"

& "$projectRoot\.venv\Scripts\python.exe" -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
& "$projectRoot\.venv\Scripts\python.exe" -m pip install -r "$projectRoot\requirements-ml.txt"

Write-Host ""
Write-Host "Training environment is ready."
