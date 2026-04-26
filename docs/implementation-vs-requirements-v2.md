# 目前實作 vs 要件 v2

語言: [English](implementation-vs-requirements-v2.en.md) | [日本語](implementation-vs-requirements-v2.ja.md) | [繁體中文](implementation-vs-requirements-v2.md)

回到 [Document Index](document-index.zh-Hant.md)

最後更新：2026-04-26（Asia/Tokyo）

> [!IMPORTANT]
> 目前狀態：必做後端範圍已完成，demo 加值項已完成，YOLO 整合以 public-safe artifact 形式達到 demo-ready。

## 驗證快照

- `pytest`：`7 passed`
- `docker compose up -d --build`：已實測通過
- Docker `/health`：`200 OK`
- `POST /events`：
  - 首次建立：`201 Created`
  - 相同 `source_event_id` 且內容相同：`200 OK` + `meta.deduplicated=true`
  - 相同 `source_event_id` 但內容衝突：`409 Conflict`
- `GET /events/stream`：`200 text/event-stream`
- 本輪補齊：
  - `latitude` / `longitude` 改為可選
  - optional 欄位回應時明確回 `null`
  - 所有時間欄位統一序列化為 `UTC ISO 8601` + `Z`
  - 補上 `.dockerignore`，Docker build context 從約 `5.03 GB` 降到約 `13.47 kB`

## 完成度清單

### P0 必做

| 項目 | 狀態 | 說明 / 證據 |
| --- | --- | --- |
| `POST /events` 接收事件 | 完成 | 已支援 validation、idempotent ingest、`source_event_id` dedup、`201/200/409` 契約 |
| `GET /events` 列表查詢 | 完成 | 已支援 `severity`、`event_type`、`status`、`camera_id`、`highway_id`、sort、pagination |
| `GET /events/{id}` 單筆查詢 | 完成 | 已支援 `404 NOT_FOUND` |
| `PATCH /events/{id}/status` | 完成 | 已支援合法工作流程、誤操作退回、no-op，未支援跳轉會回 `409 INVALID_STATUS_TRANSITION` |
| `GET /events/stream` SSE | 完成 | 已支援 `incident.created`、`incident.status_updated`、keep-alive |
| SQLite 持久化 | 完成 | 本地與 Docker 都使用 SQLite，並保留 migration 邏輯 |
| 統一成功 / 錯誤回應格式 | 完成 | 已有 `success/data/meta` 與 `success/error` 契約 |
| `UTC ISO 8601` 時間欄位 | 完成 | `detected_at`、`ingested_at`、`updated_at` 皆正規化成 UTC 並輸出 `Z` |
| 基本結構化日誌 | 完成 | 已記錄 request、SSE connect/disconnect、incident create / dedup / status update |
| README 與 AI log | 完成 | `README.md`、`docs/ai-log.md` 已存在 |

### P1 展示加值

| 項目 | 狀態 | 說明 / 證據 |
| --- | --- | --- |
| `docker compose up` 一鍵啟動 | 完成 | 2026-04-23 已實測成功；`api` 與 `seed` 容器都能正常啟動 |
| Seed script 持續送事件 | 完成 | `scripts/seed.py` 已驗證可透過 Docker `seed` service 持續送事件 |
| Dashboard 即時顯示事件 | 完成 | `ui/index.html` 已串 SSE 契約並展示搜尋結果、`Source Event ID`、Location、Delay、`status_note` |
| Dashboard 三語切換 | 完成 | 已支援 English / 日本語 / 中文，切換後靜態文字、事件標籤、狀態按鈕會同步更新 |
| Dashboard 易用性改善 | 完成 | 已補搜尋專用 Filter 說明、指定頁數跳轉、每頁筆數、事件標題多語化、enum 下拉、手動輸入 / 範圍搜尋、欄位 tooltip、狀態變更前確認 |
| KPI / Detection delay 顯示 | 完成 | 顯示筆數、重大事件、平均延遲都以「本頁 / 符合總數」呈現，並顯示搜尋時間與 DB 更新時間 |

### P2 YOLO / 視訊整合

