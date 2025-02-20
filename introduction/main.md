# 記帳機器

|[活動圖](https://www.mermaidchart.com/raw/2d38eeed-abd7-42c2-98be-ba711edd8d52?theme=light&version=v0.1&format=svg)|[架構流程](https://www.mermaidchart.com/raw/b2bef3b1-4680-42c5-8fbd-3f26e0c79dda?theme=light&version=v0.1&format=svg)|[循序圖](https://www.mermaidchart.com/raw/f1f72e8a-6f98-4c33-8099-6f32137a34b7?theme=light&version=v0.1&format=svg)|
|---|---|---|

---

專案使用 Streamlit、LangChain 框架開發應用程式，用來作為記帳助理，透過 LLM 來解析並處理用戶的記帳需求。它的主要功能包括：

1. 與用戶對話：\
   使用 Streamlit 建立聊天介面，記錄對話歷史並顯示 AI 回應。\
   使用 `st.chat_input()` 來接收用戶輸入，並調用 `run_llm()` 來獲取 AI 回應。

2. 記帳資料處理：\
   使用 LangChain 建立 LLM 處理鏈，根據用戶輸入決定適當的記帳任務：\
   解析記帳資料 (`parse_record.py`)\
   插入記帳資料 (`insert_record.py`)\
   透過 路由機制 (`router.py`) 自動選擇適當的處理方式。

3. 核心模組 (LLM 運行機制)：\
   `core.py` 負責管理 LLM 運行，並設置不同的處理邏輯。\
   透過 `create_task_router_chain()` 選擇合適的記帳處理鏈。

---

### 程式架構解析
|檔案|主要功能|
|---|---|
|`app.py`			|Streamlit 主程式，處理 UI 及用戶輸入|
|`core.py`			|負責 LLM 運行，選擇適當的記帳處理邏輯|
|`router.py`		|負責路由選擇，確保不同輸入能進入正確的 LLM 處理鏈|
|`parse_record.py`	|負責解析記帳輸入，將資料整理成表格|
|`insert_record.py`	|負責將整理好的記帳資料轉換為 JSON 並送入資料庫|

### 專案運作流程
1. 用戶輸入 記帳資訊（如「午餐 150 元」）。
2. LLM 路由機制 透過 router.py 決定執行 解析 或 新增 記帳資料：
   - 若是 新的記帳資訊，則進入 parse_record.py，將輸入整理為表格格式。
   - 若用戶 確認無誤，則進入 insert_record.py，轉換為 JSON 並插入資料庫。
3. 回應用戶 整理後的記帳資訊，請求確認或提供建議。

### 優點與可改進之處

**✅ 優點**

1. 模組化設計：
   - 透過 LangChain 的 RunnableLambda、RouterRunnable 設計不同的 LLM 運行邏輯，維護性高。

2. 動態記帳分類：
   - parse_record.py 能自動將用戶輸入對應至適當的 記帳類別（如「晚餐」→「飲食」）。

3. 流式回應 (st.write_stream())：
   - 透過 流式輸出 提高用戶體驗，使回應更加即時。

**🔧 可改進點**

1. 資料庫整合：
   - 目前 insert_record.py 只是將記帳資訊轉換為 JSON，缺少實際的 資料庫存取邏輯（如 SQL 或 NoSQL）。
2. 錯誤處理：
   - run_llm() 內部缺少 錯誤處理機制，如果 API 錯誤可能導致應用崩潰。
   - 可考慮 加入 logging，以便追蹤用戶的輸入與 LLM 回應。
3. 時間處理：
   - 目前 parse_record.py 預設時間為 datetime.now()，但並未根據 用戶輸入的時間資訊進行調整（如「昨天晚餐」應該對應到前一天的時間）。
