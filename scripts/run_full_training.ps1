param(
    [int]$MioEpochs = 30,
    [int]$RddEpochs = 30,
    [int]$TrancosEpochs = 20,
    [int]$MioBatch = 8,
    [int]$RddBatch = 4,
    [int]$TrancosBatch = 16,
    [int]$Workers = 2
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$defaultDataRoot = Join-Path (Split-Path -Parent $projectRoot) "traffic-incident-data"
$dataRoot = if ($env:TRAFFIC_DATASETS_ROOT) { $env:TRAFFIC_DATASETS_ROOT } else { $defaultDataRoot }
$cacheRoot = if ($env:TRAFFIC_CACHE_ROOT) { $env:TRAFFIC_CACHE_ROOT } else { Join-Path $dataRoot "cache" }
$runsRoot = if ($env:TRAFFIC_RUNS_ROOT) { $env:TRAFFIC_RUNS_ROOT } else { Join-Path $dataRoot "runs" }
$logRoot = Join-Path $runsRoot "logs"
New-Item -ItemType Directory -Force -Path $logRoot | Out-Null

$env:TRAFFIC_DATASETS_ROOT = $dataRoot
$env:TRAFFIC_CACHE_ROOT = $cacheRoot
$env:TRAFFIC_RUNS_ROOT = $runsRoot
$env:TORCH_HOME = Join-Path $cacheRoot "torch"
$env:ULTRALYTICS_CACHE_DIR = Join-Path $cacheRoot "ultralytics"
$env:YOLO_CONFIG_DIR = Join-Path $cacheRoot "ultralytics"

Write-Host "Starting sequential full training run $timestamp"
Write-Host "Using TRAFFIC_DATASETS_ROOT=$env:TRAFFIC_DATASETS_ROOT"

& $python -m yolo.train --profile mio-localization --epochs $MioEpochs --batch $MioBatch --workers $Workers --name "mio-full-$timestamp"
& $python -m yolo.train --profile rdd2022 --epochs $RddEpochs --batch $RddBatch --workers $Workers --imgsz 960 --name "rdd-full-$timestamp"
& $python -m yolo.train --profile trancos --epochs $TrancosEpochs --batch $TrancosBatch --workers $Workers --name "trancos-full-$timestamp"

Write-Host "Full training run $timestamp completed"
