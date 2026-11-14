"""Module boundary signatures only; members implement these protocols."""

from pathlib import Path
from typing import Protocol

from .models import DocumentInfo, ExportResult, GeneratedNote, NoteRequest, PageContent, ProjectState


class PDFReader(Protocol):
    def inspect(self, source: Path) -> DocumentInfo:
        """Member 1: read page count and hash the source bytes."""
        ...

    def read_page(self, source: Path, original_page: int) -> PageContent:
        """Member 1: original_page is 1-based; preview_path is optional."""
        ...


class NoteGenerator(Protocol):
    def generate(self, document: DocumentInfo, request: NoteRequest,
                 context: tuple[PageContent, ...]) -> GeneratedNote:
        """Member 2: return a draft; run validate_generation before returning."""
        ...


class PDFExporter(Protocol):
    def export(self, source: Path, project: ProjectState, output: Path) -> ExportResult:
        """Member 3: verify source; new output path; approved notes only.

        Reject an output that resolves to the input source (including aliases).
        Validate placement with validate_export after rendering. This protocol
        itself does not inspect files, render pages, or enforce these operations.
        """
        ...
