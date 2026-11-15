"""Offline Groq transport and real-PDF-to-project integration checks."""
from dataclasses import replace
import io
import json
import os
from pathlib import Path
import shutil
import ssl
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError

from noteweaver import (
    ContractError, FakeNoteProvider, GenerationError, GroqProvider,
    approve_note, create_project, generate_note, load_project, save_project,
    update_note,
)
from noteweaver.pdf_reader import PDFReader

SAMPLE = Path(__file__).resolve().parents[1] / "examples/data/sample_lecture_3p.pdf"
DUMMY_KEY = "dummy-groq-key-for-offline-tests"


def response_bytes(language="en"):
    note = {
        "title": "Opportunity cost" if language == "en" else "機會成本",
        "sections": [
            {"kind": "explanation", "content": "Time matters." if language == "en" else "時間也有價值。", "origin": "lecture"},
            {"kind": "example", "content": "A study example.", "origin": "ai"},
        ],
    }
    return json.dumps({"choices": [{"message": {"content": json.dumps(note)}}]}).encode()


class GroqWorkflowTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.source = self.root / "lecture.pdf"
        shutil.copyfile(SAMPLE, self.source)
        self.reader = PDFReader(render_preview=False)
        self.project = create_project(self.reader.inspect(self.source), self.source)
        self.environment = patch.dict(os.environ, {}, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def generate(self, provider, **kwargs):
        return generate_note(self.project, original_page=2, question="Explain opportunity cost.",
                             provider=provider, **kwargs)

    def test_groq_request_uses_fixed_endpoint_key_and_json_format(self):
        os.environ.update(GROQ_API_KEY=DUMMY_KEY, NOTEWEAVER_API_KEY="wrong-key",
                          NOTEWEAVER_BASE_URL="https://wrong.invalid", NOTEWEAVER_MODEL="wrong-model")
        with patch("urllib.request.urlopen", return_value=io.BytesIO(response_bytes())) as call:
            result = self.generate(GroqProvider())
        call.assert_called_once()
        request = call.call_args.args[0]
        body = json.loads(request.data)
        self.assertEqual(request.full_url, "https://api.groq.com/openai/v1/chat/completions")
        self.assertEqual(request.get_header("Authorization"), f"Bearer {DUMMY_KEY}")
        self.assertEqual(request.get_header("User-agent"), "NoteWeaver/0.0.1")
        self.assertEqual(body["model"], "openai/gpt-oss-20b")
        self.assertEqual(body["response_format"], {"type": "json_object"})
        self.assertEqual(body["max_completion_tokens"], 4096)
        self.assertEqual(call.call_args.kwargs["timeout"], 60)
        self.assertIn("[page 2]", body["messages"][1]["content"])
        self.assertNotIn("[page 1]", body["messages"][1]["content"])
        self.assertNotIn(DUMMY_KEY, json.dumps(body))
        self.assertEqual(result.notes[0].status, "draft")
        self.assertEqual(result.requests[0].context_pages, (2,))
        self.assertNotIn(DUMMY_KEY, result.to_json())
        self.assertEqual(self.project.notes, ())

    def test_explicit_configuration_overrides_environment(self):
        os.environ["GROQ_API_KEY"] = "wrong-key"
        provider = GroqProvider(api_key=DUMMY_KEY, model="test-model", timeout=12, max_completion_tokens=512)
        with patch("urllib.request.urlopen", return_value=io.BytesIO(response_bytes())) as call:
            self.generate(provider)
        self.assertEqual(call.call_args.args[0].get_header("Authorization"), f"Bearer {DUMMY_KEY}")
        self.assertEqual(json.loads(call.call_args.args[0].data)["model"], "test-model")
        self.assertEqual(json.loads(call.call_args.args[0].data)["max_completion_tokens"], 512)
        self.assertEqual(call.call_args.kwargs["timeout"], 12)
        self.assertNotIn(DUMMY_KEY, repr(provider))

    def test_missing_groq_key_does_not_reuse_other_service_credentials(self):
        os.environ.update(OPENAI_API_KEY="other-service-key", NOTEWEAVER_API_KEY="other-key")
        with patch("urllib.request.urlopen") as call:
            with self.assertRaisesRegex(GenerationError, "GROQ_API_KEY"):
                self.generate(GroqProvider())
        call.assert_not_called()

    def test_invalid_provider_configuration_is_rejected(self):
        for config in ({"api_key": " "}, {"model": ""}, {"model": None}, {"timeout": 0},
                       {"timeout": float("nan")}, {"max_completion_tokens": True},
                       {"max_completion_tokens": -1}, {"max_completion_tokens": None}):
            with self.subTest(config=config), self.assertRaises(ContractError):
                GroqProvider(**config)

    def test_auth_rate_limit_timeout_and_network_errors_do_not_retry_or_leak(self):
        errors = [
            (HTTPError("https://example.invalid", 401, DUMMY_KEY, None, None), "API key was rejected"),
            (HTTPError("https://example.invalid", 429, DUMMY_KEY, None, None), "rate limit"),
            (TimeoutError(DUMMY_KEY), "timed out"),
            (URLError(DUMMY_KEY), "connection failed"),
            (URLError(ssl.SSLCertVerificationError(1, DUMMY_KEY)), "certificate verification failed"),
        ]
        for error, message in errors:
            with self.subTest(error=type(error).__name__):
                with patch("urllib.request.urlopen", side_effect=error) as call:
                    with self.assertRaisesRegex(GenerationError, message) as caught:
                        self.generate(GroqProvider(api_key=DUMMY_KEY))
                call.assert_called_once()
                self.assertNotIn(DUMMY_KEY, str(caught.exception))
                self.assertEqual(self.project.notes, ())
                self.assertEqual(self.project.requests, ())

    def test_malformed_http_response_is_not_a_successful_draft(self):
        for body in (b"not json", b"\xff", b'{}', b'{"choices": []}'):
            with self.subTest(body=body):
                with patch("urllib.request.urlopen", return_value=io.BytesIO(body)):
                    with self.assertRaises(GenerationError):
                        self.generate(GroqProvider(api_key=DUMMY_KEY))
        self.assertEqual(self.project.notes, ())

    def test_live_shaped_response_integrates_with_edit_approval_and_persistence(self):
        for language in ("en", "zh-Hant"):
            with self.subTest(language=language):
                with patch("urllib.request.urlopen", return_value=io.BytesIO(response_bytes(language))):
                    project = self.generate(GroqProvider(api_key=DUMMY_KEY), language=language)
                note = project.notes[-1]
                self.assertEqual(note.language, language)
                self.assertEqual(note.request_id, project.requests[-1].request_id)
                project = approve_note(project, note.note_id)
                saved = save_project(project, self.root / f"{language}.json")
                self.assertEqual(load_project(saved), project)
                edited = update_note(project, note.note_id, content="My reviewed explanation.")
                self.assertEqual(edited.notes[-1].status, "draft")
                self.assertNotIn(DUMMY_KEY, saved.read_text())
                self.assertEqual(self.source.read_bytes(), SAMPLE.read_bytes())

    def test_explicit_multi_page_context_and_repeated_generation_keep_history(self):
        first = self.generate(FakeNoteProvider(), context_pages=(1, 2, 3))
        second = generate_note(first, original_page=2, question="Give another example.", provider=FakeNoteProvider())
        self.assertEqual(second.notes[0], first.notes[0])
        self.assertEqual(len(second.requests), 2)
        self.assertNotEqual(second.requests[0].request_id, second.requests[1].request_id)
        self.assertEqual(second.requests[0].context_pages, (1, 2, 3))
        self.assertEqual(second.requests[1].context_pages, (2,))
        self.assertTrue(all(note.status == "draft" for note in second.notes))

    def test_changed_source_is_rejected_before_provider_call(self):
        self.source.write_bytes(self.source.read_bytes() + b"\nchanged")
        provider = Mock()
        with self.assertRaisesRegex(ContractError, "source document changed"):
            self.generate(provider)
        provider.generate.assert_not_called()

    def test_incorrect_metadata_is_rejected_before_provider_call(self):
        self.project = replace(self.project, document=replace(self.project.document, page_count=4))
        provider = Mock()
        with self.assertRaisesRegex(ContractError, "metadata"):
            self.generate(provider)
        provider.generate.assert_not_called()

    def test_relative_source_and_invalid_context_are_rejected_before_provider_call(self):
        provider = Mock()
        relative = replace(self.project, source_path="lecture.pdf")
        with self.assertRaisesRegex(ContractError, "absolute source path"):
            generate_note(relative, original_page=2, question="Why?", provider=provider)
        for pages in ((1,), (2, 2), (2, 4)):
            with self.subTest(pages=pages), self.assertRaises(ContractError):
                self.generate(provider, context_pages=pages)
        provider.generate.assert_not_called()

    def test_provider_failure_preserves_existing_project_and_saved_file(self):
        self.project = self.generate(FakeNoteProvider())
        saved = save_project(self.project, self.root / "existing.json")
        before = saved.read_bytes()
        with self.assertRaises(GenerationError):
            self.generate(FakeNoteProvider(fail=True))
        self.assertEqual(saved.read_bytes(), before)
        self.assertEqual(load_project(saved), self.project)

    def test_source_changed_during_generation_prevents_attachment(self):
        class ChangingProvider:
            def generate(inner, document, request, context):
                note = FakeNoteProvider().generate(document, request, context)
                self.source.write_bytes(self.source.read_bytes() + b"\nchanged")
                return note
        with self.assertRaisesRegex(ContractError, "source document changed"):
            self.generate(ChangingProvider())
        self.assertEqual(self.project.notes, ())
        self.assertEqual(self.project.requests, ())


if __name__ == "__main__":
    unittest.main()
