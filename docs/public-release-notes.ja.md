# Public release notes

この repository は GitHub で public にする前提です。そのため、dataset 由来の media file や trained model weight は含めていません。

## license review summary

- MIO-TCD は公式 dataset page 上で Creative Commons Attribution-NonCommercial-ShareAlike 4.0 とされています。job-application 用の public repository が純粋な non-commercial research redistribution と見なされるかは曖昧なため、MIO 由来の動画と weight は除外しました。
- RDD2022 は Figshare 上で Creative Commons Attribution 4.0 とされています。3 つの中では最も制限が少ないですが、public repository では一貫して保守的な方針を取るため、RDD 由来の動画、snapshot、trained weight も除外しました。
- TRANCOS の documentation には、database は scientific research purposes 向けに公開され、Spanish DGT の terms を尊重する必要があると書かれています。そのため TRANCOS 由来の media と trained weight は除外しました。

## source links

- MIO-TCD dataset page: https://tcd.miovision.com/challenge/dataset.html
- RDD2022 Figshare page: https://figshare.com/articles/dataset/RDD2022_-_The_multi-national_Road_Damage_Dataset_released_through_CRDDC_2022/21431547
- TRANCOS dataset page: https://gram.web.uah.es/data/datasets/trancos/index.html
- Creative Commons BY-NC-SA 4.0: https://creativecommons.org/licenses/by-nc-sa/4.0/
- Creative Commons BY 4.0: https://creativecommons.org/licenses/by/4.0/

## public に含めるもの

- API、dashboard、seed script、YOLO pipeline の source code。
- dataset download、prepare、training、inference scripts。
- `model-artifacts/` 配下の training configuration と summary metrics。
- `demo-data/` 配下の demo SQLite database snapshot。
- AI conversation logs と project documentation。

## public から除外するもの

- raw / prepared training images。
- dataset image から生成した短い YOLO demo MP4。
- dataset image から生成した YOLO snapshot。
- MIO-TCD、RDD2022、TRANCOS から学習した `.pt` weight。
- intermediate epoch checkpoint と cache。

## local で再現する方法

`yolo/` 配下の script を使い、official dataset を `<DATA_ROOT>` に download し、YOLO label を prepare し、local training を行い、`yolo.infer_video` を local video に対して実行します。README と deployment guide には local reproduction 用の command を残していますが、この public repository では data-derived artifact を再配布しません。

これは技術的制限ではなく、public release 向けの保守的な compliance 判断です。
