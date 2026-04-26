# Public Submission Assets and Data Sources

Language: [English](submission-assets.md) | [日本語](submission-assets.ja.md) | [繁體中文](submission-assets.zh-Hant.md)

Back to [Document Index](document-index.md)

This document explains which non-code demo artifacts are included in the repository and where their data came from.

> [!NOTE]
> The public repository includes reproducibility evidence and demo data, not raw training assets or trained weights.

## Included In The Repository

- Source code for the API, dashboard, seed script, tests, and YOLO pipeline.
- `model-artifacts/*/args.yaml`, `results.csv`, `results.png`, `confusion_matrix.png`: training configuration and summary metrics for the selected runs.
- `demo-data/incidents-demo.db`: local SQLite demo database snapshot for presentation.
- `docs/public-release-notes*.md`: public-release compliance notes for dataset-derived artifacts.

## Excluded Intentionally

- Raw and prepared training images are not included because they are large and should stay under `<DATA_ROOT>`.
- Dataset-derived YOLO demo MP4 files are not included in the public repository.
- YOLO snapshots generated from dataset frames are not included in the public repository.
- Trained `.pt` weights are not included in the public repository because they are derived from MIO-TCD, RDD2022, and TRANCOS.
- Intermediate epoch checkpoints are not included. There are 76 `.pt` checkpoint files under `<DATA_ROOT>\runs`, totaling about 1.39 GB.
- Caches, virtual environments, and local secrets are excluded.

## Data Sources

- MIO-TCD Localization: official archive configured in `yolo/config.py` as `https://tcd.miovision.com/static/dataset/MIO-TCD-Localization.tar`.
- RDD2022 / CRDDC2022: official archive configured in `yolo/config.py` as `https://bigdatacup.s3.ap-northeast-1.amazonaws.com/2022/CRDDC2022/RDD2022/RDD2022.zip`.
- TRANCOS: official package configured in `yolo/config.py` as `https://universidaddealcala-my.sharepoint.com/:u:/g/personal/gram_uah_es/Eank6osXQgxEqa-1bb0nVsoBc3xO4XDwENc_g0nc6t58BA?Download=1`.

The two short video clips are derived demo clips generated from validation images, not original continuous road videos. This is useful for a repeatable demo and also makes YOLO quality limitations visible, especially weak tracking on non-continuous image sequences and imperfect low-confidence road-damage boxes.

For public release, those clips and their annotated outputs remain local-only under:

```text
<DATA_ROOT>\yolovideotest
```

## Demo Database Source

`demo-data/incidents-demo.db` is demonstration data. At packaging time it contains 7,889 rows: 7,878 seed events, 6 manual/Codex verification events, 3 legacy/manual rows, and 2 YOLO-generated persisted events from `CAM-YOLO-VIDEO-RDD`. It is not a database of real incidents; only the two `CAM-YOLO-VIDEO-RDD` rows were produced by the YOLO video pipeline.

The verified YOLO writes were:

- `CAM-YOLO-VIDEO-RDD:DEBRIS:20260426T141118178311:a44c447c`, confidence `0.3328`.
- `CAM-YOLO-VIDEO-RDD:DEBRIS:20260426T141119377223:8545637c`, confidence `0.6701`.

The snapshots for these writes were generated locally but are excluded from the public repository.
