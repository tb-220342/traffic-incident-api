# 交通事件監控 API 平台

語言: [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-Hant.md)

相關文件:

- 文檔索引: [English](docs/document-index.md) | [日本語](docs/document-index.ja.md) | [繁體中文](docs/document-index.zh-Hant.md)
- 部署 / 執行指南: [English](docs/deployment.md) | [日本語](docs/deployment.ja.md) | [繁體中文](docs/deployment.zh-Hant.md)
- 實作完成度: [English](docs/implementation-vs-requirements-v2.en.md) | [日本語](docs/implementation-vs-requirements-v2.ja.md) | [繁體中文](docs/implementation-vs-requirements-v2.md)
- 要件定義書翻譯: [English](docs/requirements-spec.en.md) | [日本語](docs/requirements-spec.ja.md) | [繁體中文](docs/requirements-spec.zh-Hant.md) | [source PDF](docs/requirements_spec.md.pdf)
- AI 使用紀錄: [English](docs/ai-log.md) | [日本語](docs/ai-log.ja.md) | [繁體中文](docs/ai-log.zh-Hant.md)
- AI 對話來源: [English](docs/ai-conversation-source.en.md) | [日本語](docs/ai-conversation-source.ja.md) | [繁體中文](docs/ai-conversation-source.zh-Hant.md) | [raw 抽出 Markdown](docs/ai-conversation-source.md) | [原始 PDF](docs/Claude_geminiconversation.md.pdf)
- YOLO 影片測試: [English](docs/yolo-video-test.md) | [日本語](docs/yolo-video-test.ja.md) | [繁體中文](docs/yolo-video-test.zh-Hant.md)
- 提交用資產與資料來源: [English](docs/submission-assets.md) | [日本語](docs/submission-assets.ja.md) | [繁體中文](docs/submission-assets.zh-Hant.md)
- 公開發布說明: [English](docs/public-release-notes.md) | [日本語](docs/public-release-notes.ja.md) | [繁體中文](docs/public-release-notes.zh-Hant.md)

這個專案是針對後端面試課題完成的交通事件監控 API。系統會接收 AI 影像分析送出的事件，將資料保存到 SQLite，提供可查詢的 REST API，並透過 Server-Sent Events (SSE) 即時推送到 Dashboard。

## 包含內容

- FastAPI 後端，採用 `router / service / repository / schema` 分層
- SQLAlchemy + SQLite 持久化
- 使用 `source_event_id` 做事件冪等與去重
- 支援篩選、排序、分頁的事件列表 API
- 支援退回操作的事件狀態更新 API
- SSE 即時推播
- 支援 English / 日本語 / 中文 切換的靜態 Dashboard，並補上搜尋專用 Filter 說明、顯示 / 符合總數、翻頁控制、事件類型多語顯示、欄位 tooltip、可退回的狀態操作
- 隨機假事件 seed script
- `Dockerfile` 與 `docker-compose.yml`
- 主要 API 流程的 pytest 測試
- 使用 `TRAFFIC_DATASETS_ROOT` 指定之外部 data directory 的 YOLO 訓練 / 推理管線
- `docs/ai-log.md` 的 AI 使用紀錄

## 技術選型

- **FastAPI**: 開發速度快，內建 API 文件，支援 async。
- **SQLite**: 適合本地 demo 與面試提交，啟動成本低。
- **SQLAlchemy 2.x**: 讓資料模型與查詢邏輯更清楚。
- **SSE**: 符合 Dashboard 單向即時更新需求，比 WebSocket 更簡潔。
- **Vanilla JS Dashboard**: 不引入前端框架，專注展示 API 與即時推播。

## API 端點

| Method | Path | 用途 |
| --- | --- | --- |
| `POST` | `/events` | 接收新事件 |
| `GET` | `/events` | 查詢事件列表，支援篩選、排序、分頁 |
| `GET` | `/events/{id}` | 查詢單筆事件 |
| `PATCH` | `/events/{id}/status` | 將事件處理狀態往前或往回更新 |
| `GET` | `/events/stream` | 透過 SSE 訂閱即時事件 |

主要列表篩選:

- `severity`、`event_type`、`status`
- `camera_query`、`camera_id`、`source_event_id`、`highway_id`
- `detected_from/to`、`ingested_from/to`
- `min_delay_seconds`、`max_delay_seconds`
- `min_confidence`、`max_confidence`
- `sort_by=detected_at|ingested_at|updated_at|severity|confidence|detection_delay`
- `limit`、`offset`

## 本地啟動

