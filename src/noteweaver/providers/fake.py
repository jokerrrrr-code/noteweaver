"""Deterministic offline provider for integration testing without network."""

from __future__ import annotations

from uuid import uuid4

from noteweaver.models import (
    DocumentInfo,
    GeneratedNote,
    NoteRequest,
    NoteSection,
    PageContent,
)

from .base import GenerationError, NoteProvider


class FakeNoteProvider:
    """Fixed-output provider that never calls the network.

    Suitable for teammate integration, CI, and demos. The content is
    intentionally simple and deterministic so other members can assert on
    structure without depending on a live model.
    """

    def __init__(self, *, fail: bool = False) -> None:
        """If fail is True, every generate call raises GenerationError."""
        self._fail = fail

    def generate(
        self,
        document: DocumentInfo,
        request: NoteRequest,
        context: tuple[PageContent, ...],
    ) -> GeneratedNote:
        if self._fail:
            raise GenerationError("fake provider forced failure (no network used)")

        # Use the first context page that matches the target for lecture origin.
        target_pages = [p for p in context if p.original_page == request.original_page]
        lecture_snippet = ""
        if target_pages and target_pages[0].text.strip():
            lecture_snippet = target_pages[0].text.strip().split("\n")[0][:120]
        else:
            lecture_snippet = "(no extractable lecture text on target page)"

        # Deterministic title and sections based on request fields.
        style = request.style
        lang = request.language
        question = request.question.strip()

        if lang.startswith("zh"):
            title = f"關於「{question[:40]}」的補充說明"
            explanation = (
                f"根據講義內容：「{lecture_snippet}」。"
                f"針對問題「{question}」，以下用{style}風格整理重點。"
            )
            example = (
                "舉例：假設你選擇參加一場免費講座，而最佳替代方案是用同樣時間溫習考試，"
                "那麼放棄的溫習價值仍屬於機會成本。"
            )
            quiz = "免費的選擇是否可能仍有機會成本？為什麼？"
            answer = "可能，因為時間與注意力仍是有限資源，放棄的替代方案價值仍需計算。"
        else:
            title = f"Notes on: {question[:50]}"
            explanation = (
                f"From the lecture: “{lecture_snippet}”. "
                f"Regarding “{question}”, key points in a {style} style follow."
            )
            example = (
                "Example: choosing a free event still forgoes the value of the "
                "best alternative use of that same hour of study time."
            )
            quiz = "Can a free choice still have an opportunity cost? Why?"
            answer = (
                "Yes, because time and attention remain scarce; the value of the "
                "forgone alternative still counts."
            )

        sections = (
            NoteSection(kind="explanation", content=explanation, origin="lecture"),
            NoteSection(kind="example", content=example, origin="ai"),
            NoteSection(kind="quiz", content=quiz, origin="ai"),
            NoteSection(kind="answer", content=answer, origin="ai"),
        )

        # source_pages limited to what was actually supplied in context
        source_pages = tuple(sorted({p.original_page for p in context}))

        return GeneratedNote(
            note_id=str(uuid4()),
            document_id=document.document_id,
            original_page=request.original_page,
            title=title,
            sections=sections,
            source_pages=source_pages,
            request_id=request.request_id,
            language=request.language,
            status="draft",
        )


# Satisfy the protocol for static checkers
_: NoteProvider = FakeNoteProvider()
