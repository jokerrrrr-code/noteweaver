"""Member 4 step 2: in-memory editing, using synthetic document metadata."""

from noteweaver import (
    DocumentInfo, add_manual_note, approve_note, create_project,
    delete_note, list_notes, update_note,
)


def main() -> None:
    # Placeholder only: no PDF exists or is opened by this demonstration.
    document = DocumentInfo("sha256:" + "0" * 64, "demo.pdf", 3)
    project = create_project(document, "local_data/demo.pdf")
    project = add_manual_note(
        project, original_page=2, title="機會成本 Opportunity cost",
        content="機會成本是放棄的最佳選擇之價值。", language="zh-Hant",
    )
    note_id = project.notes[-1].note_id
    print("新增筆記：", list_notes(project)[0].status)

    # In a UI, this call follows the student's explicit confirmation.
    project = approve_note(project, note_id)
    print("學生確認後：", list_notes(project)[0].status)
    project = update_note(project, note_id, content="機會成本也包括時間，不只是金錢。\nTime matters too.")
    note = list_notes(project, original_page=2)[0]
    assert note.note_id == note_id and note.original_page == 2
    assert note.status == "draft"
    print("修改後需要再次確認：", note.status)
    print("原始頁碼：", note.original_page)
    print("筆記內容：", note.sections[0].content)
    print("可匯出筆記數：", len(list_notes(project, status="approved")))

    project = approve_note(project, note_id)
    print("再次確認後可匯出筆記數：", len(list_notes(project, status="approved")))
    project = delete_note(project, note_id)
    assert list_notes(project) == ()
    print("刪除後筆記數：", len(list_notes(project)))
    print("此範例只管理記憶體中的筆記；沒有呼叫 AI、讀寫 PDF 或存檔。")


if __name__ == "__main__":
    main()
