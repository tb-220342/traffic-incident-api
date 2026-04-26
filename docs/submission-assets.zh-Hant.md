# Public 提交用資產與資料來源

這份文件說明 repo 內包含哪些非程式 demo 資產，以及這些資料從哪裡來。

## 已放入 Repo 的內容

- API、Dashboard、seed script、tests、YOLO pipeline 原始碼。
- `model-artifacts/*/args.yaml`, `results.csv`, `results.png`, `confusion_matrix.png`: 已選訓練 run 的設定與結果摘要。
- `demo-data/incidents-demo.db`: 展示用 SQLite demo database snapshot。
- `docs/public-release-notes*.md`: dataset 派生 artifact 的 public release compliance notes。

## 刻意不放入的內容

- 原始訓練圖片與轉換後訓練圖片不放入 repo，因為容量很大，預設保留在 `<DATA_ROOT>`。
- dataset 派生的 YOLO demo MP4 不放入 public repository。
- 由 dataset frame 生成的 YOLO snapshot 不放入 public repository。
- 訓練完成的 `.pt` weight 由 MIO-TCD、RDD2022、TRANCOS 派生，因此不放入 public repository。
- intermediate epoch checkpoint 不放入 repo。`<DATA_ROOT>\runs` 底下共有 76 個 `.pt` checkpoint，合計約 1.39 GB。
- cache、virtual environment、本地 secret 不放入 repo。

## 資料來源

- MIO-TCD Localization: `yolo/config.py` 設定的官方 archive 為 `https://tcd.miovision.com/static/dataset/MIO-TCD-Localization.tar`。
- RDD2022 / CRDDC2022: `yolo/config.py` 設定的官方 archive 為 `https://bigdatacup.s3.ap-northeast-1.amazonaws.com/2022/CRDDC2022/RDD2022/RDD2022.zip`。
- TRANCOS: `yolo/config.py` 設定的官方 package 為 `https://universidaddealcala-my.sharepoint.com/:u:/g/personal/gram_uah_es/Eank6osXQgxEqa-1bb0nVsoBc3xO4XDwENc_g0nc6t58BA?Download=1`。

這兩段短影片是由 validation 圖片生成的 demo 影片，不是原始連續道路影片。這樣方便重複測試，也能清楚展示 YOLO 品質問題：非連續影格上的 tracking 較弱，路面損傷 box 可能出現低信心、漏檢或框位不完全貼合。

公開發布時，這些 clip 與 annotated output 只作為本機 artifact 保留在:

```text
<DATA_ROOT>\yolovideotest
```

## Demo DB 來源

`demo-data/incidents-demo.db` 是展示用資料。打包當下共有 7,889 筆，其中 seed event 7,878 筆、manual / Codex 驗證 event 6 筆、legacy / manual row 3 筆、由 `CAM-YOLO-VIDEO-RDD` 真正透過 YOLO 保存的 event 2 筆。它不是實際事故資料；只有 `CAM-YOLO-VIDEO-RDD` 這 2 筆是由 YOLO video pipeline 產生。

已驗證的 YOLO 寫入:

- `CAM-YOLO-VIDEO-RDD:DEBRIS:20260426T141118178311:a44c447c`，confidence `0.3328`。
- `CAM-YOLO-VIDEO-RDD:DEBRIS:20260426T141119377223:8545637c`，confidence `0.6701`。

這些寫入時生成的 snapshot 在本機仍可保存，但不放入 public repository。
