# YOLO 動画テストクリップ

ローカルの YOLO 動画テスト用フォルダ:

```text
D:\Datasets\traffic-incident\yolovideotest
```

public GitHub release では、dataset 由来の MP4 file は repo に commit しません。YOLO demo を実行する場合は、`D:\Datasets\traffic-incident\yolovideotest` にローカル保持するか、再生成してください。

含まれる短い入力動画:

- `mio_vehicle_short.mp4`: MIO-TCD localization の validation 画像から生成した車両検知 / tracking 確認用動画。
- `rdd_damage_short.mp4`: RDD2022 の validation 画像から生成した路面異常 / debris 確認用動画。

生成済みの box 付き動画:

- `mio_vehicle_short.boxes.mp4`
- `rdd_damage_short.boxes.mp4`

どちらも約 8 秒です。元動画ではなく既存の画像データセットから作った短い確認用 clip なので、連続映像としての tracking 品質は弱く見えます。ただし、面接 demo ではその弱点も説明材料になります。RDD 側では低 confidence、漏れ、box のずれなども確認しやすいです。

## Dry-Run コマンド

車両 / 停止車両 mode:

```powershell
cd D:\Projects\traffic-incident-api
.\.venv\Scripts\python.exe -m yolo.infer_video `
  --mode vehicle `
  --weights D:\Datasets\traffic-incident\runs\mio-localization\mio-stage2-20260421-234643\weights\best.pt `
  --source D:\Datasets\traffic-incident\yolovideotest\mio_vehicle_short.mp4 `
  --base-url http://127.0.0.1:8000 `
  --camera-id CAM-YOLO-VIDEO-MIO `
  --highway-id E1 `
  --confidence 0.25 `
  --stop-seconds 1 `
  --cooldown-seconds 5 `
  --annotated-output D:\Datasets\traffic-incident\yolovideotest\mio_vehicle_short.boxes.mp4 `
  --dry-run
```

路面異常 / debris mode:

```powershell
cd D:\Projects\traffic-incident-api
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
  --annotated-output D:\Datasets\traffic-incident\yolovideotest\rdd_damage_short.boxes.mp4 `
  --dry-run
```

API に event を送って Dashboard に表示したい場合は `--dry-run` を外します。

## API 書き込み確認済み demo

seed を止めた状態で API を起動すると、YOLO が書き込んだ record を見つけやすくなります。

```powershell
cd D:\Projects\traffic-incident-api
docker compose up -d --build
docker compose stop seed
```

RDD clip を `--dry-run` なしで実行します。

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

書き込まれた event を確認します。

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/events?camera_id=CAM-YOLO-VIDEO-RDD&sort_by=detected_at&order=desc&limit=10&offset=0' |
  ConvertTo-Json -Depth 12
```

packaged demo database で確認済みの record:

- `CAM-YOLO-VIDEO-RDD:DEBRIS:20260426T141118178311:a44c447c`
- `CAM-YOLO-VIDEO-RDD:DEBRIS:20260426T141119377223:8545637c`
