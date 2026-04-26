# 文檔索引

這份文件是整個 repo 的文檔地圖。

## 先看這裡

- `README.md`: 英文主 README，包含 overview、quick start、API summary、Docker/local run、YOLO-to-API demo、取捨。
- `README.ja.md`: 日文 README。
- `README.zh-Hant.md`: 繁體中文 README。

## 提交 / Review 用文檔

- `docs/deployment.md`: 英文部署 / 執行指南，包含 Docker Compose、本機 Python、DB 持久化、YOLO 寫入 API 驗證。
- `docs/deployment.ja.md`: 日文部署 / 執行指南。
- `docs/deployment.zh-Hant.md`: 繁體中文部署 / 執行指南。
- `docs/implementation-vs-requirements-v2.en.md`: 英文「實作 vs 要件」完成度。
- `docs/implementation-vs-requirements-v2.ja.md`: 日文「實作 vs 要件」完成度。
- `docs/implementation-vs-requirements-v2.md`: 繁體中文「實作 vs 要件」完成度。

## AI 使用紀錄

- `docs/ai-log.md`: 英文 AI workflow summary。
- `docs/ai-log.ja.md`: 日文 AI workflow summary。
- `docs/ai-log.zh-Hant.md`: 繁體中文 AI workflow summary。
- `docs/ai-conversation-source.md`: Claude / Gemini 對話抽出文字。
- `docs/Claude_geminiconversation.md.pdf`: Claude / Gemini 對話原始 PDF。

## YOLO / 資料證據

- `docs/yolo-video-test.md`: 英文 YOLO 影片測試、dry-run 指令、已驗證 API 寫入 demo。
- `docs/yolo-video-test.ja.md`: 日文 YOLO 影片測試說明。
- `docs/yolo-video-test.zh-Hant.md`: 繁體中文 YOLO 影片測試說明。
- `docs/submission-assets.md`: 英文提交資產、排除資產、資料來源、demo DB source。
- `docs/submission-assets.ja.md`: 日文資產 / 來源說明。
- `docs/submission-assets.zh-Hant.md`: 繁體中文資產 / 來源說明。
- `docs/public-release-notes.md`: 英文 public GitHub release 中 dataset 派生 media / weight 的處理方針。
- `docs/public-release-notes.ja.md`: 日文 public release notes。
- `docs/public-release-notes.zh-Hant.md`: 繁體中文 public release notes。

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
