# NoteWeaver 共用資料格式 v1

本文件、`src/noteweaver/models.py`、`interfaces.py` 及 `examples/data/` 是四個模組的共同約定。模型、驗證器、JSON 轉換已實作；PDF 讀取、AI 呼叫、PDF 排版和專案操作介面尚待各組員實作。

## 1. 資料如何流動

```text
組員 1：PDF → DocumentInfo + PageContent
組員 4：學生問題 → NoteRequest
組員 2：DocumentInfo + NoteRequest + tuple[PageContent, ...] → GeneratedNote（draft）
組員 4：預覽／編輯／確認 → ProjectState（notes 中的 approved 筆記可匯出）
組員 3：來源 PDF + ProjectState → 新 PDF + ExportResult
```

手動輸入筆記直接建立 `GeneratedNote(request_id=None, sections=使用者內容)`，不經過組員 2，也不需要 AI 金鑰。保留 `GeneratedNote` 名稱是為了沿用既有分工，但它同時支援手動筆記。

## 2. 統一規則

- 所有公開頁碼由 **1** 開始。`original_page` 永遠是原始講義頁碼，不能換成插頁後頁碼。
- `document_id` 是 `sha256:` 加原始 PDF 全部 bytes 的 SHA-256 小寫十六進位摘要。重新命名不改變 ID，檔案內容改變則 ID 改變。用 `document_id_for_file()` 計算；它不會確認檔案真的是 PDF。
- 所有 ID 是非空字串，正式資料建議使用 `str(uuid.uuid4())`。範例使用 `request-001` 等易讀 ID。ID 不隨標題或內容編輯而改變。
- Python 使用 frozen dataclass 和 **tuple**；JSON 使用 object 和 **array**。使用 `from_dict()`／`from_json()` 轉入，不做 `GeneratedNote(**json_dict)` 這種略過巢狀轉換的操作。
- 模型不自動把 `"2"`、`2.0` 或 `true` 轉成頁碼 2／1。未知欄位、未知列舉值、空白必要文字會報 `ContractError`。
- 文字使用 Unicode；JSON 以 UTF-8 儲存。v1 的 `content` 是純文字，可包含換行和公式原文。不是任意 HTML，也沒有保證完整 Markdown／LaTeX 渲染；組員 3 不可靜默刪除不支援內容。
- 頁碼清單不得有重複值。`notes` 的陣列順序就是同一原頁後的筆記順序，不以 UUID 或標題重新排序。
- 所有模型都是資料，不能執行其中的程式碼、指令或 HTML。

## 3. DocumentInfo：原始文件（組員 1）

| 欄位 | Python 型別 | 規則 |
| --- | --- | --- |
| `document_id` | `str` | 必須符合上述 SHA-256 格式 |
| `filename` | `str` | 顯示用名稱，例如 `lecture.pdf`，不是文件身分 |
| `page_count` | `int` | 大於 0，由真正的 PDF reader 讀取 |

來源路徑另存於 `ProjectState.source_path`。不要把檔案路徑當成穩定 ID。

## 4. PageContent：頁面內容（組員 1 → 2、4）

| 欄位 | Python 型別 | 必填／預設 |
| --- | --- | --- |
| `document_id` | `str` | 必填 |
| `original_page` | `int` | 必填，正整數 |
| `text` | `str` | 必填 |
| `extraction_status` | `Literal['ok', 'empty', 'error']` | 必填 |
| `preview_path` | `str \| None` | 預設 `None`，可選的本機預覽圖片路徑 |
| `error_message` | `str \| None` | 預設 `None` |

- `ok`：text 不可空白；error_message 必須為 None。
- `empty`：沒有可擷取文字，例如空頁或可能的掃描頁；text 必須為空字串。這個狀態不聲稱已辨識出頁面種類。
- `error`：擷取失敗；text 必須為空字串，error_message 必須有可顯示的原因，不能包含金鑰。
- `validate_page(document, page)` 會再檢查文件 ID 和頁碼上限。
- 預覽是可重新產生的暫存，不寫進專案格式。讀取原頁文字不代表已理解圖片或公式。

範例：[page.json](../examples/data/page.json)。

## 5. NoteRequest：學生的問題（組員 4 → 2）

| 欄位 | Python 型別 | 必填／預設 |
| --- | --- | --- |
| `request_id` | `str` | 必填；每次生成嘗試使用新 ID |
| `document_id` | `str` | 必填 |
| `original_page` | `int` | 必填；筆記最後綁定的原頁 |
| `question` | `str` | 必填，不可空白 |
| `context_pages` | `tuple[int, ...]` | 必填，包含目標原頁，記錄本次實際提供的上下文 |
| `selected_text` | `str \| None` | 預設 None；學生選取的原文，可由介面另外核對 |
| `language` | `str` | 預設 `zh-Hant`，其他例子為 `en`；v1 僅驗證非空字串 |
| `level` | `str` | 預設 `first-year`；非空的程度描述 |
| `style` | `ExplanationStyle` | 預設 `simple` |

