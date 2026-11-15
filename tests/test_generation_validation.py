"""Offline regressions for preflight validation and strict provider response parsing."""
from dataclasses import replace
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from noteweaver import (
    ContractError, DocumentInfo, NoteGenerator, NoteRequest,
    PageContent, add_manual_note, approve_note, create_project, load_project,
    save_project, update_note,
)
from noteweaver.pdf_reader import PDFReader
from noteweaver.providers import FakeNoteProvider, GenerationError, OpenAICompatibleProvider


class GenerationValidationTests(unittest.TestCase):
    def setUp(self):
        self.document = DocumentInfo("sha256:" + "0" * 64, "lecture.pdf", 3)
        self.request = NoteRequest(
            request_id="validation-request", document_id=self.document.document_id,
            original_page=2, question="Explain opportunity cost.", context_pages=(2,),
            language="en",
        )
        self.page = PageContent(self.document.document_id, 2, "Opportunity cost includes time.", "ok")
        self.other_id = "sha256:" + "1" * 64

    def assert_rejected_before_provider(self, document, request, context):
        provider = Mock()
        with self.assertRaises(ContractError):
            NoteGenerator(provider).generate(document, request, context)
        provider.generate.assert_not_called()

    def test_foreign_request_and_foreign_context_never_reach_provider(self):
        for request, context in (
            (replace(self.request, document_id=self.other_id), (self.page,)),
            (self.request, (replace(self.page, document_id=self.other_id),)),
        ):
            with self.subTest(request=request, context=context):
                self.assert_rejected_before_provider(self.document, request, context)

    def test_out_of_range_context_never_reaches_provider(self):
        request = replace(self.request, original_page=4, context_pages=(4,))
        page = replace(self.page, original_page=4)
        self.assert_rejected_before_provider(self.document, request, (page,))

    def test_duplicate_missing_and_unexpected_pages_never_reach_provider(self):
        for context in ((self.page, self.page), (), (replace(self.page, original_page=1),)):
            with self.subTest(context=context):
                self.assert_rejected_before_provider(self.document, self.request, context)

    def test_invalid_input_types_never_reach_provider(self):
        cases = (
            (None, self.request, (self.page,)),
            (self.document, None, (self.page,)),
            (self.document, self.request, [self.page]),
            (self.document, self.request, (None,)),
            (self.document, self.request, ({"original_page": 2},)),
        )
        for document, request, context in cases:
            with self.subTest(document=document, request=request, context=context):
                self.assert_rejected_before_provider(document, request, context)

    def test_failed_extraction_never_reaches_provider(self):
        for page in (
            replace(self.page, text="", extraction_status="empty"),
            replace(self.page, text="", extraction_status="error", error_message="Extraction failed"),
        ):
            with self.subTest(page=page):
                self.assert_rejected_before_provider(self.document, self.request, (page,))

    def test_invalid_provider_result_has_a_clear_error(self):
        for value in (None, {}, "not a note"):
            with self.subTest(value=value):
                provider = Mock()
                provider.generate.return_value = value
                with self.assertRaisesRegex(GenerationError, "GeneratedNote"):
                    NoteGenerator(provider).generate(self.document, self.request, (self.page,))

    def valid_payload(self):
        return {"title": " Opportunity cost ", "sections": [
            {"kind": "explanation", "content": " Time is a scarce resource. ", "origin": "lecture"},
            {"kind": "example", "content": "A personal illustration.\nA second line.", "origin": "ai"},
        ]}

    def generate_payload(self, note_payload, *, language="en"):
        envelope = {"choices": [{"message": {"content": json.dumps(note_payload)}}]}
        with patch.dict("os.environ", {"NOTEWEAVER_API_KEY": "dummy-offline-key"}, clear=True):
            with patch("urllib.request.urlopen", return_value=io.BytesIO(json.dumps(envelope).encode())) as call:
                note = NoteGenerator(OpenAICompatibleProvider()).generate(
                    self.document, replace(self.request, language=language), (self.page,),
                )
                call.assert_called_once()
                return note

    def test_valid_english_and_chinese_responses_preserve_text_and_draft_state(self):
        for language, title, content in (
            ("en", " Opportunity cost ", " Time matters.\nKeep this line. "),
            ("zh-Hant", " 機會成本 ", " 時間也有價值。\n保留換行。 "),
        ):
            with self.subTest(language=language):
                payload = self.valid_payload()
                payload["title"] = title
                payload["sections"][0]["content"] = content
                note = self.generate_payload(payload, language=language)
                self.assertEqual(note.title, title.strip())
                self.assertEqual(note.sections[0].content, content.strip())
                self.assertEqual(note.sections[1].origin, "ai")
                self.assertEqual(note.language, language)
                self.assertEqual(note.source_pages, (2,))
                self.assertEqual(note.request_id, self.request.request_id)
                self.assertEqual(note.status, "draft")

    def test_invalid_titles_and_section_text_are_not_coerced(self):
        for field in ("title", "content"):
            for invalid in (None, 42, True, [], {"private": "raw-response-marker"}, "", " \n "):
                with self.subTest(field=field, value=invalid):
                    payload = self.valid_payload()
                    if field == "title":
                        payload["title"] = invalid
                    else:
                        payload["sections"][0]["content"] = invalid
                    with self.assertRaisesRegex(GenerationError, "malformed note payload") as caught:
                        self.generate_payload(payload)
                    self.assertNotIn("raw-response-marker", str(caught.exception))

    def test_invalid_note_and_section_shapes_are_rejected(self):
        cases = [None, [], "note", {}, {"title": "Only a title"}]
        for sections in (None, {}, "text", [], [None], ["text"], [{}],
                         [{"kind": "unknown", "content": "text", "origin": "ai"}],
                         [{"kind": "example", "content": "text", "origin": "unknown"}]):
            cases.append({"title": "Title", "sections": sections})
        for payload in cases:
            with self.subTest(payload=payload):
                with self.assertRaisesRegex(GenerationError, "malformed note payload"):
                    self.generate_payload(payload)

    def test_malformed_response_envelopes_have_a_clear_error(self):
        for envelope in ({}, {"choices": []}, {"choices": [{"message": {"content": None}}]},
                         {"choices": [{"message": {"content": "not JSON"}}]}):
            with self.subTest(envelope=envelope):
                with patch.dict("os.environ", {"NOTEWEAVER_API_KEY": "dummy-offline-key"}, clear=True):
                    with patch("urllib.request.urlopen", return_value=io.BytesIO(json.dumps(envelope).encode())):
                        with self.assertRaisesRegex(GenerationError, "malformed note payload"):
                            OpenAICompatibleProvider().generate(self.document, self.request, (self.page,))

    def test_generation_integrates_with_editing_and_verified_persistence(self):
        source = Path(__file__).resolve().parents[1] / "examples/data/sample_lecture_3p.pdf"
        reader = PDFReader(render_preview=False)
        document = reader.inspect(source)
        page = reader.read_page(source, 2)
        request = replace(self.request, document_id=document.document_id)
        project = add_manual_note(create_project(document, source), original_page=2,
                                  title="Keep this note", content="My existing work.", language="en")
        original_note = project.notes[0]
        note = NoteGenerator(FakeNoteProvider()).generate(document, request, (page,))
        project = replace(project, requests=(request,), notes=project.notes + (note,))
        project = approve_note(project, note.note_id)
        with tempfile.TemporaryDirectory() as folder:
            saved = save_project(project, Path(folder) / "study.json")
            loaded = load_project(saved)
            self.assertEqual(loaded, project)
            edited = update_note(loaded, note.note_id, content="Reviewed wording.")
            self.assertEqual(edited.notes[1].status, "draft")
            self.assertEqual(edited.notes[0], original_note)
            self.assertEqual(edited.requests, (request,))
            before = saved.read_bytes()
            invalid = self.valid_payload()
            invalid["title"] = None
            with self.assertRaises(GenerationError):
                self.generate_payload(invalid)
            self.assertEqual(saved.read_bytes(), before)
            self.assertEqual(load_project(saved), project)


if __name__ == "__main__":
    unittest.main()
