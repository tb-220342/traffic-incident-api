# 部署 / 執行指南

這個專案是面試課題用的 demo service。給面試官重現時，推薦使用本機 Docker Compose。

表記:

- `<repo-root>` 代表 reviewer clone 這個 repository 的目錄。
- `<DATA_ROOT>` 代表 repository 外部的 ML data directory。預設是 `../traffic-incident-data`，可用 `TRAFFIC_DATASETS_ROOT` 更改。

## 推薦 Demo 部署方式

```powershell
cd <repo-root>
docker compose up -d --build
docker compose ps
```

開啟:

- API health: `http://127.0.0.1:8000/health`
- Swagger API docs: `http://127.0.0.1:8000/docs`
- Dashboard UI: `http://127.0.0.1:8000/ui/`

Docker stack 會啟動:

- `api`: FastAPI application，port `8000`
- `seed`: optional fake-event generator，會把 demo event 送進 API

如果要手動測 API 或 YOLO，建議先停止 seed，這樣比較容易找到新寫入的測試資料。

```powershell
docker compose stop seed
```

停止整套:

```powershell
docker compose down
```

## 本機 Python 執行

```powershell
cd <repo-root>
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\uvicorn app.main:app --reload
```

這適合開發。面試官要重現時，Docker Compose 更簡單。

## 資料庫持久化

Docker Compose 會把 `./data` mount 進 container，所以 SQLite 會保存在:

```text
<repo-root>\data\incidents.db
```

repo 也包含展示用 demo database snapshot:

```text
demo-data/incidents-demo.db
```

這個 snapshot 包含 seed/demo records，以及 `CAM-YOLO-VIDEO-RDD` 由 YOLO 真正寫入的 2 筆 `DEBRIS` event。

## YOLO 寫入 API / DB Demo

public GitHub release 不包含 dataset 派生的 MP4 clip、YOLO snapshot、或訓練完成的 `.pt` weight。若要執行這個 demo，請使用本機 `<DATA_ROOT>` 底下的 artifact，或用 `yolo/` 內的 script 重新生成。packaged demo database 仍保留 2 筆已驗證的 YOLO 生成 record，因此即使不再散布原始媒體或權重，面試官也能確認 API/UI 行為。

啟動 API 並停止 seed:

```powershell
docker compose up -d --build
docker compose stop seed
```

不加 `--dry-run` 執行 RDD clip:

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

查詢寫入結果:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/events?camera_id=CAM-YOLO-VIDEO-RDD&sort_by=detected_at&order=desc&limit=10&offset=0' |
  ConvertTo-Json -Depth 12
```

## 提交前測試

```powershell
.\.venv\Scripts\pytest -q
```

預期結果:

```text
7 passed
```

## 如果要正式產品化

正式 deployment 需要追加或替換:

- SQLite 換成 PostgreSQL。
- 加入 API key 或 JWT 等 API authentication。
- snapshot/image 改存 object storage，不放本地磁碟。
- 加入 rate limiting、audit log、metrics、observability。
- API 與 detector worker 分離，並用 ingestion retry queue。

這些是本次面試課題範圍外，但目前的程式分層已保留清楚的擴充點。