`style` 只接受 `simple`、`step_by_step`、`comparison`、`example`。

組員 2 可先挑上下文，但送出生成前必須將最後確定的頁碼記入 request；實際 context 頁面集合必須完全一致，每頁狀態都是 ok。v1 對沒有文字的目標頁走手動筆記或明確提示，不假裝已有 OCR。

## 6. NoteSection 與 GeneratedNote：分段筆記（組員 2／4 → 3）

### NoteSection

| 欄位 | 型別／允許值 | 意義 |
| --- | --- | --- |
| `kind` | `explanation`, `steps`, `comparison`, `example`, `quiz`, `answer`, `personal` | 讓 renderer 選擇段落標題和樣式 |
| `content` | 非空 `str` | 純文字內容，保留原文換行 |
| `origin` | `lecture`, `ai`, `user` | 分別為基於講義的內容、模型補充／推論、使用者輸入／改寫 |

`lecture` 是來源聲明，**不是**經過事實核實的標記。AI 根據講義重述也可能出錯；renderer 必須保留這個限制。使用者改寫的段落可改為 `user`。

### GeneratedNote

| 欄位 | Python 型別 | 必填／預設 |
| --- | --- | --- |
| `note_id` | `str` | 必填，編輯時保持不變 |
| `document_id` | `str` | 必填 |
| `original_page` | `int` | 必填 |
| `title` | `str` | 必填，非空 |
| `sections` | `tuple[NoteSection, ...]` | 必填，至少一段；輸出按此順序 |
| `source_pages` | `tuple[int, ...]` | 預設空 tuple；這則筆記整體參考的原頁碼 |
| `request_id` | `str \| None` | 預設 None；AI 生成時連到本次 NoteRequest |
| `language` | `str` | 預設 `zh-Hant` |
| `status` | `Literal['draft', 'approved']` | 預設 `draft` |

- 有 `lecture` 段落就必須有 source_pages；有 `ai` 段落就必須有 request_id。
- 生成筆記的來源頁碼只能是 context_pages 的子集，不能引用模型未收到的頁面。
- `validate_generation(document, request, context, note)` 檢查實際上下文、請求 ID、文件、原頁、語言、來源範圍和 draft 狀態。它不是 AI 解說正確性的判定器。
- 手動筆記使用 user 段落，可沒有 request、沒有來源頁；若引用講義，可使用 lecture 段落和來源頁。
- 新生成筆記一律 draft。組員 4 在學生明確確認後才改 approved；編輯／重新生成後必須回到 draft。資料模型驗證狀態值，但操作層負責確認狀態轉移。
- 重新生成使用新 request_id；若替換同一則筆記，可保留 note_id。必須先生成成功再替換，失敗保留舊稿。

編輯 frozen 模型的方式：

```python
from dataclasses import replace
edited = replace(note, title="我改過的標題", status="draft")
```

## 7. ProjectState：專案存檔（組員 4）

| 欄位 | Python 型別 | 必填／預設 |
| --- | --- | --- |
| `schema_version` | `int` | Python 預設 1；讀取 JSON 必須明確存在且為 1 |
| `document` | `DocumentInfo` | 必填 |
| `source_path` | `str` | 必填；相對路徑以專案 JSON 所在目錄為基準 |
| `requests` | `tuple[NoteRequest, ...]` | 預設空 tuple |
| `notes` | `tuple[GeneratedNote, ...]` | 預設空 tuple，保留編輯和同頁插入順序 |

每份 project v1 只對應一份原始 PDF。request_id／note_id 在專案內各自唯一；有 request_id 的筆記必須連到保存的 request 並符合其原頁、語言和來源範圍。note 原頁及來源頁不能超出文件頁數。

純序列化已可用：

```python
from pathlib import Path
from noteweaver import ProjectState

project = ProjectState.from_json(Path("examples/data/project.json").read_text(encoding="utf-8"))
json_text = project.to_json()
restored = ProjectState.from_json(json_text)
assert restored == project
```

組員 4 仍需實作真正的 save/load 操作、路徑解析和介面；組員 3 在匯出前也應檢查來源。兩者都可呼叫 `verify_source(project, resolved_path)`，確定原始 bytes 沒變。若檔案移動可重新選取相同 hash 的檔案；hash 不同則停止自動沿用頁碼。

存檔不內嵌 PDF、預覽圖片或 API key。講義與筆記可能是私人資料，使用 ignored 目錄保存。禁止未知 key 能抓到誤放的頂層設定，但不會辨識任意文字內容中的秘密。

