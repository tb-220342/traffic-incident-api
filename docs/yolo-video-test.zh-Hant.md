# YOLO 影片測試資料

語言: [English](yolo-video-test.md) | [日本語](yolo-video-test.ja.md) | [繁體中文](yolo-video-test.zh-Hant.md)

回到 [Document Index](document-index.zh-Hant.md)

本機 YOLO 影片測試資料夾:

```text
<DATA_ROOT>\yolovideotest
```

`<DATA_ROOT>` 是 repository 外部的 ML data directory。未設定 `TRAFFIC_DATASETS_ROOT` 時，預設是 `../traffic-incident-data`。

> [!NOTE]
> public repository 保留 video test workflow 與 demo DB 內已驗證 API rows，但不再散布 dataset 派生 MP4 或 YOLO weight。

public GitHub release 不 commit dataset 派生 MP4。若要執行 YOLO demo，請把檔案保留或重新生成在 `<DATA_ROOT>\yolovideotest`。

裡面有兩個短輸入影片:

- `mio_vehicle_short.mp4`: 由 MIO-TCD localization validation 圖片產生，用於車輛偵測 / tracking 檢查。
- `rdd_damage_short.mp4`: 由 RDD2022 validation 圖片產生，用於路面異常 / debris 檢查。

已產生的 YOLO box 標記影片:

- `mio_vehicle_short.boxes.mp4`
- `rdd_damage_short.boxes.mp4`

兩個影片都約 8 秒。它們不是原始連續道路影片，而是由既有圖片資料集組成的短測試 clip。這樣方便固定測試，但也會暴露模型品質問題：車輛 tracking 在非連續影像上不穩，RDD damage 偵測可能出現低信心、漏檢或 box 不夠準的情況。

## Dry-Run 指令

車輛 / 停止車輛模式:

```powershell
cd <repo-root>
.\.venv\Scripts\python.exe -m yolo.infer_video `
  --mode vehicle `
  --weights <DATA_ROOT>\runs\mio-localization\mio-stage2-20260421-234643\weights\best.pt `
  --source <DATA_ROOT>\yolovideotest\mio_vehicle_short.mp4 `
  --base-url http://127.0.0.1:8000 `
  --camera-id CAM-YOLO-VIDEO-MIO `
  --highway-id E1 `
  --confidence 0.25 `
  --stop-seconds 1 `
  --cooldown-seconds 5 `
  --annotated-output <DATA_ROOT>\yolovideotest\mio_vehicle_short.boxes.mp4 `
  --dry-run
```

路面異常 / debris 模式:

```powershell
cd <repo-root>
.\.venv\Scripts\python.exe -m yolo.infer_video `
  --mode damage `
  --weights <DATA_ROOT>\runs\rdd2022\rdd-stage2-20260421-234643\weights\best.pt `
  --source <DATA_ROOT>\yolovideotest\rdd_damage_short.mp4 `
  --base-url http://127.0.0.1:8000 `
  --camera-id CAM-YOLO-VIDEO-RDD `
  --highway-id E1 `
  --confidence 0.25 `
  --frame-stride 1 `
  --cooldown-seconds 5 `
  --annotated-output <DATA_ROOT>\yolovideotest\rdd_damage_short.boxes.mp4 `
  --dry-run
```

如果要真的把偵測事件送進 API 並顯示在 Dashboard，移除 `--dry-run`。

## 已驗證 API 寫入 demo

啟動 API，並先停止 seed，這樣比較容易找到 YOLO 寫入的資料。

```powershell
cd <repo-root>
docker compose up -d --build
docker compose stop seed
```

不加 `--dry-run` 執行 RDD clip。

```powershell
.\.venv\Scripts\python.exe -m yolo.infer_video `
  --mode damage `
  --weights <DATA_ROOT>\runs\rdd2022\rdd-stage2-20260421-234643\weights\best.pt `
  --source <DATA_ROOT>\yolovideotest\rdd_damage_short.mp4 `
  --base-url http://127.0.0.1:8000 `
  --camera-id CAM-YOLO-VIDEO-RDD `
  --highway-id E1 `
  --confidence 0.25 `
  --frame-stride 1 `
  --cooldown-seconds 5 `
  --annotated-output <DATA_ROOT>\yolovideotest\rdd_damage_short.boxes.mp4
```

查詢 YOLO 寫入的 event。

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/events?camera_id=CAM-YOLO-VIDEO-RDD&sort_by=detected_at&order=desc&limit=10&offset=0' |
  ConvertTo-Json -Depth 12
```

packaged demo database 中已驗證的 record:

- `CAM-YOLO-VIDEO-RDD:DEBRIS:20260426T141118178311:a44c447c`
- `CAM-YOLO-VIDEO-RDD:DEBRIS:20260426T141119377223:8545637c`
