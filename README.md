# Traffic Incident Monitoring API Platform

Languages: [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-Hant.md)

Related documents:

- Document index: [English](docs/document-index.md) | [日本語](docs/document-index.ja.md) | [繁體中文](docs/document-index.zh-Hant.md)
- Deployment and run guide: [English](docs/deployment.md) | [日本語](docs/deployment.ja.md) | [繁體中文](docs/deployment.zh-Hant.md)
- Implementation status: [English](docs/implementation-vs-requirements-v2.en.md) | [日本語](docs/implementation-vs-requirements-v2.ja.md) | [繁體中文](docs/implementation-vs-requirements-v2.md)
- AI workflow log: [English](docs/ai-log.md) | [日本語](docs/ai-log.ja.md) | [繁體中文](docs/ai-log.zh-Hant.md)
- Raw AI conversation source: [extracted Markdown](docs/ai-conversation-source.md) | [original PDF](docs/Claude_geminiconversation.md.pdf)
- YOLO video test clips: [English](docs/yolo-video-test.md) | [日本語](docs/yolo-video-test.ja.md) | [繁體中文](docs/yolo-video-test.zh-Hant.md)
- Submission assets and data sources: [English](docs/submission-assets.md) | [日本語](docs/submission-assets.ja.md) | [繁體中文](docs/submission-assets.zh-Hant.md)
- Public release notes: [English](docs/public-release-notes.md) | [日本語](docs/public-release-notes.ja.md) | [繁體中文](docs/public-release-notes.zh-Hant.md)

This repository implements the back-end assignment described in the provided evaluation brief and requirements specification. It receives AI-generated traffic incident events, persists them in SQLite, exposes queryable REST endpoints, and pushes real-time updates to connected dashboards over Server-Sent Events (SSE).

## What is included

- FastAPI API with layered `router / service / repository / schema` structure
- SQLite persistence via SQLAlchemy
- Event ingestion endpoint with Pydantic validation
- Idempotent event ingest via `source_event_id`
- Event list and detail endpoints with filters, sorting, and pagination
- Status update endpoint with reversible operator workflow rules
- SSE endpoint for real-time dashboard updates
- Static HTML dashboard using vanilla JavaScript with English, Japanese, and Chinese language switching, search-only filter guidance, displayed/matching counts, pagination controls, localized incident labels, field tooltips, and reversible status actions
- Random event seed script for demo data
- Dockerfile and `docker-compose.yml`
- Pytest coverage for key API flows
- YOLO training/download/preparation scripts kept on `D:` for low-`C:`-space environments
- Public-safe demo assets in the repository: training summaries and a demo SQLite database snapshot. Dataset-derived videos, snapshots, and trained `.pt` weights are intentionally excluded from the public repo.
- AI workflow log in `docs/ai-log.md`

## Tech choices

- **FastAPI**: automatic docs, fast iteration, native async support
- **SQLite**: sufficient for the exercise, simple local setup
- **SQLAlchemy 2.x**: explicit data model and query control
- **SSE**: direct answer to the “Speed matters” requirement without introducing unnecessary infrastructure
- **Vanilla JS dashboard**: lightweight demo UI with no framework overhead

## Project structure

```text
traffic-incident-api/
├── app/
│   ├── core/
│   ├── models/
│   ├── repositories/
│   ├── routers/
│   ├── schemas/
│   └── services/
├── docs/
├── scripts/
├── tests/
├── ui/
├── yolo/
├── Dockerfile
├── docker-compose.yml
├── README.md
└── requirements.txt
```

## API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/events` | Create a new incident event |
| `GET` | `/events` | List incidents with filtering, sorting, pagination |
| `GET` | `/events/{id}` | Retrieve one incident |
| `PATCH` | `/events/{id}/status` | Move status forward or backward in the operator workflow |
| `GET` | `/events/stream` | Subscribe to real-time incident updates over SSE |

### Supported filters

