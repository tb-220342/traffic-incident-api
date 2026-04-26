# デプロイ / 実行ガイド

このプロジェクトは面接課題の demo service として作っています。review 用の推奨実行方法は、ローカル PC 上の Docker Compose です。

表記:

- `<repo-root>` は reviewer がこの repository を clone した directory です。
- `<DATA_ROOT>` は repository 外の ML data directory です。default は `../traffic-incident-data` で、`TRAFFIC_DATASETS_ROOT` で変更できます。

## 推奨 demo deployment

```powershell
cd <repo-root>
docker compose up -d --build
docker compose ps
```

開く URL:

- API health: `http://127.0.0.1:8000/health`
- Swagger API docs: `http://127.0.0.1:8000/docs`
- Dashboard UI: `http://127.0.0.1:8000/ui/`

Docker stack で起動する service:

- `api`: port `8000` の FastAPI application
- `seed`: demo event を API に送る optional fake-event generator

手動 API 確認や YOLO demo を行う場合は、seed を止めると新しい record を見つけやすくなります。

```powershell
docker compose stop seed
```

全体を停止:

```powershell
docker compose down
```

## Python でのローカル実行

```powershell
cd <repo-root>
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\uvicorn app.main:app --reload
```

開発には便利ですが、面接官が再現する場合は Docker Compose の方が簡単です。

## database persistence

Docker Compose は `./data` を container に mount するため、SQLite は以下に保存されます。

```text
<repo-root>\data\incidents.db
```

提出確認用の demo database snapshot も repo に含めています。

```text
demo-data/incidents-demo.db
```

この snapshot には seed/demo record と、`CAM-YOLO-VIDEO-RDD` から実際に YOLO が保存した `DEBRIS` event 2 件が含まれます。

## YOLO から API / DB へ書き込む demo

public GitHub release では、dataset 由来の MP4 clip、YOLO snapshot、学習済み `.pt` weight は含めません。この demo を実行する場合は、ローカルの `<DATA_ROOT>` 配下にある artifact を使うか、`yolo/` 配下の script で再生成します。packaged demo database には確認済みの YOLO 由来 record が 2 件残っているため、元 media や weight を再配布しなくても API/UI の挙動は確認できます。

API を起動し、seed を止めます。

```powershell
docker compose up -d --build
docker compose stop seed
```

RDD clip を `--dry-run` なしで実行します。

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

書き込まれた record を確認します。

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/events?camera_id=CAM-YOLO-VIDEO-RDD&sort_by=detected_at&order=desc&limit=10&offset=0' |
  ConvertTo-Json -Depth 12
```

## 提出前 test

```powershell
.\.venv\Scripts\pytest -q
```

期待結果:

```text
7 passed
```

## 本番化する場合

本番 deployment では、以下を追加または変更します。

- SQLite を PostgreSQL に置き換える。
- API key または JWT などの API authentication を追加する。
- snapshot/image を local disk ではなく object storage に保存する。
- rate limiting、audit log、metrics、observability を追加する。
- API と detector worker を分離し、ingestion retry queue を使う。

これらは今回の面接課題の scope 外ですが、現在の構成は拡張しやすい分離にしています。
