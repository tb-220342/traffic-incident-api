# Public Release Notes

Language: [English](public-release-notes.md) | [日本語](public-release-notes.ja.md) | [繁體中文](public-release-notes.zh-Hant.md)

Back to [Document Index](document-index.md)

This repository is intended to be public on GitHub. For that reason, it does not include dataset-derived media files or trained model weights.

> [!CAUTION]
> This is a conservative compliance note for an interview submission. It is not legal advice, but it documents the publication choices made to avoid redistributing dataset-derived artifacts.

## License Review Summary

- MIO-TCD is published under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 on the official MIO-TCD dataset page. Because a public job-application repository may be interpreted differently from purely non-commercial research redistribution, MIO-derived videos and weights are excluded.
- RDD2022 is published on Figshare under Creative Commons Attribution 4.0. It is the least restrictive of the three datasets, but the public repository still excludes derived RDD videos, snapshots, and trained weights to keep a single conservative publication policy.
- TRANCOS documentation states that the database is publicly available for scientific research purposes and that users must respect the Spanish DGT terms. Therefore TRANCOS-derived media and trained weights are excluded.

## Source Links

- MIO-TCD dataset page: https://tcd.miovision.com/challenge/dataset.html
- RDD2022 Figshare page: https://figshare.com/articles/dataset/RDD2022_-_The_multi-national_Road_Damage_Dataset_released_through_CRDDC_2022/21431547
- TRANCOS dataset page: https://gram.web.uah.es/data/datasets/trancos/index.html
- Creative Commons BY-NC-SA 4.0: https://creativecommons.org/licenses/by-nc-sa/4.0/
- Creative Commons BY 4.0: https://creativecommons.org/licenses/by/4.0/

## Included Publicly

- Source code for the API, dashboard, seed script, and YOLO pipeline.
- Dataset download, preparation, training, and inference scripts.
- Training configuration and summary metrics under `model-artifacts/`.
- A demo SQLite database snapshot under `demo-data/`.
- AI conversation logs and project documentation.

## Excluded Publicly

- Raw and prepared training images.
- Short YOLO demo MP4 files generated from dataset images.
- YOLO snapshots generated from dataset images.
- Trained `.pt` weights derived from MIO-TCD, RDD2022, or TRANCOS.
- Intermediate epoch checkpoints and caches.

## How To Reproduce Locally

Use the scripts under `yolo/` to download the official datasets to `<DATA_ROOT>`, prepare YOLO labels, train locally, and run `yolo.infer_video` against local videos. The README and deployment guide keep the commands needed for local reproduction, while this public repository avoids redistributing the underlying data-derived artifacts.

This is a conservative compliance choice, not a technical limitation.
