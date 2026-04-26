# Deployment and Run Guide

This project is designed as an interview/demo service. The recommended deployment for review is Docker Compose on a local machine.

## Recommended Demo Deployment

```powershell
cd D:\Projects\traffic-incident-api
docker compose up -d --build
docker compose ps
```

Open:

- API health: `http://127.0.0.1:8000/health`
- Swagger API docs: `http://127.0.0.1:8000/docs`
- Dashboard UI: `http://127.0.0.1:8000/ui/`

The Docker stack starts:

- `api`: FastAPI application on port `8000`
- `seed`: optional fake-event generator that posts demo events to the API

For manual API or YOLO testing, stop the seed service so new test records are easy to find:

```powershell
docker compose stop seed
```

Stop the whole stack:

```powershell
docker compose down
```

## Local Python Run

```powershell
cd D:\Projects\traffic-incident-api
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\uvicorn app.main:app --reload
```

This is useful for development. Docker Compose is easier for reviewer playback.

## Database Persistence

Docker Compose mounts `./data` into the API container, so SQLite persists at:

```text
D:\Projects\traffic-incident-api\data\incidents.db
```

The repository also includes a packaged demo database snapshot:

```text
demo-data/incidents-demo.db
```

That snapshot contains seed/demo records plus two verified YOLO-generated `DEBRIS` events from `CAM-YOLO-VIDEO-RDD`.

## YOLO Write-To-API Demo

Public GitHub releases intentionally do not include dataset-derived MP4 clips, YOLO snapshots, or trained `.pt` weights. To run this demo, keep the local dataset artifacts under `D:\Datasets\traffic-incident` or regenerate them with the scripts in `yolo/`. The packaged demo database still contains two verified YOLO-generated rows, so the reviewer can confirm API/UI behavior without redistributing the underlying media or weights.

Start the API and stop seed:

```powershell
docker compose up -d --build
docker compose stop seed
```

Run the local RDD clip without `--dry-run`:

```powershell
.\.venv\Scripts\python.exe -m yolo.infer_video `
  --mode damage `
  --weights D:\Datasets\traffic-incident\runs\rdd2022\rdd-stage2-20260421-234643\weights\best.pt `
  --source D:\Datasets\traffic-incident\yolovideotest\rdd_damage_short.mp4 `
  --base-url http://127.0.0.1:8000 `
  --camera-id CAM-YOLO-VIDEO-RDD `
  --confidence 0.25 `
  --frame-stride 1 `
  --cooldown-seconds 5 `
  --annotated-output D:\Datasets\traffic-incident\yolovideotest\rdd_damage_short.boxes.mp4
```

Query written records:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/events?camera_id=CAM-YOLO-VIDEO-RDD&sort_by=detected_at&order=desc&limit=10&offset=0' |
  ConvertTo-Json -Depth 12
```

## Test Before Submission

```powershell
.\.venv\Scripts\pytest -q
```

Expected result:

```text
7 passed
```

## Production Notes

For a production deployment, the following would be added or changed:

- Replace SQLite with PostgreSQL.
- Add API authentication, e.g. API key or JWT.
- Store snapshots/images in object storage instead of local disk.
- Add rate limiting, audit logs, metrics, and structured observability.
- Run API and detector workers separately, with retry queues for ingestion.

These are intentionally outside the interview scope, but the current code structure leaves clear extension points.