| 項目 | 狀態 | 說明 / 證據 |
| --- | --- | --- |
| `infer_video.py` 轉事件並送 API | 完成 | 2026-04-26 已用 `rdd_damage_short.mp4` 驗證，`CAM-YOLO-VIDEO-RDD` 寫入 2 筆 `DEBRIS` event |
| 訓練權重本機保留 | 完成 | `MIO`、`RDD2022`、`TRANCOS` 權重保留在 `<DATA_ROOT>\\runs`；public repo 不包含 `.pt` weight，`model-artifacts/` 只保留 training summary |
| 訓練資料 / 快取放在 repo 外 | 完成 | 預設使用 `../traffic-incident-data`，也可用 `TRAFFIC_DATASETS_ROOT` 指定任意磁碟或 workspace |
| 端到端影片驗證 | 可 demo / 待人工看品質 | 短版測試影片與 YOLO box 輸出保留在 `<DATA_ROOT>\\yolovideotest`；public repo 排除 dataset 派生 MP4/snapshot，但 demo DB 保留已驗證的 API event |

## 目前仍建議你人工確認的點

- Dashboard 視覺與互動：
  - 我已驗 API、SSE、欄位對齊，但這一輪沒有替你做瀏覽器畫面審美與長時間互動巡檢。
- YOLO 準確率：
  - pipeline 與權重已在，但是否「夠用」要用你的實際路段 / 影片素材來看 false positive / false negative。
- SSE 延遲：
  - 已做 smoke test，未額外做專門的 latency benchmark harness。

## 這一輪補完的實作項目

- 把 `latitude` / `longitude` 改成真正可選，與 `requirements v2` 對齊。
- API 回傳的 optional 欄位改成明確回 `null`，避免欄位消失造成前端或驗收誤判。
- 所有時間欄位改為標準 UTC 序列化，回應會帶 `Z`。
- 補 `.dockerignore`，讓 Docker build 不再把 `.venv`、權重、資料庫等大量內容打包進 context。
- 補一條 `pytest` 測試，確認「無座標事件」可正常建立。

## 使用方式

### A. Docker 跑整套

```powershell
cd <repo-root>
docker compose up -d --build
docker compose ps
```

開啟：

- Swagger：`http://127.0.0.1:8000/docs`
- Dashboard：`http://127.0.0.1:8000/ui/`

如果你想先做乾淨的手動測試，不想讓 seed 持續灌資料：

```powershell
docker compose stop seed
```

結束後可關掉：

```powershell
docker compose down
```

### B. 本地直接跑 API

```powershell
cd <repo-root>
.\.venv\Scripts\uvicorn app.main:app --reload
```

### C. 跑測試

```powershell
cd <repo-root>
.\.venv\Scripts\pytest
```

## 檢驗方式

### 1. 最快的人工驗收路徑

1. 啟動 Docker stack。
2. 打開 `http://127.0.0.1:8000/ui/`，確認 Dashboard 會隨 seed 事件即時更新。
3. 在 Dashboard 右上角切換 `EN / 日本語 / 中文`，確認畫面文字、事件標題、事件標籤與狀態按鈕會跟著更新。
4. 確認 Filter 區域看起來是搜尋專用，不像新增或修改資料的輸入區。
5. 確認上方 KPI 會跟目前篩選條件連動，顯示為「本頁 / 符合總數」，且有搜尋時間與 DB 更新時間。
6. 切換每頁筆數，輸入指定頁數，按前往 / 上一頁 / 下一頁，確認顯示範圍與卡片內容會更新。
7. 測試攝像頭 / 位置、Camera ID、Source Event ID、偵測 / 接收時間、延遲秒數、信心分數的詳細搜尋。
8. 滑鼠移到標籤與欄位名稱上，確認重要度、事件類型、狀態、偵測延遲、位置、座標、Source ID、Camera ID 都有補充說明。
9. 打開 `http://127.0.0.1:8000/docs`，照下面的 payload 手動測 API。
10. 另開一個 PowerShell 看 SSE：

```powershell
curl.exe -N http://127.0.0.1:8000/events/stream
```

你應該會看到：

- `event: incident.created`
- `event: incident.status_updated`

### 2. `POST /events` 成功建立

在 Swagger 的 `POST /events` 貼這個 body：

