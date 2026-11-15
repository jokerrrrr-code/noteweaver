"""Tests for Member 2 NoteGenerator and providers.

Fake-provider tests always run (offline). Live-provider tests are skipped
unless NOTEWEAVER_API_KEY or OPENAI_API_KEY is set in the environment.
"""

from __future__ import annotations

import os
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from noteweaver.generation import NoteGenerator, default_generator
from noteweaver.models import (
    ContractError,
    DocumentInfo,
    GeneratedNote,
    NoteRequest,
    NoteSection,
    PageContent,
    validate_generation,
)
from noteweaver.providers import (
    FakeNoteProvider,
    GenerationError,
    OpenAICompatibleProvider,
)
from noteweaver.providers.base import NoteProvider


DATA = Path(__file__).resolve().parents[1] / "examples" / "data"


def _doc() -> DocumentInfo:
    return DocumentInfo(
        document_id="sha256:" + "0" * 64,
        filename="demo.pdf",
        page_count=3,
    )


def _page(original_page: int = 2, text: str = "機會成本是為某個選擇而放棄的最佳替代方案價值。") -> PageContent:
    return PageContent(
        document_id="sha256:" + "0" * 64,
        original_page=original_page,
        text=text,
        extraction_status="ok",
    )


def _request(
    *,
    context_pages: tuple[int, ...] = (2,),
    original_page: int = 2,
    question: str = "機會成本是否只是實際花掉的金錢？",
    language: str = "zh-Hant",
    style: str = "example",
) -> NoteRequest:
    return NoteRequest(
        request_id="request-test-001",
        document_id="sha256:" + "0" * 64,
        original_page=original_page,
        question=question,
        context_pages=context_pages,
        selected_text="機會成本",
        language=language,
        level="first-year",
        style=style,  # type: ignore[arg-type]
    )


