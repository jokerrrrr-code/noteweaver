"""Provider boundary for structured note generation."""

from __future__ import annotations

from typing import Protocol

from noteweaver.models import DocumentInfo, GeneratedNote, NoteRequest, PageContent


class GenerationError(RuntimeError):
    """Provider or generation failed; the note was not produced.

    Callers may retry with the same inputs. Credentials and raw provider
    payloads must not be attached to this exception message.
    """


class NoteProvider(Protocol):
    """Produce a draft GeneratedNote from document, request, and page context.

    Implementations must not mutate the source PDF, must not write credentials
    to disk, and must return only structured content. Validation against the
    shared contracts is the responsibility of the NoteGenerator wrapper.
    """

    def generate(
        self,
        document: DocumentInfo,
        request: NoteRequest,
        context: tuple[PageContent, ...],
    ) -> GeneratedNote:
        """Return a draft note. May raise GenerationError on service failure."""
        ...