## 8. ExportResult：輸出頁碼對照（組員 3 → 4）

| 欄位 | Python 型別 | 意義 |
| --- | --- | --- |
| `document_id` | `str` | 原始文件 ID |
| `output_path` | `str` | 新 PDF 的路徑，由 exporter 回傳；不代表模型已建立該檔案 |
| `output_page_count` | `int` | 匯出後實際頁數 |
| `original_to_output_pages` | `tuple[OriginalPageLocation, ...]` | 每個項目為 original_page + output_page，兩者從 1 起 |
| `note_to_output_pages` | `tuple[NotePageLocation, ...]` | 每個項目為 note_id + output_pages；長筆記可以佔多頁 |

使用「物件陣列」而不是整數 key 字典，避免 JSON 將整數 key 轉成字串後接錯。

```json
{
  "original_to_output_pages": [
    {"original_page": 1, "output_page": 1},
    {"original_page": 2, "output_page": 2},
    {"original_page": 3, "output_page": 4}
  ],
  "note_to_output_pages": [
    {"note_id": "note-001", "output_pages": [3]}
  ]
}
```

上面只展示對照欄位；完整資料見 [export.json](../examples/data/export.json)。

- **v1 僅匯出 approved 筆記**；draft 留在專案裏，介面可另外預覽。
- 先按原頁順序輸出；每一原頁後，依 project.notes 中的順序插入該頁的 approved 筆記。
- 一則筆記的所有輸出頁必須連續。每個輸出頁恰好屬於原頁或一則筆記，不能重複或遺漏。
- `validate_export(project, result)` 驗證上述對照、完整性和排序，但不會打開 PDF 檢查實際內容或版面。真正的 PDF 測試由組員 3 負責。
- exporter 預設輸出新檔案，須拒絕輸出路徑等於來源檔（包含解析後指向同檔的別名）。

## 9. 各組員要接的函式介面

`src/noteweaver/interfaces.py` 定義 Protocol，只有方法簽名和約定，沒有執行 PDF 或 AI 工作。實作物件只要提供相同方法，不必繼承 Protocol。

```python
# 組員 1：實作 reader
inspect(source: Path) -> DocumentInfo
read_page(source: Path, original_page: int) -> PageContent

# 組員 2：實作 generator
generate(document: DocumentInfo, request: NoteRequest,
         context: tuple[PageContent, ...]) -> GeneratedNote

# 組員 3：實作 exporter
export(source: Path, project: ProjectState, output: Path) -> ExportResult

# 組員 4：編輯、保存和協調上述方法；公開專案 API 尚待實作
```

Python 型別／欄位不符、版本不符或資料關聯錯誤使用 `ContractError`。讀取不存在檔案等 I/O 問題保留 `OSError` 子類；provider 的連線／認證錯誤由組員 2 的 provider 層定義，不能用空白「成功」筆記代替失敗。各模組完成後再整合錯誤展示方式。

## 10. 共用範例及快速開始

- [project.json](../examples/data/project.json)：三頁文件、一次問題、一則已確認補充筆記、一則手動草稿。
- [page.json](../examples/data/page.json)：第 2 頁的文字上下文。
- [export.json](../examples/data/export.json)：四頁輸出對照；手動草稿沒有匯出。
- [contract_demo.py](../examples/contract_demo.py)：驗證資料流和 JSON round trip。

這些內容由專案自製，**沒有真的呼叫模型或建立 PDF**。全零 SHA-256 是明確的範例佔位值；`demo.pdf`、預覽和輸出路徑並不存在。正式檔案必須由 reader 重新計算 hash，不能照抄範例 ID。

從 repo 根目錄、Python 3.10+ 環境執行（本次實測為 Python 3.14）：

```bash
python -m pip install -e .
python examples/contract_demo.py
python -m unittest discover -s tests -v
```

建議先建立自己的虛擬環境。以上是安裝本機 checkout，不是從 PyPI 安裝。本模組沒有執行時第三方依賴；建置需要 setuptools。`pyproject.toml` 目前標記不可上傳，正式發布前另確認套件名稱、授權及功能狀態。

## 11. 修改格式的規則

四位組員直接 `from noteweaver.models import ...`，不要在自己模組重寫相同模型。修改欄位時同時更新本文件、共用 JSON 範例及合約測試，並說明受影響的模組。沒有遷移程式時不得靜默接受未知 schema version；v1 loader 對未知欄位採拒絕策略。格式有破壞性變更時提升版本並提供遷移方案。

實作參考：[Python dataclasses](https://docs.python.org/3/library/dataclasses.html)、[typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)、[Python packaging guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)。