class FakeProviderTests(unittest.TestCase):
    """Offline deterministic provider tests."""

    def setUp(self) -> None:
        self.document = _doc()
        self.request = _request()
        self.context = (_page(),)
        self.generator = NoteGenerator(FakeNoteProvider())

    def test_normal_generation_returns_draft_and_passes_validate(self) -> None:
        note = self.generator.generate(self.document, self.request, self.context)
        self.assertEqual(note.status, "draft")
        self.assertEqual(note.request_id, self.request.request_id)
        self.assertEqual(note.document_id, self.document.document_id)
        self.assertEqual(note.original_page, 2)
        self.assertTrue(note.sections)
        self.assertIn("lecture", {s.origin for s in note.sections})
        self.assertIn("ai", {s.origin for s in note.sections})
        self.assertEqual(set(note.source_pages), {2})
        # Shared contract must accept the result
        validate_generation(self.document, self.request, self.context, note)

    def test_english_language_produces_english_title(self) -> None:
        request = _request(language="en", question="Is opportunity cost only money spent?")
        note = self.generator.generate(self.document, request, self.context)
        self.assertEqual(note.language, "en")
        self.assertTrue(note.title)
        self.assertIn("opportunity", note.title.lower() + note.sections[0].content.lower())

    def test_context_mismatch_raises_contract_error(self) -> None:
        # request wants page 2, but context supplies page 1
        bad_context = (_page(original_page=1, text="scarcity text"),)
        with self.assertRaises(ContractError) as cm:
            self.generator.generate(self.document, self.request, bad_context)
        self.assertIn("context", str(cm.exception).lower())

    def test_empty_or_error_page_rejected(self) -> None:
        empty = replace(_page(), text="", extraction_status="empty")
        with self.assertRaises(ContractError):
            self.generator.generate(self.document, self.request, (empty,))

        error_page = PageContent(
            document_id=self.document.document_id,
            original_page=2,
            text="",
            extraction_status="error",
            error_message="parse failed",
        )
        with self.assertRaises(ContractError):
            self.generator.generate(self.document, self.request, (error_page,))

    def test_citing_unprovided_page_is_blocked_by_validation(self) -> None:
        # Provider that claims source_pages outside the supplied context
        class BadProvider:
            def generate(self, document, request, context):
                return GeneratedNote(
                    note_id="bad-note",
                    document_id=document.document_id,
                    original_page=request.original_page,
                    title="Bad",
                    sections=(NoteSection(kind="explanation", content="x", origin="lecture"),),
                    source_pages=(1, 2, 99),  # 99 not in context
                    request_id=request.request_id,
                    language=request.language,
                    status="draft",
                )

        gen = NoteGenerator(BadProvider())  # type: ignore[arg-type]
        with self.assertRaises(ContractError) as cm:
            gen.generate(self.document, self.request, self.context)
        self.assertIn("source_pages", str(cm.exception).lower())

    def test_invalid_output_status_rejected(self) -> None:
        class ApprovedProvider:
            def generate(self, document, request, context):
                return GeneratedNote(
                    note_id="approved-note",
                    document_id=document.document_id,
                    original_page=request.original_page,
                    title="Already approved",
                    sections=(NoteSection(kind="explanation", content="x", origin="ai"),),
                    source_pages=(2,),
                    request_id=request.request_id,
                    language=request.language,
                    status="approved",  # forbidden for new generation
                )

        gen = NoteGenerator(ApprovedProvider())  # type: ignore[arg-type]
        with self.assertRaises(ContractError):
            gen.generate(self.document, self.request, self.context)

    def test_service_failure_raises_generation_error(self) -> None:
        gen = NoteGenerator(FakeNoteProvider(fail=True))
        with self.assertRaises(GenerationError):
            gen.generate(self.document, self.request, self.context)

    def test_default_generator_is_offline_fake(self) -> None:
        gen = default_generator()
        note = gen.generate(self.document, self.request, self.context)
        self.assertEqual(note.status, "draft")
        validate_generation(self.document, self.request, self.context, note)

    def test_multi_page_context_accepted(self) -> None:
        request = _request(context_pages=(1, 2), original_page=2)
        context = (
            _page(original_page=1, text="Scarcity page."),
            _page(original_page=2),
        )
        note = self.generator.generate(self.document, request, context)
        self.assertEqual(set(note.source_pages), {1, 2})
        validate_generation(self.document, request, context, note)

    def test_provider_unexpected_exception_becomes_generation_error(self) -> None:
        class CrashProvider:
            def generate(self, document, request, context):
                raise ValueError("internal bug")

        gen = NoteGenerator(CrashProvider())  # type: ignore[arg-type]
        with self.assertRaises(GenerationError):
            gen.generate(self.document, self.request, self.context)


@unittest.skipUnless(
    os.environ.get("NOTEWEAVER_API_KEY") or os.environ.get("OPENAI_API_KEY"),
    "live provider tests require NOTEWEAVER_API_KEY or OPENAI_API_KEY",
)
class LiveProviderTests(unittest.TestCase):
    """Optional live-service tests; skipped when no API key is present."""

    def setUp(self) -> None:
        self.document = _doc()
        self.request = _request()
        self.context = (_page(),)
        self.generator = NoteGenerator(OpenAICompatibleProvider())

    def test_live_generation_returns_valid_draft(self) -> None:
        note = self.generator.generate(self.document, self.request, self.context)
        self.assertEqual(note.status, "draft")
        validate_generation(self.document, self.request, self.context, note)


class OpenAICompatibleUnitTests(unittest.TestCase):
    """Unit tests for the live provider that never hit the network."""

    def test_missing_key_raises_generation_error(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            # Ensure both key names are absent
            os.environ.pop("NOTEWEAVER_API_KEY", None)
            os.environ.pop("OPENAI_API_KEY", None)
            provider = OpenAICompatibleProvider()
            with self.assertRaises(GenerationError) as cm:
                provider.generate(_doc(), _request(), (_page(),))
            self.assertIn("API key", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
