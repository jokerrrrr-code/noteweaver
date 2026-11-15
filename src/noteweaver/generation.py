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
    validate_page,
    validate_request,
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
        # Validate the full input boundary before a provider can send any text.
        if type(document) is not DocumentInfo or type(request) is not NoteRequest:
            raise ContractError("document and request must use the shared model types")
        validate_request(document, request)
        if type(context) is not tuple or any(type(page) is not PageContent for page in context):
            raise ContractError("context must be a tuple of PageContent")
        for page in context:
            validate_page(document, page)
            if page.extraction_status != "ok":
                raise ContractError("generation needs successfully extracted text")
        page_numbers = tuple(page.original_page for page in context)
        if len(set(page_numbers)) != len(page_numbers):
            raise ContractError("context must not contain duplicate pages")
        if set(page_numbers) != set(request.context_pages):
            raise ContractError("actual context must match request.context_pages exactly")

        try:
            note = self._provider.generate(document, request, context)
        except GenerationError:
            raise
        except Exception as exc:  # noqa: BLE001 — isolate unexpected provider bugs
            raise GenerationError(f"provider failed unexpectedly: {type(exc).__name__}") from None

        # Enforce draft status and full shared validation before returning.
        if type(note) is not GeneratedNote:
            raise GenerationError("provider must return a GeneratedNote")
        if note.status != "draft":
            # Providers should already return draft; defend the contract.
            raise ContractError("new generated notes must be drafts")

        validate_generation(document, request, context, note)
        return note


def default_generator() -> NoteGenerator:
    """Convenience factory that returns an offline FakeNoteProvider generator."""
    return NoteGenerator(FakeNoteProvider())
