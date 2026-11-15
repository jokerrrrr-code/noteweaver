"""Public orchestration connecting PDF input, generation, and project state."""
from dataclasses import replace
from pathlib import Path
from uuid import uuid4

from .generation import NoteGenerator
from .models import ContractError, ExplanationStyle, NoteRequest, ProjectState, verify_source
from .pdf_reader import PDFReader
from .providers.base import NoteProvider


def generate_note(
    project: ProjectState, *, original_page: int, question: str, provider: NoteProvider,
    language: str = "en", style: ExplanationStyle = "simple", level: str = "first-year",
    selected_text: str | None = None, context_pages: tuple[int, ...] | None = None,
) -> ProjectState:
    """Generate and append one draft, returning a new project only on success.

    Requires an absolute source path (as returned by load_project). Only requested
    context pages are read and sent; the default is the target page alone. This
    function does not render a preview, approve notes, save files, or export PDFs.
    Pass GroqProvider for live generation or an explicitly chosen fake for tests.
    """
    if type(project) is not ProjectState:
        raise ContractError("project must be a ProjectState")
    source = Path(project.source_path)
    if not source.is_absolute():
        raise ContractError("generation needs an absolute source path; use load_project or source.resolve()")
    verify_source(project, source)
    reader = PDFReader(render_preview=False)
    actual = reader.inspect(source)
    if (actual.document_id, actual.page_count) != (project.document.document_id, project.document.page_count):
        raise ContractError("project document metadata does not match the source PDF")
    request = NoteRequest(
        request_id=str(uuid4()), document_id=project.document.document_id,
        original_page=original_page, question=question,
        context_pages=(original_page,) if context_pages is None else context_pages,
        selected_text=selected_text, language=language, style=style, level=level,
    )
    context = reader.read_pages(source, request.context_pages, render_preview=False)
    verify_source(project, source)
    note = NoteGenerator(provider).generate(project.document, request, context)
    verify_source(project, source)
    return replace(project, requests=project.requests + (request,), notes=project.notes + (note,))
