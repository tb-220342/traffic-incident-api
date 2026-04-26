# Public 提出用アセットとデータ出典

言語: [English](submission-assets.md) | [日本語](submission-assets.ja.md) | [繁體中文](submission-assets.zh-Hant.md)

[Document Index](document-index.ja.md) に戻る

この文書は、リポジトリに含めたコード以外の demo アセットと、そのデータ出典を説明するものです。

> [!NOTE]
> public repository には再現性の evidence と demo data を含めていますが、raw training asset や trained weight は含めていません。

## リポジトリに含めたもの

- API、dashboard、seed script、test、YOLO pipeline の source code。
- `model-artifacts/*/args.yaml`, `results.csv`, `results.png`, `confusion_matrix.png`: 選択した学習 run の設定と結果サマリー。
- `demo-data/incidents-demo.db`: 発表確認用の SQLite demo database snapshot。
- `docs/public-release-notes*.md`: dataset 由来 artifact の public release compliance notes。

## 意図的に含めていないもの

- 生の学習画像と変換後の学習画像は、容量が大きいため含めていません。ローカルでは `<DATA_ROOT>` に置く前提です。
- dataset 由来の YOLO demo MP4 は public repository に含めていません。
- dataset frame から生成した YOLO snapshot は public repository に含めていません。
- 学習済み `.pt` weight は、MIO-TCD、RDD2022、TRANCOS 由来の artifact なので public repository に含めていません。
- intermediate epoch checkpoint は含めていません。`<DATA_ROOT>\runs` 配下には 76 個、合計約 1.39 GB の `.pt` checkpoint があります。
- cache、virtual environment、local secret は含めていません。

## データ出典

- MIO-TCD Localization: `yolo/config.py` に公式 archive として `https://tcd.miovision.com/static/dataset/MIO-TCD-Localization.tar` を設定。
- RDD2022 / CRDDC2022: `yolo/config.py` に公式 archive として `https://bigdatacup.s3.ap-northeast-1.amazonaws.com/2022/CRDDC2022/RDD2022/RDD2022.zip` を設定。
- TRANCOS: `yolo/config.py` に公式 package として `https://universidaddealcala-my.sharepoint.com/:u:/g/personal/gram_uah_es/Eank6osXQgxEqa-1bb0nVsoBc3xO4XDwENc_g0nc6t58BA?Download=1` を設定。

2 本の短い動画は、validation 画像から生成した demo 用クリップであり、元から連続撮影された道路動画ではありません。そのため再現性のある確認には便利ですが、非連続フレームでは tracking が弱いこと、路面損傷 box が低 confidence や位置ずれを起こし得ることも確認できます。

public release では、これらの clip と annotated output は以下の local-only artifact として扱います。

```text
<DATA_ROOT>\yolovideotest
```

## Demo DB の出典

`demo-data/incidents-demo.db` は demo 用データです。packaging 時点では 7,889 行あり、その内訳は seed event 7,878 件、manual / Codex verification event 6 件、legacy / manual row 3 件、`CAM-YOLO-VIDEO-RDD` から YOLO が保存した event 2 件です。実際の事故データではなく、YOLO video pipeline 由来なのは `CAM-YOLO-VIDEO-RDD` の 2 行のみです。

確認済みの YOLO 書き込み:

- `CAM-YOLO-VIDEO-RDD:DEBRIS:20260426T141118178311:a44c447c`、confidence `0.3328`。
- `CAM-YOLO-VIDEO-RDD:DEBRIS:20260426T141119377223:8545637c`、confidence `0.6701`。

これらの書き込み時に生成した snapshot は local にはありますが、public repository からは除外しています。
