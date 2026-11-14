# 組員 4：手寫筆記管理（第 2 步）

這一版提供記憶體中的專案及筆記操作，不需要網路、AI 金鑰或其他組員的模組。這裏的「手寫」指使用者輸入文字，不是手寫圖片辨識。PDF 讀取、生成、匯出以及檔案 save/load 尚未接入。

## 快速執行

先依 [README](../README.md) 安裝本機開發版，再於 repo 根目錄執行：

```bash
python examples/manual_notes_demo.py
python -m unittest discover -s tests -v
```

範例展示新增、確認、修改、再次確認和刪除。修改後可匯出的筆記數變成 0，再次確認後變成 1。它使用自製文字與模擬文件資料，不開啟真正的 PDF，也不會保存檔案。

## 可以直接使用的 API

以下函式都可以從 `noteweaver` 匯入：

| 函式 | 參數 | 回傳／行為 |
| --- | --- | --- |
| `create_project` | `document: DocumentInfo, source_path: str 或 Path` | 空的 `ProjectState`；不開啟或驗證來源檔案 |
| `add_manual_note` | `project`；具名參數 `original_page, title, content, language='zh-Hant'` | 新專案，末尾加入一則 `draft` 筆記 |
| `update_note` | `project, note_id`；具名參數 `title=None, content=None` | 新專案，修改指定筆記並回到 `draft` |
| `approve_note` | `project, note_id` | 新專案，指定筆記變成 `approved` |
| `delete_note` | `project, note_id` | 新專案，移除指定筆記，保留其他筆記和請求紀錄 |
| `list_notes` | `project`；具名參數 `original_page=None, status=None` | 符合條件的 `tuple[GeneratedNote, ...]`，保持原順序 |

**所有修改函式都回傳新的 ProjectState；請寫成 `project = 操作(project, ...)`。** 不接收回傳值，原本的 project 不會改變。舊專案可保留供比較；無效操作不會破壞舊資料。

## 從新增到修改的例子

```python
from noteweaver import (
    DocumentInfo, create_project, add_manual_note,
    approve_note, update_note, list_notes,
)

# 只供演示的 metadata；正式使用時由組員 1 的 reader.inspect() 提供。
document = DocumentInfo("sha256:" + "0" * 64, "demo.pdf", 3)
project = create_project(document, "local_data/demo.pdf")
project = add_manual_note(
    project, original_page=2, title="機會成本 Opportunity cost",
    content="放棄的最佳選擇之價值。", language="zh-Hant",
)
note_id = project.notes[-1].note_id

# 真正的介面必須等使用者確認後，才呼叫 approve_note。
project = approve_note(project, note_id)
project = update_note(project, note_id, content="機會成本也包括時間。")

print(project.notes[0].status)                   # draft
print(project.notes[0].original_page)            # 2
print(project.notes[0].note_id == note_id)        # True
print(len(list_notes(project, status="approved")))  # 0
```

## 編輯及確認規則

- 新筆記使用 UUID，段落為 `kind='personal'`、`origin='user'`，沒有生成請求或來源聲明。
- 原始頁碼由 1 開始，必須在文件頁數內；標題、內容和語言不能空白。
- 編輯保留筆記 ID、文件身分、原始頁碼、語言及所在順序。
- `update_note` 的 `None` 表示不修改該欄；至少提供 title 或 content。每次有效編輯都回到 draft，即使提交文字與舊值相同也需重新確認。
- **content 是替換整份筆記正文，不是修改其中一段。** 它會把正文換成一段使用者文字，清除原先 source_pages 的來源聲明；保留 request_id 作為原始生成關聯。此版本尚未提供逐段編輯。
- 只改 title 時，原有分段及 source_pages 保持不變。
- approve_note 可重複呼叫。它記錄使用者確認，不代表筆記事實已驗證；不得在生成或編輯後自動確認。
- list_notes 的頁碼及狀態條件同時提供時，必須兩者都符合；沒有結果會回傳空 tuple。
- 不會讀寫來源 PDF，create_project 也不會驗證路徑是否存在。相對來源路徑仍遵守共用格式：以未來專案 JSON 所在目錄為基準。

## 錯誤與測試

- `ContractError`：內容／型別不符、頁碼越界、無效查詢條件、空白 ID，或編輯沒有指定任何欄位。
- `KeyError`：指定的有效字串 ID 不存在於專案中。

本次新增測試覆蓋中英文字、唯一 ID、多筆記順序、確認後編輯回草稿、無效操作保留舊資料、正文替換的來源標記，以及查詢和刪除。既有共用格式測試繼續使用，沒有修改模型或 JSON schema。

## 下一步交接

組員 4 第 3 步再加入實際檔案保存、載入、路徑解析及來源驗證。這次的更新結果仍是共用 ProjectState，可以使用既有 `to_json()` 做純序列化，但這不是已完成 save/load 功能。

組員 1 後續提供真實 DocumentInfo；組員 2 回傳的 GeneratedNote 使用相同資料結構；組員 3 接收同一個 ProjectState，依共用約定只匯出 approved 筆記。這次不代寫其他人的模組。
