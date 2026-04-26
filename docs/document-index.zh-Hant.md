# 文檔索引

語言: [English](document-index.md) | [日本語](document-index.ja.md) | [繁體中文](document-index.zh-Hant.md)

這份文件是提交文檔的導航頁。README 是入口，這裡是整個 repository 的路標。

> [!TIP]
> 快速 review 建議順序：README、Docker Compose、`/docs`、`/ui/`、完成度清單、公開發布說明。

## Fast Review Route

| Step | Read / Open | 用途 |
| --- | --- | --- |
| 1 | [README.zh-Hant.md](../README.zh-Hant.md) | 專案概要與 quick start |
| 2 | [Deployment guide](deployment.zh-Hant.md) | 可重現部署步驟 |
| 3 | [Implementation status](implementation-vs-requirements-v2.md) | 逐項要件完成度 |
| 4 | [Public release notes](public-release-notes.zh-Hant.md) | dataset / weight 公開策略 |
| 5 | [AI workflow log](ai-log.zh-Hant.md) | AI 使用紀錄 |

## 先看這裡

- `README.md`: 英文主 README，包含 overview、quick start、API summary、Docker/local run、YOLO-to-API demo、取捨。
- `README.ja.md`: 日文 README。
- `README.zh-Hant.md`: 繁體中文 README。

## 提交 / Review 用文檔

| Document | 用途 |
| --- | --- |
| [deployment.md](deployment.md) | 英文部署 / 執行指南 |
| [deployment.ja.md](deployment.ja.md) | 日文部署 / 執行指南 |
| [deployment.zh-Hant.md](deployment.zh-Hant.md) | 繁體中文部署 / 執行指南 |
| [requirements-spec.en.md](requirements-spec.en.md) | 英文要件定義書 |
| [requirements-spec.ja.md](requirements-spec.ja.md) | 日文要件定義書 |
| [requirements-spec.zh-Hant.md](requirements-spec.zh-Hant.md) | 繁體中文要件定義書 |
| [requirements_spec.md.pdf](requirements_spec.md.pdf) | 要件定義書原始 PDF |
| [implementation-vs-requirements-v2.en.md](implementation-vs-requirements-v2.en.md) | 英文完成度 checklist |
| [implementation-vs-requirements-v2.ja.md](implementation-vs-requirements-v2.ja.md) | 日文完成度 checklist |
| [implementation-vs-requirements-v2.md](implementation-vs-requirements-v2.md) | 繁體中文完成度 checklist |

## AI 使用紀錄

| Document | 用途 |
| --- | --- |
| [ai-log.md](ai-log.md) | 英文 AI workflow summary |
| [ai-log.ja.md](ai-log.ja.md) | 日文 AI workflow summary |
| [ai-log.zh-Hant.md](ai-log.zh-Hant.md) | 繁體中文 AI workflow summary |
| [ai-conversation-source.en.md](ai-conversation-source.en.md) | Claude / Gemini 對話來源英文翻譯 |
| [ai-conversation-source.ja.md](ai-conversation-source.ja.md) | Claude / Gemini 對話來源日文翻譯 |
| [ai-conversation-source.zh-Hant.md](ai-conversation-source.zh-Hant.md) | Claude / Gemini 對話來源繁體中文翻譯 |
| [ai-conversation-source.md](ai-conversation-source.md) | Claude / Gemini 對話 raw 抽出文字 |
| [Claude_geminiconversation.md.pdf](Claude_geminiconversation.md.pdf) | Claude / Gemini 對話原始 PDF |

## YOLO / 資料證據

| Document | 用途 |
| --- | --- |
| [yolo-video-test.md](yolo-video-test.md) | YOLO 影片測試、dry-run 指令、API 寫入 demo |
| [yolo-video-test.ja.md](yolo-video-test.ja.md) | 日文 YOLO 影片測試說明 |
| [yolo-video-test.zh-Hant.md](yolo-video-test.zh-Hant.md) | 繁體中文 YOLO 影片測試說明 |
| [submission-assets.md](submission-assets.md) | 提交資產、排除資產、資料來源、demo DB source |
| [submission-assets.ja.md](submission-assets.ja.md) | 日文資產 / 來源說明 |
| [submission-assets.zh-Hant.md](submission-assets.zh-Hant.md) | 繁體中文資產 / 來源說明 |
| [public-release-notes.md](public-release-notes.md) | public GitHub release policy |
| [public-release-notes.ja.md](public-release-notes.ja.md) | 日文 public release notes |
| [public-release-notes.zh-Hant.md](public-release-notes.zh-Hant.md) | 繁體中文 public release notes |

## 畫面證據

- `docs/dashboard-smoke.png`: Dashboard smoke-test 截圖。
- `docs/dashboard-i18n-smoke.png`: Dashboard i18n smoke-test 截圖。

## 非 Markdown 的運行相關文件

- `Dockerfile`: FastAPI API 的 container image 定義。
- `docker-compose.yml`: 啟動 `api` 與 optional `seed` services。
- `.env.example`: 環境變數範例。
- `.gitignore`: 排除 cache、本地 DB、raw dataset、dataset 派生 media、YOLO weight、大型中間檔。
- `.dockerignore`: 縮小 Docker build context。
- `.gitattributes`: 將 MP4、DB、PT、PDF、PNG 等視為 binary。
- `requirements.txt`: API/runtime Python dependencies。
- `requirements-ml.txt`: YOLO/ML dependencies。

## 不是完整 production runbook 的部分

這是 interview/demo submission，不是正式 production service。`docs/deployment.zh-Hant.md` 已列出 production follow-up，但 cloud deployment、authentication rollout、monitoring、backup、incident-response runbook 屬於本次範圍外。
