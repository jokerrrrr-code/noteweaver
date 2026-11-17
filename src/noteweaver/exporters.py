"""Approved-note PDF export using the team's shared data contracts."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import tempfile
from typing import Iterator

from .models import (
    ContractError, ExportResult, GeneratedNote, NotePageLocation,
    OriginalPageLocation, ProjectState, validate_export, verify_source,
)


class PyMuPDFPDFExporter:
    """Render plain-text English/Chinese notes to a new, verified study PDF.

    Install the ``export`` extra. Existing destinations are never overwritten.
    Missing font glyphs are errors rather than silent substitutions.
    """

    def __init__(self) -> None:
        try:
            import pymupdf
        except ImportError as exc:
            raise ImportError(
                'PDF export requires PyMuPDF; install this checkout with '
                'python -m pip install -e ".[export]"'
            ) from exc
        self._pdf = pymupdf
        # MuPDF's bundled Droid Sans Fallback covers Latin and CJK characters.
        # The font is embedded in output; no system font or network lookup occurs.
        self._font = pymupdf.Font("cjk")

    @staticmethod
    def _check_destination(source: Path, output: Path) -> None:
        if source.resolve() == output.resolve() or (
            output.exists() and os.path.samefile(source, output)
        ):
            raise ValueError("Output must not identify the source PDF, including aliases")
        if output.exists() or output.is_symlink():
            raise FileExistsError(f"Output already exists: {output}")

    def export(self, source: Path, project: ProjectState, output: Path) -> ExportResult:
        """Export approved notes in project order and return validated page maps.

        Source bytes are verified before reading and before publication. Build
        privately beside the destination and publish without replacing a file.
        """
        if not isinstance(project, ProjectState):
            raise TypeError("project must be a shared ProjectState")
        source, output = Path(source).absolute(), Path(output).absolute()
        self._check_destination(source, output)
        verify_source(project, source)
        source_bytes = source.read_bytes()
        if "sha256:" + hashlib.sha256(source_bytes).hexdigest() != project.document.document_id:
            raise ContractError("Source document changed while reading")

        temporary: Path | None = None
        try:
            with self._pdf.open(stream=source_bytes, filetype="pdf") as doc:
                if doc.needs_pass:
                    raise ValueError("Password-protected PDFs are not supported for export")
                if len(doc) != project.document.page_count:
                    raise ContractError("Source PDF page count does not match project metadata")
                # Edit a memory copy of the entire document, preserving original
                # pages, annotations and links rather than copying isolated pages.
                old_toc = doc.get_toc(simple=False)
                old_links = [page.get_links() for page in doc]
                original_locations = []
                note_locations = []
                notes_by_page: dict[int, list[GeneratedNote]] = {}
                for note in project.notes:
                    if note.status == "approved":
                        notes_by_page.setdefault(note.original_page, []).append(note)
                cursor = 0
                for original_page in range(1, project.document.page_count + 1):
                    original_locations.append(OriginalPageLocation(original_page, cursor + 1))
                    cursor += 1
                    for ordinal, note in enumerate(notes_by_page.get(original_page, []), 1):
                        pages = self._render_note(doc, note, cursor, ordinal)
                        note_locations.append(NotePageLocation(note.note_id, pages))
                        cursor += len(pages)
                result = ExportResult(
                    document_id=project.document.document_id,
                    output_path=str(output), output_page_count=len(doc),
                    original_to_output_pages=tuple(original_locations),
                    note_to_output_pages=tuple(note_locations),
                )
                validate_export(project, result)
                self._navigation(doc, old_toc, old_links, result, notes_by_page)
                with tempfile.NamedTemporaryFile(
                    dir=output.parent, prefix=".noteweaver-", suffix=".pdf", delete=False,
                ) as handle:
                    temporary = Path(handle.name)
                doc.save(temporary, garbage=3, deflate=True)
            with self._pdf.open(temporary) as saved:
                if len(saved) != result.output_page_count:
                    raise ContractError("Saved PDF page count differs from export map")
            verify_source(project, source)
            self._check_destination(source, output)
            # Atomic no-clobber publication on the destination filesystem.
            os.link(temporary, output)
            return result
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def _lines(self, text: str, size: float, width: float) -> Iterator[str]:
        """Wrap by measured glyph advances, always consuming source characters."""
        text = text.replace("\r\n", "\n").replace("\r", "\n").expandtabs(4)
        for char in set(text) - {"\n"}:
            if not self._font.has_glyph(ord(char)):
                raise ValueError(f"Export font cannot render U+{ord(char):04X}; edit the text first")
        for paragraph in text.split("\n"):
            if not paragraph:
                yield ""
                continue
            advances = self._font.char_lengths(paragraph, fontsize=size)
            start = 0
            while start < len(paragraph):
                end, used, last_space = start, 0.0, -1
                while end < len(paragraph) and used + advances[end] <= width:
                    used += advances[end]
                    if paragraph[end] == " ":
                        last_space = end
                    end += 1
                if end == start:
                    raise ValueError("A text glyph is wider than the available note area")
                if end < len(paragraph) and last_space > start:
                    end = last_space + 1
                yield paragraph[start:end]
                start = end

    def _render_note(self, doc, note: GeneratedNote, index: int, ordinal: int) -> tuple[int, ...]:
        width, height, margin = 595, 842, 54
        body_top, body_bottom = 100, height - 64
        pages: list[int] = []
        page = None
        y = body_top

        def draw(text: str, x: float, baseline: float, size: float, color) -> None:
            writer = self._pdf.TextWriter(page.rect)
            writer.append((x, baseline), text, font=self._font, fontsize=size)
            writer.write_text(page, color=color)

        def new_page() -> None:
            nonlocal page, y
            page = doc.new_page(pno=index + len(pages), width=width, height=height)
            pages.append(index + len(pages) + 1)
            draw(f"Original page {note.original_page} | Supplementary note {ordinal}",
                 margin, 48, 10, (0.25, 0.3, 0.4))
            page.draw_line((margin, 65), (width - margin, 65), color=(0.75, 0.78, 0.82))
            draw(f"Note page {len(pages)} | Output page {pages[-1]}",
                 margin, height - 30, 9, (0.35, 0.4, 0.45))
            y = body_top

        def block(text: str, size: float, color=(0.12, 0.15, 0.2)) -> None:
            nonlocal y
            leading = max(size * 1.5, size * (self._font.ascender - self._font.descender) + 2)
            for line in self._lines(text, size, width - 2 * margin):
                if page is None or y - self._font.descender * size > body_bottom:
                    new_page()
                if line:
                    draw(line, margin, y, size, color)
                y += leading
            y += 7

        block(note.title, 17, (0.1, 0.18, 0.32))
        if note.source_pages:
            block("Source pages: " + ", ".join(map(str, note.source_pages)) +
                  " (source claims, not fact checking)", 9)
        for section in note.sections:
            origin = {"lecture": "Lecture-based claim", "ai": "AI-added material", "user": "User-written"}[section.origin]
            block(f"{section.kind.replace('_', ' ').title()} | {origin}", 10, (0.22, 0.35, 0.5))
            block(section.content, 11)
        return tuple(pages)

    def _navigation(self, doc, old_toc, old_links, result, notes_by_page) -> None:
        locations = {item.original_page: item.output_page for item in result.original_to_output_pages}
        note_pages = {item.note_id: item.output_pages for item in result.note_to_output_pages}
        for original, links in enumerate(old_links, 1):
            page = doc[locations[original] - 1]
            for link in links:
                if link.get("kind") == self._pdf.LINK_GOTO and link.get("page", -1) >= 0:
                    link["page"] = locations[link["page"] + 1] - 1
                    page.update_link(link)
        for item in old_toc:
            destination = item[3]
            if destination.get("kind") == self._pdf.LINK_GOTO and destination.get("page", -1) >= 0:
                destination["page"] = locations[destination["page"] + 1] - 1
                item[2] = destination["page"] + 1
        toc = old_toc + [[1, "NoteWeaver study navigation", 1]]
        for original, output in locations.items():
            toc.append([2, f"Original page {original}", output])
            for ordinal, note in enumerate(notes_by_page.get(original, []), 1):
                toc.append([3, f"Note {ordinal}: {note.title}", note_pages[note.note_id][0]])
        doc.set_toc(toc)
