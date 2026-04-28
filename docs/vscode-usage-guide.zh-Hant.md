# VSCode 詳細使用說明

[返回文檔索引](document-index.zh-Hant.md) | [專案 README](../README.zh-Hant.md)

> [!NOTE]
> 這份文件是給開發者或面試前自查使用的 VSCode 操作手冊。部署給面試官時仍推薦使用 `docker compose up -d --build`。

## 1. 使用目的

這個專案可以用 VSCode 做以下事情：

- 閱讀 FastAPI 後端程式碼與資料模型。
- 啟動本地 API server。
- 開啟 Swagger UI 測試 `POST /events`、`GET /events`、`PATCH /events/{id}/status`。
- 查看 Dashboard 是否能收到 SSE 即時推送。
- 執行 pytest。
- 查看 SQLite DB 內容。
- 執行 seed script 或 YOLO-to-API demo。

## 2. 前置條件

建議安裝：

| 工具 | 用途 |
| --- | --- |
| VSCode | 開發與閱讀程式碼 |
| Python 3.11 | 執行 FastAPI 與 pytest |
| Docker Desktop | 用 Docker Compose 一鍵啟動 demo |
| Git | clone / pull / push repository |

建議 VSCode extension：

| Extension | 用途 |
| --- | --- |
| Python | Python interpreter、debug、test discovery |
| Pylance | 型別提示與跳轉 |
| Docker | 查看 container、image、logs |
| SQLite Viewer 或 SQLite | 檢查 `data/incidents.db` 或 `demo-data/incidents-demo.db` |
| REST Client | 可選，用 `.http` 文件手動測 API |

## 3. 開啟專案

```powershell
cd <repo-root>
code .
```

如果是從 GitHub clone：

```powershell
git clone https://github.com/tb-220342/traffic-incident-api.git
cd traffic-incident-api
code .
```

`<repo-root>` 代表 repository 根目錄，不是固定本機路徑。

## 4. 選擇 Python Interpreter

在 VSCode：

1. 按 `Ctrl+Shift+P`。
2. 輸入 `Python: Select Interpreter`。
3. 選擇 `<repo-root>\.venv\Scripts\python.exe`。

如果 `.venv` 尚未建立：

```powershell
cd <repo-root>
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

若要跑 YOLO / ML 相關 script，再安裝：

```powershell
.\.venv\Scripts\pip install -r requirements-ml.txt
```

## 5. 建議的 VSCode Terminal

打開 VSCode terminal：

```text
Terminal -> New Terminal
```

確認目前位置：

```powershell
pwd
```

應該位於 `<repo-root>`。所有 README 指令預設都從 `<repo-root>` 執行。

## 6. 用 Docker Compose 啟動

這是推薦給面試官與 demo 的方式。

```powershell
docker compose up -d --build
docker compose ps
```

打開：

- API health: `http://127.0.0.1:8000/health`
- Swagger UI: `http://127.0.0.1:8000/docs`
- Dashboard: `http://127.0.0.1:8000/ui/`

如果要手動測試 API，建議先停掉 seed，避免畫面一直新增 fake event：

```powershell
docker compose stop seed
```

停止整套：

```powershell
docker compose down
```

## 7. 用本地 Python 啟動

適合 debug 與加 breakpoint。

```powershell
cd <repo-root>
.\.venv\Scripts\uvicorn app.main:app --reload
```

打開：

- Swagger UI: `http://127.0.0.1:8000/docs`
- Dashboard: `http://127.0.0.1:8000/ui/`

若 port 被占用，先找出占用 process，或改用其他 port：

```powershell
.\.venv\Scripts\uvicorn app.main:app --reload --port 8001
```

## 8. VSCode Debug 設定