```powershell
cd <repo-root>
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\uvicorn app.main:app --reload
```

打開:

- API docs: `http://localhost:8000/docs`
- Dashboard: `http://localhost:8000/ui/`

產生 demo 事件:

```powershell
.\.venv\Scripts\python scripts\seed.py
```

## Docker 啟動

```powershell
cd <repo-root>
docker compose up -d --build
```

會啟動:

- `api`: `http://localhost:8000`
- `seed`: 持續送出隨機事件

若要停止 seed:

```powershell
docker compose stop seed
```

## 測試

```powershell
cd <repo-root>
.\.venv\Scripts\pytest
```

目前驗證結果為 `7 passed`。

## 回應契約重點

- `POST /events` 首次建立會回 `201`。
- 相同 `source_event_id` 且內容一致的重送會回 `200` + `meta.deduplicated=true`。
- 相同 `source_event_id` 但內容衝突會回 `409`。
- 更新到相同狀態會回 `200` + `meta.noop=true`。
- SSE 會送出 `incident.created` 與 `incident.status_updated`。

## YOLO 整合

YOLO 相關資料集、快取、訓練結果與截圖都預設放在 `<DATA_ROOT>`，也可以透過 `TRAFFIC_DATASETS_ROOT` 指定任意外部資料目錄。
`<DATA_ROOT>` 預設為 `../traffic-incident-data`，代表 repository 外部的 ML data directory。
public GitHub release 不包含 dataset 派生 MP4、snapshot、trained `.pt` weight；`model-artifacts/` 只保留 training summary。RDD demo clip 已在本機確認不加 `--dry-run` 可透過 `POST /events` 寫入 2 筆 `DEBRIS` event，`camera_id=CAM-YOLO-VIDEO-RDD`。

```powershell
.\scripts\setup_training_env.ps1
.\.venv\Scripts\python.exe -m yolo.download_datasets --show-paths
.\.venv\Scripts\python.exe -m yolo.prepare_mio_tcd
.\.venv\Scripts\python.exe -m yolo.prepare_rdd2022
.\.venv\Scripts\python.exe -m yolo.train --profile mio-localization
.\.venv\Scripts\python.exe -m yolo.train --profile rdd2022
```

影片推理並回寫 API:

```powershell
.\.venv\Scripts\python.exe -m yolo.infer_video --mode vehicle --weights <DATA_ROOT>\runs\mio-localization\<run>\weights\best.pt --source <path-to-highway-video>.mp4
.\.venv\Scripts\python.exe -m yolo.infer_video --mode damage --weights <DATA_ROOT>\runs\rdd2022\<run>\weights\best.pt --source <path-to-road-video>.mp4
```

提交用 demo 最短確認方式:

```powershell
docker compose up -d --build
docker compose stop seed
.\.venv\Scripts\python.exe -m yolo.infer_video --mode damage --weights <DATA_ROOT>\runs\rdd2022\rdd-stage2-20260421-234643\weights\best.pt --source <DATA_ROOT>\yolovideotest\rdd_damage_short.mp4 --base-url http://127.0.0.1:8000 --camera-id CAM-YOLO-VIDEO-RDD --confidence 0.25 --frame-stride 1 --cooldown-seconds 5 --annotated-output <DATA_ROOT>\yolovideotest\rdd_damage_short.boxes.mp4
Invoke-RestMethod 'http://127.0.0.1:8000/events?camera_id=CAM-YOLO-VIDEO-RDD&sort_by=detected_at&order=desc&limit=10&offset=0' | ConvertTo-Json -Depth 12
```

查詢結果應包含 `event_type=DEBRIS`、`camera_id=CAM-YOLO-VIDEO-RDD`、`extra_payload.source=yolo.detector`。也可以在 Swagger `http://127.0.0.1:8000/docs` 的 `GET /events` 查，或在 Dashboard `http://127.0.0.1:8000/ui/` 用 Camera ID 篩選。

## 取捨

- 認證與授權不在本次課題範圍內。
- SQLite 適合本地 demo，正式環境建議換成 PostgreSQL。
- 使用 SSE 是因為目前需求是後端到 Dashboard 的單向即時推送。
- `source_event_id` 是偵測系統與 API 之間的冪等 key。
- Dashboard 目標是展示營運流程與即時性，不是做完整前端產品。

## 若進一步產品化

- API key 或 JWT 認證
- rate limiting 與 audit log
- 圖片改存 object storage
- PostgreSQL
- retry queue / background worker
- 模型評估與 detector pipeline 監控
