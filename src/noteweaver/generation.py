"""NoteGenerator: turn lecture context + student question into a draft note.

This module implements the shared NoteGenerator protocol. It never reads or
writes PDFs; it only validates the supplied context against the request and
delegates content production to a replaceable NoteProvider.
"""

from __future__ import annotations

from noteweaver.models import (
    ContractError,
    DocumentInfo,
    GeneratedNote,
    NoteRequest,
    PageContent,
    validate_generation,
)
from noteweaver.providers.base import GenerationError, NoteProvider
from noteweaver.providers.fake import FakeNoteProvider


class NoteGenerator:
    """Concrete NoteGenerator that wraps a NoteProvider.

    By default uses FakeNoteProvider (offline, deterministic). Pass any object
    satisfying the NoteProvider protocol to switch to a live service.
    """

    def __init__(self, provider: NoteProvider | None = None) -> None:
        self._provider: NoteProvider = provider if provider is not None else FakeNoteProvider()

    def generate(
        self,
        document: DocumentInfo,
        request: NoteRequest,
        context: tuple[PageContent, ...],
    ) -> GeneratedNote:
        """Produce a draft GeneratedNote and run validate_generation.

        Raises:
            ContractError: context does not match request, pages not ok, or the
                resulting note violates shared contracts.
            GenerationError: the underlying provider failed (network, auth,
                malformed reply, forced failure, etc.).
        """
        # Early structural checks so we fail fast before calling the provider.
        # validate_generation will re-check after the note is built.
        if not isinstance(context, tuple):
            raise ContractError("context must be a tuple of PageContent")
        page_numbers = tuple(p.original_page for p in context)
        if set(page_numbers) != set(request.context_pages):
            raise ContractError(
                "actual context must match request.context_pages exactly"
            )
        for page in context:
            if page.extraction_status != "ok":
                raise ContractError("generation needs successfully extracted text")

        try:
            note = self._provider.generate(document, request, context)
        except GenerationError:
            raise
        except Exception as exc:  # noqa: BLE001 — isolate unexpected provider bugs
            raise GenerationError(f"provider failed unexpectedly: {type(exc).__name__}") from None

        # Enforce draft status and full shared validation before returning.
        if note.status != "draft":
            # Providers should already return draft; defend the contract.
            raise ContractError("new generated notes must be drafts")

        validate_generation(document, request, context, note)
        return note


def default_generator() -> NoteGenerator:
    """Convenience factory that returns an offline FakeNoteProvider generator."""
    return NoteGenerator(FakeNoteProvider())
