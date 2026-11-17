"""Exercise the notebook's provider selection with offline HTTP responses only."""

from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError

from noteweaver import (
    FakeNoteProvider, GenerationError, GroqProvider, OpenAICompatibleProvider,
    create_project, generate_note,
)
from noteweaver.pdf_reader import PDFReader


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = json.loads((ROOT / "examples/generation_workflow_demo.ipynb").read_text())
PROVIDER_CELL = next("".join(c["source"]) for c in NOTEBOOK["cells"] if c["id"] == "groq-05")
DUMMY_KEY = "dummy-openrouter-key-for-offline-tests"


class NotebookProviderTests(unittest.TestCase):
    def setUp(self):
        environment = patch.dict(os.environ, {}, clear=True)
        environment.start()
        self.addCleanup(environment.stop)
        self.source = (ROOT / "examples/data/sample_lecture_3p.pdf").resolve()
        self.project = create_project(PDFReader(render_preview=False).inspect(self.source), self.source)

    def select(self, mode, entered=DUMMY_KEY):
        prompt = Mock(return_value=entered)
        namespace = dict(
            MODE=mode, os=os, getpass=prompt, FakeNoteProvider=FakeNoteProvider,
            GroqProvider=GroqProvider, OpenAICompatibleProvider=OpenAICompatibleProvider,
        )
        output = io.StringIO()
        with redirect_stdout(output), patch("urllib.request.urlopen") as transport:
            exec(compile(PROVIDER_CELL, "notebook-provider-cell", "exec"), namespace)
        transport.assert_not_called()
        self.assertNotIn("entered_key", namespace)
        self.assertNotIn(DUMMY_KEY, output.getvalue())
        return namespace["provider"], prompt

    def generate(self, provider):
        return generate_note(self.project, original_page=2, question="Why is time an opportunity cost?",
                             language="en", style="example", provider=provider)

    def test_default_offline_mode_does_not_prompt_or_call_network(self):
        setup = next("".join(c["source"]) for c in NOTEBOOK["cells"] if c["id"] == "groq-01")
        self.assertIn('MODE = "offline"', setup)
        os.environ["OPENROUTER_API_KEY"] = DUMMY_KEY
        provider, prompt = self.select("offline")
        self.assertIsInstance(provider, FakeNoteProvider)
        prompt.assert_not_called()
        with patch("urllib.request.urlopen") as transport:
            self.assertEqual(self.generate(provider).notes[-1].status, "draft")
        transport.assert_not_called()

    def test_openrouter_prompt_and_environment_send_only_to_selected_service(self):
        os.environ.update(OPENAI_API_KEY="wrong-openai-key", GROQ_API_KEY="wrong-groq-key",
                          NOTEWEAVER_API_KEY="wrong-generic-key",
                          NOTEWEAVER_BASE_URL="https://wrong.invalid", NOTEWEAVER_MODEL="wrong-model")
        reply = json.dumps({"choices": [{"message": {"content": json.dumps({
            "title": "Opportunity cost", "sections": [
                {"kind": "explanation", "content": "Time has alternative uses.", "origin": "lecture"},
                {"kind": "example", "content": "A free event takes study time.", "origin": "ai"},
            ],
        })}}]}).encode()
        for use_environment in (False, True):
            with self.subTest(use_environment=use_environment):
                if use_environment:
                    os.environ["OPENROUTER_API_KEY"] = f" {DUMMY_KEY} "
                provider, prompt = self.select("openrouter", entered=f" {DUMMY_KEY} ")
                self.assertEqual(prompt.call_count, 0 if use_environment else 1)
                with patch("urllib.request.urlopen", return_value=io.BytesIO(reply)) as transport:
                    result = self.generate(provider)
                transport.assert_called_once()
                request = transport.call_args.args[0]
                body = json.loads(request.data)
                self.assertEqual(request.full_url, "https://openrouter.ai/api/v1/chat/completions")
                self.assertEqual(request.get_header("Authorization"), f"Bearer {DUMMY_KEY}")
                self.assertEqual(body["model"], "openrouter/free")
                self.assertEqual(body["response_format"], {"type": "json_object"})
                self.assertEqual(transport.call_args.kwargs["timeout"], 120)
                self.assertIn("[page 2]", body["messages"][1]["content"])
                self.assertNotIn("[page 1]", body["messages"][1]["content"])
                self.assertNotIn(DUMMY_KEY, json.dumps(body))
                self.assertNotIn(DUMMY_KEY, result.to_json())
                self.assertEqual(result.notes[-1].status, "draft")
                self.assertEqual(result.notes[-1].source_pages, (2,))
                self.assertEqual(self.project.notes, ())

    def test_blank_key_disables_generation_instead_of_reusing_other_credentials(self):
        os.environ.update(OPENAI_API_KEY="wrong-key", OPENROUTER_API_KEY=" ")
        provider, prompt = self.select("openrouter", entered=" ")
        prompt.assert_called_once()
        self.assertIsNone(provider)

    def test_groq_selection_still_uses_its_own_credentials(self):
        os.environ.update(OPENROUTER_API_KEY=DUMMY_KEY, GROQ_API_KEY="dummy-groq-key")
        provider, prompt = self.select("groq")
        self.assertIsInstance(provider, GroqProvider)
        prompt.assert_not_called()
        with patch("urllib.request.urlopen", side_effect=HTTPError("https://example.invalid", 401, "", None, None)) as transport:
            with self.assertRaises(GenerationError):
                self.generate(provider)
        request = transport.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.groq.com/openai/v1/chat/completions")
        self.assertEqual(request.get_header("Authorization"), "Bearer dummy-groq-key")

    def test_openrouter_errors_preserve_notes_without_retry_or_key_disclosure(self):
        self.project = self.generate(FakeNoteProvider())
        before = self.project.to_json()
        provider, _ = self.select("openrouter")
        for status in (401, 402, 403, 429):
            with self.subTest(status=status):
                error = HTTPError("https://example.invalid", status, DUMMY_KEY, None, io.BytesIO(DUMMY_KEY.encode()))
                with patch("urllib.request.urlopen", side_effect=error) as transport:
                    with self.assertRaises(GenerationError) as caught:
                        self.generate(provider)
                transport.assert_called_once()
                self.assertNotIn(DUMMY_KEY, str(caught.exception))
                self.assertEqual(self.project.to_json(), before)

    def test_invalid_mode_is_explicit(self):
        with self.assertRaisesRegex(ValueError, "offline.*openrouter.*groq"):
            self.select("unknown")


if __name__ == "__main__":
    unittest.main()
