param(
    [string]$RddStage1Run = "",
    [string]$MioStage1Run = "",
    [int]$RddStage1Epochs = 10,
    [int]$RddStage2Epochs = 20,
    [int]$MioStage2Epochs = 20,
    [int]$RddBatch = 4,
    [int]$MioBatch = 8,
    [int]$Workers = 2,
    [int]$PollSeconds = 60
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
$runsRoot = "D:\Datasets\traffic-incident\runs"

$env:TORCH_HOME = "D:\Datasets\traffic-incident\cache\torch"
$env:ULTRALYTICS_CACHE_DIR = "D:\Datasets\traffic-incident\cache\ultralytics"
$env:YOLO_CONFIG_DIR = "D:\Datasets\traffic-incident\cache\ultralytics"

function Write-Status {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message"
}

function Get-LatestRunName {
    param(
        [string]$ProjectName,
        [string]$Prefix
    )

    $projectDir = Join-Path $runsRoot $ProjectName
    $latest = Get-ChildItem $projectDir -Directory |
        Where-Object { $_.Name -like "$Prefix*" } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if ($null -eq $latest) {
        throw "Unable to locate a run under $projectDir with prefix '$Prefix'."
    }

    return $latest.Name
}

function Wait-ForCompletedRun {
    param(
        [string]$ProjectName,
        [string]$RunName,
        [int]$ExpectedEpochs,
        [int]$PollIntervalSeconds
    )

    $runDir = Join-Path (Join-Path $runsRoot $ProjectName) $RunName
    $resultsPath = Join-Path $runDir "results.csv"
    $bestPath = Join-Path $runDir "weights\best.pt"

    if (-not (Test-Path $runDir)) {
        throw "Run directory not found: $runDir"
    }

    Write-Status "Waiting for $RunName to finish ($ExpectedEpochs epochs expected)."

    while ($true) {
        $rowCount = 0
        if (Test-Path $resultsPath) {
            $rowCount = @(Import-Csv $resultsPath).Count
        }

        if ((Test-Path $bestPath) -and $rowCount -ge $ExpectedEpochs) {
            Write-Status "$RunName completed with $rowCount epochs recorded."
            return $runDir
        }

        if ($rowCount -gt 0) {
            Write-Status "$RunName progress: $rowCount/$ExpectedEpochs epochs recorded."
        }
        else {
            Write-Status "$RunName is still initializing."
        }

        Start-Sleep -Seconds $PollIntervalSeconds
    }
}

function Invoke-StageTraining {
    param(
        [string]$Profile,
        [string]$RunName,
        [int]$Epochs,
        [int]$Batch,
        [int]$Workers,
        [string]$ModelPath = "",
        [int]$ImageSize = 0
    )

    $arguments = @(
        "-m", "yolo.train",
        "--profile", $Profile,
        "--epochs", $Epochs.ToString(),
        "--batch", $Batch.ToString(),
        "--workers", $Workers.ToString(),
        "--save-period", "1",
        "--name", $RunName
    )

    if ($ModelPath) {
        $arguments += @("--model", $ModelPath)
    }

    if ($ImageSize -gt 0) {
        $arguments += @("--imgsz", $ImageSize.ToString())
    }

    Write-Status "Starting $Profile as $RunName."
    & $python @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Training command failed for $RunName with exit code $LASTEXITCODE."
    }
}

if (-not $RddStage1Run) {
    $RddStage1Run = Get-LatestRunName -ProjectName "rdd2022" -Prefix "rdd-stage1-"
}

if (-not $MioStage1Run) {
    $MioStage1Run = Get-LatestRunName -ProjectName "mio-localization" -Prefix "mio-stage1-"
}

$chainTimestamp = Get-Date -Format "yyyyMMdd-HHmmss"

$rddStage1Dir = Wait-ForCompletedRun -ProjectName "rdd2022" -RunName $RddStage1Run -ExpectedEpochs $RddStage1Epochs -PollIntervalSeconds $PollSeconds
$rddStage1Best = Join-Path $rddStage1Dir "weights\best.pt"
if (-not (Test-Path $rddStage1Best)) {
    throw "RDD stage-1 best weight not found at $rddStage1Best"
}

$rddStage2Name = "rdd-stage2-$chainTimestamp"
Invoke-StageTraining -Profile "rdd2022" -RunName $rddStage2Name -Epochs $RddStage2Epochs -Batch $RddBatch -Workers $Workers -ModelPath $rddStage1Best -ImageSize 960

$mioStage1Best = Join-Path (Join-Path (Join-Path $runsRoot "mio-localization") $MioStage1Run) "weights\best.pt"
if (-not (Test-Path $mioStage1Best)) {
    throw "MIO stage-1 best weight not found at $mioStage1Best"
}

$mioStage2Name = "mio-stage2-$chainTimestamp"
Invoke-StageTraining -Profile "mio-localization" -RunName $mioStage2Name -Epochs $MioStage2Epochs -Batch $MioBatch -Workers $Workers -ModelPath $mioStage1Best

$latestTrancos = Get-ChildItem (Join-Path $runsRoot "trancos") -Directory |
    Where-Object { $_.Name -like "trancos-full-*" } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if ($null -eq $latestTrancos) {
    $trancosRunName = "trancos-full-$chainTimestamp"
    Invoke-StageTraining -Profile "trancos" -RunName $trancosRunName -Epochs 30 -Batch 16 -Workers $Workers
}
else {
    Write-Status "TRANCOS full run already exists at $($latestTrancos.FullName). Skipping retraining."
}

Write-Status "Unattended training chain completed."
