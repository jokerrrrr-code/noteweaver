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
        project, original_page=2, title="Opportunity cost",
        content="Opportunity cost is the value of the next-best alternative forgone.", language="en",
    )
    note_id = project.notes[-1].note_id
    print("New note:", list_notes(project)[0].status)

    # In a UI, this call follows the student's explicit confirmation.
    project = approve_note(project, note_id)
    print("After student confirmation:", list_notes(project)[0].status)
    project = update_note(project, note_id, content="Opportunity cost includes time, not only money.\nTime matters too.")
    note = list_notes(project, original_page=2)[0]
    assert note.note_id == note_id and note.original_page == 2
    assert note.status == "draft"
    print("After editing, confirmation is required again:", note.status)
    print("Original page:", note.original_page)
    print("Note content:", note.sections[0].content)
    print("Notes eligible for export:", len(list_notes(project, status="approved")))

    project = approve_note(project, note_id)
    print("Notes eligible after reconfirmation:", len(list_notes(project, status="approved")))
    project = delete_note(project, note_id)
    assert list_notes(project) == ()
    print("Notes remaining after deletion:", len(list_notes(project)))
    print("This demo manages notes in memory only; no AI calls, PDF operations, or file saving.")


if __name__ == "__main__":
    main()