- `severity=HIGH,CRITICAL`
- `event_type=DEBRIS,CONGESTION`
- `status=NEW,ACKNOWLEDGED`
- `camera_query=CAM,E1,K12+300` for camera/location keyword search
- `camera_id=CAM-001`
- `source_event_id=producer-id`
- `highway_id=E1`
- `detected_from`, `detected_to`, `ingested_from`, `ingested_to` as ISO datetimes
- `min_delay_seconds`, `max_delay_seconds`
- `min_confidence`, `max_confidence` as `0.0..1.0`
- `sort_by=detected_at|ingested_at|updated_at|severity|confidence|detection_delay`
- `order=asc|desc`
- `limit=1..100`
- `offset=0..`

## Local run

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Install dependencies

```bash
.venv\Scripts\pip install -r requirements.txt
```

### 3. Start the API

```bash
.venv\Scripts\uvicorn app.main:app --reload
```

### 4. Open the dashboard

- API docs: `http://localhost:8000/docs`
- Dashboard: `http://localhost:8000/ui/`

### 5. Generate demo traffic incidents

```bash
.venv\Scripts\python scripts\seed.py
```

## Docker run

```bash
docker compose up --build
```

This starts:

- `api` on port `8000`
- `seed` which continuously posts random incidents to the API

## Example event payload

```json
{
  "source_event_id": "cam-001-track-981-2026-04-23T08:30:12Z",
  "event_type": "DEBRIS",
  "severity": "HIGH",
  "description": "Road debris detected on lane 1 shoulder",
  "confidence": 0.94,
  "camera_id": "CAM-001",
  "highway_id": "E1",
  "road_marker": "K12+300",
  "lane_no": "2",
  "latitude": 35.68,
  "longitude": 139.76,
  "image_url": "https://example.com/incidents/1.jpg",
  "detected_at": "2026-04-20T08:00:00Z",
  "extra_payload": {
    "model": "seed"
  }
}
```

## Response contract highlights

- `POST /events` returns `201` on first create
- `POST /events` returns `200` with `meta.deduplicated=true` when the same `source_event_id` is resent with identical content
- duplicate `source_event_id` with conflicting content returns `409`
- `PATCH /events/{id}/status` returns `200` with `meta.noop=true` if the requested status already matches the current status
- SSE emits named events:
  - `incident.created`
  - `incident.status_updated`

## Testing

```bash
.venv\Scripts\pytest
```

Detailed implementation status and manual verification steps are in `docs/implementation-vs-requirements-v2.md`.

## YOLO training version

The project now includes a training-oriented `yolo/` pipeline that keeps datasets, caches, checkpoints, and snapshots on `D:` by default.

### 1. Install the ML stack on `D:`

```powershell
.\scripts\setup_training_env.ps1
```

This installs:

- CUDA-enabled `torch` / `torchvision` / `torchaudio`
- `ultralytics`
- OpenCV and image-processing dependencies

### 2. Download official datasets

```powershell
.\.venv\Scripts\python.exe -m yolo.download_datasets --show-paths
```

Default dataset targets:

- `mio-localization`: official MIO-TCD localization set
- `rdd2022`: official CRDDC RDD2022 archive
- `trancos`: official TRANCOS package

### 3. Prepare datasets for YOLO

```powershell
.\.venv\Scripts\python.exe -m yolo.prepare_mio_tcd
.\.venv\Scripts\python.exe -m yolo.prepare_rdd2022
```

### 4. Train models

```powershell
.\.venv\Scripts\python.exe -m yolo.train --profile mio-localization
.\.venv\Scripts\python.exe -m yolo.train --profile rdd2022
```

### 5. Feed trained detections back into the API

```powershell
.\.venv\Scripts\python.exe -m yolo.infer_video --mode vehicle --weights D:\Datasets\traffic-incident\runs\mio-localization\<run>\weights\best.pt --source D:\path\to\highway.mp4
.\.venv\Scripts\python.exe -m yolo.infer_video --mode damage --weights D:\Datasets\traffic-incident\runs\rdd2022\<run>\weights\best.pt --source D:\path\to\road.mp4
```

`vehicle` mode turns tracked detections into `STOPPED_VEHICLE` and `CONGESTION` events.  
`damage` mode maps road-surface anomalies into `DEBRIS` events.
Use `--annotated-output D:\path\to\output.boxes.mp4` to export a video with YOLO boxes. Use `--dry-run` when you want to inspect detection quality without writing events to the API.

