# 交通事件監控 API 平台

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](#技術選型)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)](#api-端點)
[![SQLite](https://img.shields.io/badge/SQLite-Persistence-003B57?logo=sqlite&logoColor=white)](#本地啟動)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](#docker-啟動)
[![SSE](https://img.shields.io/badge/Realtime-SSE-111827)](#回應契約重點)
[![YOLO](https://img.shields.io/badge/YOLO-Optional%20Pipeline-FF6B00)](#yolo-整合)

語言: [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-Hant.md)

這是針對後端面試課題完成的交通事件監控平台。系統接收 AI 影像分析產生的道路事件，保存到 SQLite，提供可查詢 REST API，並透過 SSE 即時推送到 Dashboard。

> [!NOTE]
> 這個公開 repository 已整理成可安全分享的狀態：不包含原始資料集、資料集派生 MP4、snapshot、訓練完成的 `.pt` weight、本地 `.env` 或個人電腦路徑。

## 審查快速路徑

| 目的 | 連結 / 指令 |
| --- | --- |
| 啟動示範 | `docker compose up -d --build` |
| API 文件 | `http://127.0.0.1:8000/docs` |
| 儀表板 | `http://127.0.0.1:8000/ui/` |
| 查看設計判斷 | [架構審查備忘](docs/architecture-review-notes.zh-Hant.md) |
| 查看完成度 | [目前實作 vs 要件](docs/implementation-vs-requirements-v2.md) |
| 查看部署方式 | [部署 / 執行指南](docs/deployment.zh-Hant.md) |
| 查看所有文檔 | [文檔索引](docs/document-index.zh-Hant.md) |

## 文檔中心

| 文檔 | 英文 | 日文 | 繁體中文 |
| --- | --- | --- | --- |
| 文檔索引 | [EN](docs/document-index.md) | [JA](docs/document-index.ja.md) | [ZH](docs/document-index.zh-Hant.md) |
| 部署 / 執行指南 | [EN](docs/deployment.md) | [JA](docs/deployment.ja.md) | [ZH](docs/deployment.zh-Hant.md) |
| 架構審查備忘 | [EN](docs/architecture-review-notes.md) | [JA](docs/architecture-review-notes.ja.md) | [ZH](docs/architecture-review-notes.zh-Hant.md) |
| 實作完成度 | [EN](docs/implementation-vs-requirements-v2.en.md) | [JA](docs/implementation-vs-requirements-v2.ja.md) | [ZH](docs/implementation-vs-requirements-v2.md) |
| 要件定義書 | [EN](docs/requirements-spec.en.md) | [JA](docs/requirements-spec.ja.md) | [ZH](docs/requirements-spec.zh-Hant.md) |
| AI 使用紀錄 | [EN](docs/ai-log.md) | [JA](docs/ai-log.ja.md) | [ZH](docs/ai-log.zh-Hant.md) |
| AI 對話來源 | [EN](docs/ai-conversation-source.en.md) | [JA](docs/ai-conversation-source.ja.md) | [ZH](docs/ai-conversation-source.zh-Hant.md) |
| YOLO 影片測試 | [EN](docs/yolo-video-test.md) | [JA](docs/yolo-video-test.ja.md) | [ZH](docs/yolo-video-test.zh-Hant.md) |
| 提交素材與資料來源 | [EN](docs/submission-assets.md) | [JA](docs/submission-assets.ja.md) | [ZH](docs/submission-assets.zh-Hant.md) |
| 公開發布說明 | [EN](docs/public-release-notes.md) | [JA](docs/public-release-notes.ja.md) | [ZH](docs/public-release-notes.zh-Hant.md) |

原始來源：[要件 PDF](docs/requirements_spec.md.pdf)、[AI 對話 PDF](docs/Claude_geminiconversation.md.pdf)、[AI 對話 raw 抽出 Markdown](docs/ai-conversation-source.md)。

## 包含內容

| 領域 | 內容 |
| --- | --- |
| API | FastAPI、Pydantic 驗證、`source_event_id` 冪等接收、列表 / 詳細 / 狀態 API |
| 即時推送 | SSE 推送 `incident.created` / `incident.status_updated` |
| 持久化 | SQLAlchemy + SQLite，透過 Docker volume 保存資料 |
| 儀表板 | Vanilla JS、EN/JA/ZH、篩選說明、分頁、tooltip、可退回狀態操作 |
| 示範運用 | Docker Compose、seed script、Swagger UI、同梱 demo DB |
| YOLO 擴充 | download / prepare / train / infer / API post pipeline |
| 證據資料 | tests、screenshots、AI logs、要件比較、公開發布說明 |

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

- API 文件: `http://localhost:8000/docs`
- 儀表板: `http://localhost:8000/ui/`

產生示範事件:

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

提交用示範最短確認方式:

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
