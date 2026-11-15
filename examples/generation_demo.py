#!/usr/bin/env python3
"""Offline demo of Member 2 NoteGenerator with the shared three-page lecture PDF.

Run from the repository root after `pip install -e .`:

    python examples/generation_demo.py
"""

from __future__ import annotations

from pathlib import Path

from noteweaver import (
    FakeNoteProvider,
    NoteGenerator,
    NoteRequest,
)
from noteweaver.pdf_reader import PDFReader


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "examples" / "data" / "sample_lecture_3p.pdf"

    reader = PDFReader()
    document = reader.inspect(source)
    print(f"Document: {document.filename}  pages={document.page_count}")
    print(f"document_id: {document.document_id[:20]}...")

    # Read the target page (page 2: opportunity cost)
    page = reader.read_page(source, 2)
    print(f"\nPage 2 extraction_status={page.extraction_status}")
    print(f"Text preview: {page.text[:80].replace(chr(10), ' ')}...")

    request = NoteRequest(
        request_id="demo-request-001",
        document_id=document.document_id,
        original_page=2,
        question="機會成本是否只是實際花掉的金錢？",
        context_pages=(2,),
        selected_text="機會成本",
        language="zh-Hant",
        level="first-year",
        style="example",
    )

    generator = NoteGenerator(FakeNoteProvider())
    note = generator.generate(document, request, (page,))

    print("\n=== Generated draft note ===")
    print(f"note_id     : {note.note_id}")
    print(f"title       : {note.title}")
    print(f"status      : {note.status}")
    print(f"source_pages: {note.source_pages}")
    print(f"request_id  : {note.request_id}")
    print("sections:")
    for section in note.sections:
        print(f"  [{section.origin}/{section.kind}] {section.content[:90]}...")

    print("\nDemo finished. The note is a draft; Member 4 will attach it to a ProjectState.")


if __name__ == "__main__":
    main()
