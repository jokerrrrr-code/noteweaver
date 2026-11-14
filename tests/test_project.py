from pathlib import Path
import unittest
from uuid import UUID

from noteweaver import (
    ContractError, DocumentInfo, ProjectState, add_manual_note, approve_note,
    create_project, delete_note, list_notes, update_note,
)


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.document = DocumentInfo("sha256:" + "0" * 64, "synthetic.pdf", 3)
        self.empty = create_project(self.document, Path("local_data/synthetic.pdf"))
        self.project = add_manual_note(
            self.empty, original_page=2, title="機會成本 Opportunity cost",
            content="放棄的最佳選擇。\nThe next-best alternative.",
        )
        self.note_id = self.project.notes[0].note_id

    def test_create_uses_metadata_without_reading_source(self):
        self.assertEqual(self.empty.document, self.document)
        self.assertEqual(self.empty.source_path, "local_data/synthetic.pdf")
        self.assertEqual(self.empty.notes, ())
        self.assertEqual(self.empty.requests, ())
        for bad in ("", "  ", None, 42):
            with self.subTest(path=bad), self.assertRaises(ContractError):
                create_project(self.document, bad)

    def test_add_preserves_unicode_and_builds_a_user_draft(self):
        note = self.project.notes[0]
        self.assertEqual(UUID(note.note_id).version, 4)
        self.assertEqual(note.document_id, self.document.document_id)
        self.assertEqual(note.original_page, 2)
        self.assertEqual(note.language, "zh-Hant")
        self.assertEqual(note.status, "draft")
        self.assertEqual(note.sections[0].origin, "user")
        self.assertEqual(note.sections[0].kind, "personal")
        self.assertEqual(note.sections[0].content, "放棄的最佳選擇。\nThe next-best alternative.")
        self.assertIsNone(note.request_id)
        self.assertEqual(note.source_pages, ())
        self.assertEqual(self.empty.notes, ())
        self.assertEqual(ProjectState.from_json(self.project.to_json()), self.project)

    def test_add_multiple_notes_keeps_insertion_order_and_unique_ids(self):
        result = self.project
        for page in (1, 2):
            result = add_manual_note(result, original_page=page, title="Note", content="English", language="en")
        self.assertEqual([note.original_page for note in result.notes], [2, 1, 2])
        self.assertEqual(len({note.note_id for note in result.notes}), 3)
        self.assertEqual(result.notes[-1].language, "en")
        self.assertEqual(result.notes[0], self.project.notes[0])

    def test_invalid_add_leaves_previous_project_unchanged(self):
        before = self.project.to_json()
        cases = [{"original_page": p} for p in (0, 4, -1, True, 2.0, "2")]
        cases += [{name: value} for name in ("title", "content", "language")
                  for value in ("", "  ", 42, None)]
        for changes in cases:
            args = dict(original_page=2, title="Title", content="Body", language="en")
            args.update(changes)
            with self.subTest(changes=changes), self.assertRaises(ContractError):
                add_manual_note(self.project, **args)
        self.assertEqual(self.project.to_json(), before)

    def test_approve_then_edit_requires_confirmation_again(self):
        approved = approve_note(self.project, self.note_id)
        self.assertEqual(self.project.notes[0].status, "draft")
        self.assertEqual(approved.notes[0].status, "approved")
        self.assertEqual(approve_note(approved, self.note_id), approved)
        edited = update_note(approved, self.note_id, title="修訂", content="New explanation 新解釋")
        note = edited.notes[0]
        self.assertEqual(note.status, "draft")
        self.assertEqual(note.title, "修訂")
        self.assertEqual(note.sections[0].content, "New explanation 新解釋")
        for field in ("note_id", "document_id", "original_page", "language", "request_id"):
            self.assertEqual(getattr(note, field), getattr(approved.notes[0], field))
        self.assertEqual(approved.notes[0].status, "approved")
        self.assertEqual(list_notes(edited, status="approved"), ())

    def test_title_only_edit_preserves_structured_body_and_provenance(self):
        fixture = Path(__file__).resolve().parents[1] / "examples/data/project.json"
        project = ProjectState.from_json(fixture.read_text(encoding="utf-8"))
        old = project.notes[0]
        result = update_note(project, old.note_id, title="My revised title")
        self.assertEqual(result.notes[0].sections, old.sections)
        self.assertEqual(result.notes[0].source_pages, old.source_pages)
        self.assertEqual(result.notes[0].status, "draft")
        self.assertEqual(result.requests, project.requests)
        self.assertEqual(result.notes[1:], project.notes[1:])

    def test_body_replacement_marks_user_authorship_and_removes_source_claims(self):
        fixture = Path(__file__).resolve().parents[1] / "examples/data/project.json"
        project = ProjectState.from_json(fixture.read_text(encoding="utf-8"))
        old = project.notes[0]
        result = update_note(project, old.note_id, content="My own explanation")
        note = result.notes[0]
        self.assertEqual(note.title, old.title)
        self.assertEqual(len(note.sections), 1)
        self.assertEqual(note.sections[0].origin, "user")
        self.assertEqual(note.source_pages, ())
        self.assertEqual(note.request_id, old.request_id)
        self.assertEqual(result.requests, project.requests)

    def test_invalid_update_does_not_change_approved_note(self):
        approved = approve_note(self.project, self.note_id)
        before = approved.to_json()
        for changes in ({}, {"title": " "}, {"content": ""}, {"title": 42},
                        {"content": False}, {"title": "valid", "content": " "}):
            with self.subTest(changes=changes), self.assertRaises(ContractError):
                update_note(approved, self.note_id, **changes)
        self.assertEqual(approved.to_json(), before)

    def test_edit_and_delete_preserve_other_notes_and_order(self):
        project = self.project
        for content in ("second", "third"):
            project = add_manual_note(project, original_page=2, title="same title", content=content)
        middle = project.notes[1].note_id
        edited = update_note(project, middle, content="edited second")
        self.assertEqual([n.note_id for n in edited.notes], [n.note_id for n in project.notes])
        result = delete_note(edited, middle)
        self.assertEqual(result.notes, (project.notes[0], project.notes[2]))
        self.assertEqual(len(project.notes), 3)
        self.assertEqual(delete_note(self.project, self.note_id).notes, ())

    def test_delete_keeps_request_history_for_remaining_notes(self):
        fixture = Path(__file__).resolve().parents[1] / "examples/data/project.json"
        project = ProjectState.from_json(fixture.read_text(encoding="utf-8"))
        result = delete_note(project, project.notes[0].note_id)
        self.assertEqual(result.requests, project.requests)
        self.assertEqual(result.notes, project.notes[1:])

    def test_unknown_or_invalid_id_never_modifies_project(self):
        before = self.project.to_json()
        operations = (
            lambda key: update_note(self.project, key, title="Updated"),
            lambda key: approve_note(self.project, key),
            lambda key: delete_note(self.project, key),
        )
        for operation in operations:
            with self.assertRaises(KeyError):
                operation("not-a-real-id")
            for key in (None, "", "  ", 1):
                with self.subTest(key=key), self.assertRaises(ContractError):
                    operation(key)
        self.assertEqual(self.project.to_json(), before)

    def test_list_filters_intersect_and_keep_order(self):
        project = add_manual_note(self.project, original_page=1, title="Other", content="Body")
        project = add_manual_note(project, original_page=2, title="Another", content="Body")
        project = approve_note(project, self.note_id)
        self.assertEqual(list_notes(project), project.notes)
        self.assertEqual(list_notes(project, original_page=2), (project.notes[0], project.notes[2]))
        self.assertEqual(list_notes(project, status="draft"), project.notes[1:])
        self.assertEqual(list_notes(project, original_page=2, status="approved"), (project.notes[0],))
        self.assertEqual(list_notes(project, original_page=3), ())
        self.assertEqual(list_notes(self.empty), ())

    def test_invalid_filters_report_errors_instead_of_hiding_notes(self):
        for page in (0, 4, True, "2", 2.0):
            with self.subTest(page=page), self.assertRaises(ContractError):
                list_notes(self.project, original_page=page)
        for status in ("APPROVED", "", False, 1, []):
            with self.subTest(status=status), self.assertRaises(ContractError):
                list_notes(self.project, status=status)


if __name__ == "__main__":
    unittest.main()
