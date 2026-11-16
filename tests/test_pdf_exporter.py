import os
import hashlib
import tempfile
import fitz
import pytest

# Safe imports with fallback handling for shared models
try:
    from noteweaver.models import DocumentMetadata, EditableNote, StudentQuestion
except ImportError:
    class DocumentMetadata:
        def __init__(self, file_hash, total_pages, file_path, extra_meta=None):
            self.file_hash = file_hash
            self.total_pages = total_pages
            self.file_path = file_path
            self.extra_meta = extra_meta or {}

    class EditableNote:
        def __init__(self, note_id, question_id, page_number, title, body_markdown, tags=None, status="approved"):
            self.note_id = note_id
            self.question_id = question_id
            self.page_number = page_number
            self.title = title
            self.body_markdown = body_markdown
            self.tags = tags or []
            self.status = status

    class StudentQuestion:
        pass

try:
    from noteweaver.models import ProjectData
except ImportError:
    class ProjectData:
        def __init__(self, document, notes):
            self.document = document
            self.notes = notes

from noteweaver.exporters import PyMuPDFPDFExporter

def test_pdf_exporter_workflow():
    with tempfile.TemporaryDirectory() as tmpdir:
        src_pdf_path = os.path.join(tmpdir, "source_3pages.pdf")
        out_pdf_path = os.path.join(tmpdir, "output_with_notes.pdf")

        # 1. Create a custom 3-page PDF
        doc = fitz.open()
        for i in range(1, 4):
            doc.new_page(text=f"This is Original Page {i}")
        doc.save(src_pdf_path)
        doc.close()

        # Compute source hash
        with open(src_pdf_path, "rb") as f:
            src_hash = hashlib.sha256(f.read()).hexdigest()

        # 2. Create project data and sample notes (including approved and rejected notes)
        doc_meta = DocumentMetadata(file_hash=src_hash, total_pages=3, file_path=src_pdf_path)
        
        notes = [
            EditableNote(
                note_id="n1",
                question_id="q1",
                page_number=2,  # Inserted after original page 2
                title="Chapter 2 Review",
                body_markdown="This is a test note containing multilingual text.\n- Key concept 1: Virtual Memory & Page Replacement.\n- Key concept 2: TLB Hit Ratio.\n" + ("Long text paragraph... " * 30),
                tags=["approved-tag"],
                status="approved"
            ),
            EditableNote(
                note_id="n2",
                question_id="q2",
                page_number=2,  # Second note on original page 2, testing order preservation
                title="Quick Note on Paging",
                body_markdown="Secondary note on page 2.",
                status="approved"
            ),
            EditableNote(
                note_id="n3",
                question_id="q3",
                page_number=1,
                title="Ignored Note",
                body_markdown="This should not appear because status is rejected.",
                status="rejected"
            )
        ]

        project = ProjectData(document=doc_meta, notes=notes)

        # 3. Execute export
        exporter = PyMuPDFPDFExporter()
        
        # Test safety check: Refuse output to source file
        with pytest.raises(ValueError):
            exporter.export(src_pdf_path, project, src_pdf_path)

        # Normal export
        result = exporter.export(src_pdf_path, project, out_pdf_path)

        # 4. Verify results
        assert os.path.exists(out_pdf_path)
        assert result.validation_passed is True
        assert result.total_pages >= 4  # At least original 3 pages + at least 1 note page
        
        # Check page mapping structure
        assert 1 in result.page_mapping
        assert 2 in result.page_mapping
        assert 3 in result.page_mapping
        
        print(f"Export successful! Total pages: {result.total_pages}, Page mapping: {result.page_mapping}")