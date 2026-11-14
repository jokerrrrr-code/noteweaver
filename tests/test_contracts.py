from dataclasses import FrozenInstanceError, replace
import json
from pathlib import Path
import tempfile
import unittest

from noteweaver import (
    ContractError, DocumentInfo, ExportResult, GeneratedNote, NotePageLocation,
    NoteRequest, NoteSection, OriginalPageLocation, PageContent, ProjectState,
    document_id_for_file, validate_export, validate_generation, validate_page,
    validate_request, verify_source,
)

DATA = Path(__file__).resolve().parents[1] / "examples" / "data"


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.project = ProjectState.from_json((DATA / "project.json").read_text(encoding="utf-8"))
        self.document = self.project.document
        self.request = self.project.requests[0]
        self.approved, self.manual = self.project.notes
        self.draft = replace(self.approved, status="draft")
        self.page = PageContent.from_json((DATA / "page.json").read_text(encoding="utf-8"))
        self.export = ExportResult.from_json((DATA / "export.json").read_text(encoding="utf-8"))

    def test_fixture_pipeline_and_unicode_roundtrip(self):
        validate_generation(self.document, self.request, (self.page,), self.draft)
        validate_export(self.project, self.export)
        self.assertIn("機會成本", self.project.to_json())
        self.assertEqual(ProjectState.from_json(self.project.to_json()), self.project)
        self.assertEqual(self.project.to_dict()["notes"][0]["sections"][0]["origin"], "lecture")

    def test_manual_project_needs_no_request_or_key(self):
        project = ProjectState(self.document, "demo.pdf", notes=(self.manual,))
        self.assertEqual(project.requests, ())
        self.assertEqual(ProjectState.from_dict(project.to_dict()), project)

    def test_strict_page_types_and_bounds(self):
        for value in (0, -1, True, 2.0, "2"):
            with self.subTest(value=value), self.assertRaises(ContractError):
                replace(self.page, original_page=value)
        with self.assertRaises(ContractError):
            validate_page(self.document, replace(self.page, original_page=4))

    def test_document_identity_and_counts(self):
        for value in ("demo.pdf", "sha256:ABC", "sha256:" + "A" * 64):
            with self.subTest(value=value), self.assertRaises(ContractError):
                replace(self.document, document_id=value)
        with self.assertRaises(ContractError):
            replace(self.document, page_count=True)
        with self.assertRaises(ContractError):
            validate_page(self.document, replace(self.page, document_id="sha256:" + "1" * 64))

    def test_empty_and_failed_extraction_are_distinct(self):
        empty = replace(self.page, text="", extraction_status="empty")
        error = replace(empty, extraction_status="error", error_message="Cannot decode text")
        validate_page(self.document, empty)
        validate_page(self.document, error)
        for changes in ({"text": ""}, {"extraction_status": "empty"},
                        {"text": "", "extraction_status": "error"},
                        {"error_message": "unexpected"}):
            with self.subTest(changes=changes), self.assertRaises(ContractError):
                replace(self.page, **changes)

    def test_unknown_fields_rejected_including_nested_credentials(self):
        for nested in (False, True):
            value = self.project.to_dict()
            target = value["notes"][0] if nested else value
            target["api_key"] = "placeholder-not-a-real-key"
            with self.subTest(nested=nested), self.assertRaises(ContractError):
                ProjectState.from_dict(value)

    def test_missing_fields_and_wrong_container_types(self):
        with self.assertRaises(ContractError):
            NoteRequest.from_dict({"question": "test"})
        for value in ([], None, "project"):
            with self.subTest(value=value), self.assertRaises(ContractError):
                ProjectState.from_dict(value)
        value = self.project.to_dict()
        value["notes"][0]["sections"] = "not a list"
        with self.assertRaises(ContractError):
            ProjectState.from_dict(value)

    def test_schema_version_must_be_explicit_and_supported(self):
        for version in (0, 2, "1", True):
            value = self.project.to_dict()
            value["schema_version"] = version
            with self.subTest(version=version), self.assertRaises(ContractError):
                ProjectState.from_dict(value)
        value = self.project.to_dict()
        del value["schema_version"]
        with self.assertRaises(ContractError):
            ProjectState.from_dict(value)

    def test_duplicate_json_keys_and_malformed_json_rejected(self):
        for value in ('{"schema_version":1,"schema_version":2}', '{', 'null'):
            with self.subTest(value=value), self.assertRaises(ContractError):
                ProjectState.from_json(value)

    def test_invalid_style_status_and_blank_content(self):
        with self.assertRaises(ContractError):
            replace(self.request, style="chat")
        with self.assertRaises(ContractError):
            replace(self.draft, status="done")
        with self.assertRaises(ContractError):
            NoteSection("example", "   ", "ai")
        with self.assertRaises(ContractError):
            NoteSection("example", "test", "verified")
        with self.assertRaises(ContractError):
            replace(self.draft, sections=())

    def test_notes_have_explicit_provenance(self):
        with self.assertRaises(ContractError):
            replace(self.draft, request_id=None)
        with self.assertRaises(ContractError):
            replace(self.draft, source_pages=())

    def test_context_must_include_target_and_valid_unique_pages(self):
        for pages in ((), (1,), (2, 2), (True, 2)):
            with self.subTest(pages=pages), self.assertRaises(ContractError):
                replace(self.request, context_pages=pages)
        with self.assertRaises(ContractError):
            validate_request(self.document, replace(self.request, context_pages=(2, 4)))

    def test_actual_context_must_match_declared_context(self):
        other = replace(self.page, original_page=1)
        for context in ((), (other,), (self.page, self.page), (self.page, other)):
            with self.subTest(context=context), self.assertRaises(ContractError):
                validate_generation(self.document, self.request, context, self.draft)
        with self.assertRaises(ContractError):
            empty = replace(self.page, text="", extraction_status="empty")
            validate_generation(self.document, self.request, (empty,), self.draft)

    def test_generated_note_linkage_and_draft_status(self):
        for changes in ({"request_id": "different"}, {"original_page": 1},
                        {"source_pages": (1,)}, {"language": "en"}, {"status": "approved"},
                        {"document_id": "sha256:" + "1" * 64}):
            with self.subTest(changes=changes), self.assertRaises(ContractError):
                validate_generation(self.document, self.request, (self.page,), replace(self.draft, **changes))

    def test_project_rejects_duplicate_ids_and_missing_request(self):
        for changes in ({"requests": (self.request, self.request)},
                        {"notes": (self.approved, self.approved)}, {"requests": ()}):
            with self.subTest(changes=changes), self.assertRaises(ContractError):
                replace(self.project, **changes)

    def test_project_rejects_wrong_document_anchor_and_sources(self):
        for changes in ({"document_id": "sha256:" + "1" * 64},
                        {"original_page": 4}, {"source_pages": (4,)}):
            with self.subTest(changes=changes), self.assertRaises(ContractError):
                replace(self.project, notes=(replace(self.manual, **changes),))

    def test_models_are_immutable_and_edits_can_return_to_draft(self):
        with self.assertRaises(FrozenInstanceError):
            self.approved.title = "changed"
        edited = replace(self.approved, title="我修改的標題", status="draft")
        self.assertEqual(edited.note_id, self.approved.note_id)
        self.assertEqual(self.approved.status, "approved")

    def test_project_order_survives_multiple_notes_on_same_page(self):
        second = replace(self.manual, original_page=2, status="approved")
        project = replace(self.project, notes=(self.approved, second))
        export = replace(self.export, output_page_count=6,
            original_to_output_pages=(OriginalPageLocation(1,1),OriginalPageLocation(2,2),OriginalPageLocation(3,6)),
            note_to_output_pages=(NotePageLocation("note-001",(3,4)),NotePageLocation("note-002",(5,))))
        restored = ProjectState.from_json(project.to_json())
        self.assertEqual(tuple(n.note_id for n in restored.notes), ("note-001", "note-002"))
        validate_export(restored, export)
        with self.assertRaises(ContractError):
            validate_export(replace(restored, notes=tuple(reversed(restored.notes))), export)

    def test_export_excludes_drafts_and_requires_all_approved_notes(self):
        with self.assertRaises(ContractError):
            validate_export(replace(self.project, notes=(self.draft, self.manual)), self.export)
        missing = ExportResult(self.document.document_id, "out.pdf", 3,
            (OriginalPageLocation(1,1),OriginalPageLocation(2,2),OriginalPageLocation(3,3)))
        with self.assertRaises(ContractError):
            validate_export(self.project, missing)
        manual_only = replace(self.project, requests=(), notes=(self.manual,))
        validate_export(manual_only, missing)

    def test_export_rejects_overlaps_gaps_and_wrong_placement(self):
        with self.assertRaises(ContractError):
            replace(self.export, note_to_output_pages=(NotePageLocation("note-001",(2,)),))
        with self.assertRaises(ContractError):
            replace(self.export, output_page_count=5)
        misplaced = replace(self.export,
            original_to_output_pages=(OriginalPageLocation(1,1),OriginalPageLocation(2,3),OriginalPageLocation(3,4)),
            note_to_output_pages=(NotePageLocation("note-001",(2,)),))
        with self.assertRaises(ContractError):
            validate_export(self.project, misplaced)

    def test_note_pages_are_contiguous_and_ordered(self):
        for pages in ((), (3,5), (4,3), (3,3), (0,), (True,)):
            with self.subTest(pages=pages), self.assertRaises(ContractError):
                NotePageLocation("note-001", pages)

    def test_export_map_json_has_no_integer_object_keys(self):
        data = self.export.to_dict()
        self.assertIsInstance(data["original_to_output_pages"], list)
        self.assertEqual(ExportResult.from_json(json.dumps(data)), self.export)

    def test_source_fingerprint_detects_same_name_changed_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "demo.pdf"
            source.write_bytes(b"synthetic bytes; not an actual PDF")
            identity = document_id_for_file(source)
            document = replace(self.document, document_id=identity)
            project = ProjectState(document, "demo.pdf")
            verify_source(project, source)
            copy = Path(folder) / "renamed.pdf"
            copy.write_bytes(source.read_bytes())
            self.assertEqual(document_id_for_file(copy), identity)
            source.write_bytes(b"different bytes, unchanged filename")
            with self.assertRaises(ContractError):
                verify_source(project, source)
            with self.assertRaises(FileNotFoundError):
                verify_source(project, Path(folder) / "missing.pdf")


if __name__ == "__main__":
    unittest.main()