```json
{
  "source_event_id": "manual-check-001",
  "event_type": "DEBRIS",
  "severity": "HIGH",
  "description": "Manual verification payload",
  "confidence": 0.88,
  "camera_id": "CAM-MANUAL-001",
  "highway_id": "E1",
  "road_marker": "K10+500",
  "lane_no": "1",
  "detected_at": "2026-04-23T10:00:00+09:00"
}
```

預期：

- HTTP `201`
- `latitude` / `longitude` 為 `null`
- `meta.deduplicated = false`
- `detected_at` 會被正規化成 UTC，例如 `2026-04-23T01:00:00Z`

### 3. dedup 與 conflict

#### dedup

- 用完全相同的 body 再送一次

預期：

- HTTP `200`
- `meta.deduplicated = true`
- 回傳相同 `id`

#### conflict

- 保持 `source_event_id = manual-check-001`
- 只改 `severity` 或其他核心欄位

預期：

- HTTP `409`
- `error.code = DUPLICATE_CONFLICT`

### 4. `GET /events` 查詢 / 篩選 / 排序

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/events?severity=HIGH,CRITICAL&status=NEW&sort_by=severity&order=desc&limit=10&offset=0'
```

檢查：

- `meta.total`
- `meta.limit`
- `meta.offset`
- 回傳順序應符合 `CRITICAL > HIGH > MEDIUM > LOW`

### 5. `PATCH /events/{id}/status`

在 Swagger 或任意 API client：

- `NEW -> ACKNOWLEDGED`：應回 `200`
- 對同一事件再次送 `ACKNOWLEDGED`：應回 `200` 並 `meta.noop = true`
- `ACKNOWLEDGED -> RESOLVED`：應回 `200`
- `RESOLVED -> ACKNOWLEDGED` 或 `RESOLVED -> DISPATCHED`：可用於誤操作退回，應回 `200 OK`

同時在 SSE 視窗裡應看到：

- `event: incident.status_updated`

### 6. 看日誌

```powershell
docker compose logs -f api
```

你應該能看到這類訊息：

- `request_completed`
- `incident_created`
- `incident_deduplicated`
- `incident_status_updated`
- `sse_broadcast`

## YOLO 使用與檢驗方式

### 已可直接使用的權重

- MIO vehicle detector：
  - `<DATA_ROOT>\runs\mio-localization\mio-stage2-20260421-234643\weights\best.pt`
- RDD2022 damage detector：
  - `<DATA_ROOT>\runs\rdd2022\rdd-stage2-20260421-234643\weights\best.pt`
- TRANCOS calibration detector：
  - `<DATA_ROOT>\runs\trancos\trancos-full-20260421-013913\weights\best.pt`

### 車流 / 停車事件驗證

```powershell
cd <repo-root>
.\.venv\Scripts\python.exe -m yolo.infer_video `
  --mode vehicle `
  --weights <DATA_ROOT>\runs\mio-localization\mio-stage2-20260421-234643\weights\best.pt `
  --source <path-to-highway-video>.mp4 `
  --base-url http://127.0.0.1:8000
```

預期：

- 終端機輸出 `reported STOPPED_VEHICLE` 或 `reported CONGESTION`
- API 會出現新事件
- Dashboard 會插入新卡片
- snapshot 會落在 `<DATA_ROOT>\snapshots`

### 路面異常 / debris 驗證

```powershell
cd <repo-root>
.\.venv\Scripts\python.exe -m yolo.infer_video `
  --mode damage `
  --weights <DATA_ROOT>\runs\rdd2022\rdd-stage2-20260421-234643\weights\best.pt `
  --source <path-to-road-video>.mp4 `
  --base-url http://127.0.0.1:8000
```

預期：

- 終端機輸出 `reported DEBRIS`
- `/events?camera_id=CAM-YOLO-001` 可查到新資料

## 已驗證的主要檔案

- `app/main.py`
- `app/database.py`
- `app/models/incident.py`
- `app/schemas/incident.py`
- `app/services/incident_service.py`
- `app/services/sse_manager.py`
- `app/routers/incidents.py`
- `tests/test_incidents.py`
- `ui/index.html`
- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`