Short local test clips can be generated under `D:\Datasets\traffic-incident\yolovideotest`. For public GitHub release, dataset-derived MP4 files, snapshots, and trained `.pt` weights are not committed. The RDD demo clip was verified locally without `--dry-run`; it inserted two `DEBRIS` events through `POST /events` using `camera_id=CAM-YOLO-VIDEO-RDD`.

Local dry-run demo example after regenerating or restoring local weights and test clips:

```powershell
.\.venv\Scripts\python.exe -m yolo.infer_video --mode damage --weights D:\Datasets\traffic-incident\runs\rdd2022\rdd-stage2-20260421-234643\weights\best.pt --source D:\Datasets\traffic-incident\yolovideotest\rdd_damage_short.mp4 --annotated-output D:\Datasets\traffic-incident\yolovideotest\rdd_damage_short.boxes.mp4 --dry-run
```

### 6. YOLO-to-API-to-database demo

This is the shortest reviewer-friendly path for proving that YOLO detections can be converted into API events and persisted in SQLite. It requires local dataset-derived clips and trained weights, which are excluded from the public repository for licensing safety.

1. Start the API:

```powershell
cd D:\Projects\traffic-incident-api
docker compose up -d --build
docker compose stop seed
```

2. Run the local RDD2022 clip without `--dry-run`:

```powershell
.\.venv\Scripts\python.exe -m yolo.infer_video `
  --mode damage `
  --weights D:\Datasets\traffic-incident\runs\rdd2022\rdd-stage2-20260421-234643\weights\best.pt `
  --source D:\Datasets\traffic-incident\yolovideotest\rdd_damage_short.mp4 `
  --base-url http://127.0.0.1:8000 `
  --camera-id CAM-YOLO-VIDEO-RDD `
  --highway-id E1 `
  --confidence 0.25 `
  --frame-stride 1 `
  --cooldown-seconds 5 `
  --annotated-output D:\Datasets\traffic-incident\yolovideotest\rdd_damage_short.boxes.mp4
```

Expected terminal output includes:

```text
[frame 0] reported DEBRIS with labels D00
[frame 50] reported DEBRIS with labels D00
```

3. Query the events written by YOLO:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/events?camera_id=CAM-YOLO-VIDEO-RDD&sort_by=detected_at&order=desc&limit=10&offset=0' |
  ConvertTo-Json -Depth 12
```

You should see `event_type=DEBRIS`, `camera_id=CAM-YOLO-VIDEO-RDD`, and `extra_payload.source=yolo.detector`. The same records can be checked in Swagger at `http://127.0.0.1:8000/docs` through `GET /events`, or in the dashboard at `http://127.0.0.1:8000/ui/` by filtering `Camera ID` with `CAM-YOLO-VIDEO-RDD`.

## Trade-offs and assumptions

- Authentication and authorization are intentionally out of scope for this assignment.
- SQLite is chosen for simplicity; production should move to PostgreSQL.
- SSE is used instead of WebSockets because the current requirement is one-way server-to-dashboard delivery.
- Status transitions are enforced with explicit workflow rules, while common rollback paths are allowed for operator mistakes.
- `source_event_id` is the idempotency key between detector-side producers and the API.
- The dashboard focuses on operational visibility rather than polished product UX.
- The vehicle detector is fine-tuned on MIO-TCD because it is directly available and suitable for stopped-vehicle and congestion heuristics.
- `RDD2022` is used as the closest openly downloadable road-anomaly training source; it maps to `DEBRIS` events as a roadway hazard proxy, not a perfect debris taxonomy match.
- `TRANCOS` is downloaded for congestion-threshold calibration and future counting-specific work, but the main congestion event flow currently reuses the fine-tuned MIO vehicle detector.
- Raw training images, dataset-derived demo videos/snapshots, trained `.pt` weights, and intermediate epoch checkpoints are intentionally excluded from the public Git repository. The code and scripts remain sufficient to reproduce them locally after obtaining the datasets under their original terms.

## Production follow-ups

- Add API key or JWT-based authentication
- Introduce rate limiting and audit logging
- Store images in object storage such as S3
- Move persistence to PostgreSQL
- Add background workers and retry queues for upstream detector ingest
- Add calibrated model evaluation and monitoring for the detector pipeline