可以在 VSCode 建立 `.vscode/launch.json`，但這不是必須提交的檔案。手動設定如下：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI: uvicorn",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload"],
      "jinja": true,
      "justMyCode": true
    }
  ]
}
```

常用 breakpoint 位置：

| 檔案 | 適合觀察的點 |
| --- | --- |
| `app/routers/incidents.py` | request 如何進入 API endpoint |
| `app/services/incident_service.py` | idempotency、status transition、SSE broadcast |
| `app/repositories/incident_repository.py` | filter、sort、pagination、summary query |
| `app/services/sse_manager.py` | SSE connection 與 broadcast |

## 9. 執行測試

```powershell
cd <repo-root>
.\.venv\Scripts\pytest -q
```

目前預期：

```text
7 passed
```

若 VSCode Python extension 有啟用 testing：

1. 左側 Testing icon。
2. 選擇 pytest。
3. 點選 run all tests。

## 10. Swagger UI 驗收方式

打開：

```text
http://127.0.0.1:8000/docs
```

### 10.1 建立事件

使用 `POST /events`：

```json
{
  "source_event_id": "manual-vscode-check-001",
  "event_type": "DEBRIS",
  "severity": "HIGH",
  "description": "Manual VSCode verification payload",
  "confidence": 0.88,
  "camera_id": "CAM-VSCODE-001",
  "highway_id": "E1",
  "road_marker": "TK105+200",
  "lane_no": "2",
  "latitude": 35.6812,
  "longitude": 139.7671,
  "image_url": "https://example.com/manual-check.jpg",
  "detected_at": "2026-04-28T00:00:00Z",
  "extra_payload": {
    "created_by": "vscode-manual-test"
  }
}
```

預期：

- 首次建立回 `201`。
- 再送同一 payload 回 `200`，且 `meta.deduplicated=true`。
- 同一 `source_event_id` 但內容不同回 `409 Conflict`。

### 10.2 查詢事件

使用 `GET /events`：

```text
camera_id=CAM-VSCODE-001
sort_by=detected_at
order=desc
limit=10
offset=0
```

預期：

- `data` 中可看到剛建立的 event。
- `meta.total` 表示符合條件總數。
- `meta.critical_total` 表示符合條件中的 CRITICAL 數量。
- `meta.avg_delay_seconds_total` 表示符合條件的平均偵測延遲。
- `meta.latest_updated_at` 表示符合條件資料的最後更新時間。

### 10.3 更新狀態

使用 `PATCH /events/{incident_id}/status`：

```json
{
  "status": "ACKNOWLEDGED",
  "status_note": "Checked from VSCode guide"
}
```

預期：

- 回 `200`。
- `data.status` 變成 `ACKNOWLEDGED`。
- Dashboard 會透過 SSE 同步更新。

## 11. SSE 手動確認

在 PowerShell 可以用 curl 看 stream：

```powershell
curl.exe -N http://127.0.0.1:8000/events/stream
```

再用 Swagger `POST /events` 或 `PATCH /events/{id}/status`，SSE 視窗應看到：

```text
event: incident.created
data: ...
```

或：

```text
event: incident.status_updated
data: ...
```

## 12. Dashboard 確認

打開：

```text
http://127.0.0.1:8000/ui/
```

建議確認：

- 三語切換是否正常。
- Filter 區域是否只像搜尋條件，而不像新增/修改資料。
- KPI 是否跟 filter 條件連動。
- 分頁是否可上一頁、下一頁、指定頁數。
- Incident card 是否顯示攝影機、偵測時間、接收時間、偵測延遲、信心分數、source event id。
- Status 是否可往前或往回改。

## 13. SQLite 檢查方式

Docker Compose 啟動後，runtime DB 通常在：

```text
<repo-root>\data\incidents.db
```

展示用 DB snapshot：

```text
<repo-root>\demo-data\incidents-demo.db
```

可以用 VSCode SQLite extension 打開，也可以用 Python 快速查：

```powershell
@'
import sqlite3
conn = sqlite3.connect("data/incidents.db")
cur = conn.cursor()
for row in cur.execute("select id, source_event_id, event_type, severity, status, camera_id from incident_events order by ingested_at desc limit 5"):
    print(row)
conn.close()
'@ | .\.venv\Scripts\python.exe -
```

## 14. Seed Script

產生 fake events：

```powershell
.\.venv\Scripts\python.exe scripts\seed.py
```

用途：

- 讓 Dashboard 一直有新事件。
- 展示 SSE 即時更新。
- 測試 filter / pagination / KPI。

注意：

- 手動 API 驗收或 YOLO 寫入時，建議先停止 seed。
- Docker Compose 的 `seed` service 會自動產生事件。

## 15. YOLO-to-API Demo

YOLO 大型資料、影片、weight 不放在 public repository，預設放在 repository 外部：

```text
<DATA_ROOT>
```

可用環境變數指定：

```powershell
$env:TRAFFIC_DATASETS_ROOT="<DATA_ROOT>"
```

查詢目前資料根目錄：

```powershell
.\.venv\Scripts\python.exe -m yolo.download_datasets --show-paths
```

如果本機已準備好 RDD demo clip 與 weight，可執行：

```powershell
.\.venv\Scripts\python.exe -m yolo.infer_video `
  --mode damage `
  --weights <DATA_ROOT>\runs\rdd2022\rdd-stage2-20260421-234643\weights\best.pt `
  --source <DATA_ROOT>\yolovideotest\rdd_damage_short.mp4 `
  --base-url http://127.0.0.1:8000 `
  --camera-id CAM-YOLO-VIDEO-RDD `
  --confidence 0.25 `
  --frame-stride 1 `
  --cooldown-seconds 5 `
  --annotated-output <DATA_ROOT>\yolovideotest\rdd_damage_short.boxes.mp4
```

查詢 YOLO 寫入：

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/events?camera_id=CAM-YOLO-VIDEO-RDD&sort_by=detected_at&order=desc&limit=10&offset=0' |
  ConvertTo-Json -Depth 12
```

## 16. Git 操作

查看目前修改：

```powershell
git status --short --branch
```

提交：

```powershell
git add .
git commit -m "Describe the change"
git push origin main
```

如果只是給面試官部署，面試官不需要 SSH key，可用 HTTPS clone。

## 17. 常見問題

| 問題 | 處理方式 |
| --- | --- |
| `uvicorn` 找不到 | 確認已選 `.venv` interpreter，並安裝 `requirements.txt`。 |
| `port 8000 already in use` | 停掉既有 server，或改 `--port 8001`。 |
| Dashboard 沒資料 | 確認 API 有啟動，或跑 seed script。 |
| SSE 沒更新 | 確認 browser 沒阻擋、API log 無錯誤、`/events/stream` 可連線。 |
| `POST /events` 回 `409` | 同一 `source_event_id` 已存在但 payload 不同，換新的 `source_event_id`。 |
| Docker DB 沒保留 | 確認 `data/` volume mount 存在，不要刪掉 `data/incidents.db`。 |
| YOLO 找不到資料 | 設定 `TRAFFIC_DATASETS_ROOT` 或重新執行資料準備 script。 |

## 18. 面試前 VSCode 檢查清單

- `git status --short --branch` 是乾淨的。
- `.\.venv\Scripts\pytest -q` 是 `7 passed`。
- `docker compose up -d --build` 可以啟動。
- `http://127.0.0.1:8000/docs` 可以打開。
- `http://127.0.0.1:8000/ui/` 可以打開。
- `POST /events` 可以建立事件。
- `PATCH /events/{id}/status` 可以更新狀態。
- Dashboard 能即時看到新 event 或 status 更新。
- README、architecture review notes、deployment guide 都能從 document index 找到。
