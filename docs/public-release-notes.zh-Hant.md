# 公開發布說明

語言: [English](public-release-notes.md) | [日本語](public-release-notes.ja.md) | [繁體中文](public-release-notes.zh-Hant.md)

回到 [Document Index](document-index.zh-Hant.md)

這個 repo 會公開在 GitHub，因此不包含資料集派生的媒體檔或訓練權重。

> [!CAUTION]
> 這是面試提交用的保守 compliance note，不是法律意見；它用來說明為何不再散布 dataset 派生 artifact。

## 授權確認摘要

- MIO-TCD 官方 dataset page 標示採 Creative Commons Attribution-NonCommercial-ShareAlike 4.0。公開求職 repo 是否能完全視為純非商業研究再散布存在灰色地帶，因此排除 MIO 派生影片與權重。
- RDD2022 在 Figshare 上標示為 Creative Commons Attribution 4.0，是三者中最寬鬆的。但為了讓 public repo 採一致且保守的發布策略，也排除 RDD 派生影片、snapshot 與訓練權重。
- TRANCOS 文件寫明 database 是為 scientific research purposes 公開，且使用者需遵守 Spanish DGT 條款。因此排除 TRANCOS 派生媒體與訓練權重。

## 來源連結

- MIO-TCD dataset page: https://tcd.miovision.com/challenge/dataset.html
- RDD2022 Figshare page: https://figshare.com/articles/dataset/RDD2022_-_The_multi-national_Road_Damage_Dataset_released_through_CRDDC_2022/21431547
- TRANCOS dataset page: https://gram.web.uah.es/data/datasets/trancos/index.html
- Creative Commons BY-NC-SA 4.0: https://creativecommons.org/licenses/by-nc-sa/4.0/
- Creative Commons BY 4.0: https://creativecommons.org/licenses/by/4.0/

## Public Repo 會包含

- API、Dashboard、seed script、YOLO pipeline 原始碼。
- dataset download、prepare、training、inference scripts。
- `model-artifacts/` 內的 training configuration 與 summary metrics。
- `demo-data/` 內的 demo SQLite database snapshot。
- AI conversation logs 與 project documentation。

## Public Repo 不會包含

- raw / prepared training images。
- 由 dataset image 生成的 YOLO demo MP4。
- 由 dataset image 生成的 YOLO snapshot。
- 由 MIO-TCD、RDD2022、TRANCOS 訓練出的 `.pt` weight。
- intermediate epoch checkpoint 與 cache。

## 如何在本機再現

使用 `yolo/` 底下的 script，把官方資料集下載到 `<DATA_ROOT>`，轉換 YOLO labels，本機訓練，再用 `yolo.infer_video` 對本機影片執行推理。README 和 deployment guide 保留了本機再現所需指令，但 public repository 不再散布 data-derived artifacts。

這是公開發布時的保守合規選擇，不是技術限制。
