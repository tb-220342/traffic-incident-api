# YOLO Training Pipeline

This directory turns the project from a pure back-end exercise into a training-enabled demo that can fine-tune YOLO models and feed detections back into the API.

## Storage layout on `D:`

- Raw archives: `D:\Datasets\traffic-incident\raw`
- Extracted/prepared datasets: `D:\Datasets\traffic-incident\prepared`
- Training caches and pretrained weights: `D:\Datasets\traffic-incident\cache`
- YOLO runs and checkpoints: `D:\Datasets\traffic-incident\runs`
- Saved detector snapshots: `D:\Datasets\traffic-incident\snapshots`

## Datasets

- `mio-localization`
  Used to fine-tune a vehicle detector for stopped-vehicle and congestion events.
- `rdd2022`
  Used to fine-tune a road anomaly detector that can be mapped to `DEBRIS`-style hazard events.
- `trancos`
  Converted from point annotations into small YOLO boxes so we can fine-tune a congestion-focused vehicle-density model.

## Setup

Run the installer so large packages and caches stay on `D:`.

```powershell
.\scripts\setup_training_env.ps1
```

## Download datasets

```powershell
.\.venv\Scripts\python.exe -m yolo.download_datasets --show-paths
```

## Prepare YOLO datasets

```powershell
.\.venv\Scripts\python.exe -m yolo.prepare_mio_tcd
.\.venv\Scripts\python.exe -m yolo.prepare_rdd2022
.\.venv\Scripts\python.exe -m yolo.prepare_trancos
```

## Train

```powershell
.\.venv\Scripts\python.exe -m yolo.train --profile mio-localization
.\.venv\Scripts\python.exe -m yolo.train --profile rdd2022
.\.venv\Scripts\python.exe -m yolo.train --profile trancos
```

You can override the model, epochs, or batch size if the GPU budget changes.

## Run trained detectors against video

Vehicle incidents:

```powershell
.\.venv\Scripts\python.exe -m yolo.infer_video --mode vehicle --weights D:\Datasets\traffic-incident\runs\mio-localization\<run>\weights\best.pt --source D:\path\to\highway.mp4
```

Road anomaly incidents:

```powershell
.\.venv\Scripts\python.exe -m yolo.infer_video --mode damage --weights D:\Datasets\traffic-incident\runs\rdd2022\<run>\weights\best.pt --source D:\path\to\road.mp4
```

The script will post `STOPPED_VEHICLE`, `CONGESTION`, or `DEBRIS` events back to the API.
