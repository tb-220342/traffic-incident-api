# AI 使用紀錄

語言: [English](ai-log.md) | [日本語](ai-log.ja.md) | [繁體中文](ai-log.zh-Hant.md)

這份文件整理本課題開發過程中如何使用 AI 輔助。
Claude / Gemini 對話原文已抽出到 `docs/ai-conversation-source.md`，原始 PDF 保存在 `docs/Claude_geminiconversation.md.pdf`。

## 參考輸入

- `C:\Users\85260\Downloads\Back-End_Candidate_Evaluation.pdf`
- `C:\Users\85260\Downloads\requirements_spec.md.pdf`
- `C:\Users\85260\Downloads\Claude_geminiconversation.md.pdf`

## 工作流程

1. 讀取並整理面試題目的必要範圍。
   - 接收偵測系統送出的事件。
   - 提供給操作人員查詢的 API。
   - 根據「Speed matters」的描述，重視事件即時性。
2. 讀取自訂要件定義書。
   - 確認 FastAPI + SQLite + SQLAlchemy + SSE 的技術方向。
   - Dashboard、seed script、Docker、測試屬於加分項。
   - YOLO 整合是選作，但一旦做就要接近完整端到端流程。
3. 制定實作順序。
   - 先完成核心 API 與 SSE。
   - 再做輕量 Dashboard 展示即時更新。
   - 接著補測試、README、Docker 與 seed script。
4. 在 `D:\Projects\traffic-incident-api` 建立專案。
5. 進行本地驗證，並修正測試中發現的問題。
6. 擴充成支援 YOLO 訓練的版本。
   - 加入 MIO-TCD、RDD2022、TRANCOS downloader。
   - 加入 MIO-TCD 與 RDD2022 資料轉換 script。
   - 加入 YOLO 訓練指令與影片推理回寫 API 工具。
   - 大型資料集、cache、run、snapshot 都放到 `D:\Datasets\traffic-incident`。
   - 使用 RDD2022 影片推理執行非 `--dry-run` 測試，確認可透過 API 寫入 2 筆 `DEBRIS` event。
7. 提交前補齊 Dashboard 與 Markdown 文件的 English / 日本語 / 繁體中文 支援。

## 主要設計決策

- 因為需求是後端到 Dashboard 的單向即時推播，所以選擇 SSE 而不是 WebSocket。
- 為了讓面試官能快速在本機啟動，使用 SQLite。
- 保留明確的狀態流轉規則，但依照 UI 確認結果追加可退回操作，避免誤點後無法復原。
- API 成功回應統一成 `{ success, data, meta }`，錯誤回應統一成 `{ success, error }`。
- 使用 `source_event_id` 作為偵測系統與 API 之間的冪等 key。
- MIO-TCD 用於車輛偵測；RDD2022 作為路面異常資料，映射成 `DEBRIS` 類事件。
- 為避免 C 槽空間不足，ML 相關大型檔案都放在 `D:`。

## 本次未包含

- 認證與授權
- rate limiting、正式 observability 等生產環境功能
- 針對實際道路影片的正式 detector 精度評估
