"""Member 4 step 3: save/load real JSON files using synthetic source bytes."""

from pathlib import Path
import tempfile

from noteweaver import (
    ContractError, DocumentInfo, add_manual_note, approve_note, create_project,
    document_id_for_file, load_project, save_project, update_note,
)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="noteweaver-demo-") as directory:
        root = Path(directory).resolve()
        source = root / "synthetic-lecture.bin"
        source.write_bytes(b"Original lecture fixture: opportunity cost")
        # This is an identity fixture, not a parsed PDF. Real metadata will come
        # from member 1's reader. The page count is synthetic for this demo.
        document = DocumentInfo(document_id_for_file(source), source.name, 3)
        project = create_project(document, source)
        project = add_manual_note(
            project, original_page=2, title="Opportunity cost",
            content="The value of the next-best alternative forgone.", language="en",
        )
        project = add_manual_note(
            project, original_page=2, title="Question for revision",
            content="How does time affect this example?", language="en",
        )
        project = approve_note(project, project.notes[0].note_id)
        path = save_project(project, root / "study.json")
        reopened = load_project(path)
        assert reopened == project
        print("Saved and reopened two notes attached to original page 2.")
        print("States preserved:", [note.status for note in reopened.notes])
        print("Content, IDs, original pages, and note order are unchanged.")

        edited = update_note(reopened, reopened.notes[0].note_id, content="Time is also a cost.")
        save_project(edited, path, overwrite=True)
        assert load_project(path) == edited
        print("After editing and saving, the first note is a draft again.")

        relocated = root / "renamed-lecture.bin"
        source.rename(relocated)
        relinked = load_project(path, source_path=relocated)
        assert relinked.notes == edited.notes
        print("Relinked a renamed source with the same fingerprint.")

        relocated.write_bytes(b"Different lecture content")
        try:
            load_project(path, source_path=relocated)
        except ContractError as error:
            print("Changed source correctly rejected:", error)
        else:
            raise AssertionError("Changed source should have been rejected")
    print("Temporary files removed. No PDF parsing, AI calls, or PDF export occurred.")


if __name__ == "__main__":
    main()
