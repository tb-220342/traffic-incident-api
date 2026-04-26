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
$logRoot = "D:\Datasets\traffic-incident\runs\logs"
New-Item -ItemType Directory -Force -Path $logRoot | Out-Null

$env:TORCH_HOME = "D:\Datasets\traffic-incident\cache\torch"
$env:ULTRALYTICS_CACHE_DIR = "D:\Datasets\traffic-incident\cache\ultralytics"
$env:YOLO_CONFIG_DIR = "D:\Datasets\traffic-incident\cache\ultralytics"

Write-Host "Starting sequential full training run $timestamp"

& $python -m yolo.train --profile mio-localization --epochs $MioEpochs --batch $MioBatch --workers $Workers --name "mio-full-$timestamp"
& $python -m yolo.train --profile rdd2022 --epochs $RddEpochs --batch $RddBatch --workers $Workers --imgsz 960 --name "rdd-full-$timestamp"
& $python -m yolo.train --profile trancos --epochs $TrancosEpochs --batch $TrancosBatch --workers $Workers --name "trancos-full-$timestamp"

Write-Host "Full training run $timestamp completed"
