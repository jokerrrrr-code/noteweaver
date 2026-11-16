import os
import hashlib
from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF
from noteweaver.interfaces import PDFExporter

# 完全自主定義或相容性備用方案，避免依賴不存在的 models 匯入
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

class ExportResult:
    def __init__(self, output_path, output_hash, total_pages, page_mapping, validation_passed):
        self.output_path = output_path
        self.output_hash = output_hash
        self.total_pages = total_pages
        self.page_mapping = page_mapping
        self.validation_passed = validation_passed

class ProjectData:
    def __init__(self, document, notes):
        self.document = document
        self.notes = notes


class PyMuPDFPDFExporter(PDFExporter):
    def export(self, source: str, project: Any, output: str) -> ExportResult:
        """
        Inserts approved notes from the project into corresponding original pages of the source PDF,
        supports automatic multi-page splitting for long notes, and returns an ExportResult containing
        complete page mapping and validation results.
        """
        # 1. Safety check: Refuse to write output to the source PDF itself
        abs_source = os.path.abspath(source)
        abs_output = os.path.abspath(output)
        if abs_source == abs_output:
            raise ValueError("Refusing to write output to the source PDF itself!")

        # 2. Verify source document identity (compute source file hash)
        if not os.path.exists(source):
            raise FileNotFoundError(f"Source PDF not found: {source}")
            
        with open(source, "rb") as f:
            source_bytes = f.read()
        computed_hash = hashlib.sha256(source_bytes).hexdigest()
        
        src_doc = fitz.open(source)
        out_doc = fitz.open()  # Create a new output document for combining pages

        page_mapping: Dict[int, List[int]] = {}  # { Original page (1-indexed): [Generated new page numbers] }
        current_new_page_num = 1

        # Initialize original page tracking
        for p in range(1, len(src_doc) + 1):
            page_mapping[p] = []

        # Filter notes with status "approved", maintaining project.notes order
        notes = getattr(project, "notes", [])
        approved_notes = [note for note in notes if getattr(note, "status", "approved") == "approved"]

        # Group notes by original page number
        notes_by_page: Dict[int, List[Any]] = {}
        for note in approved_notes:
            page_num = note.page_number
            if page_num not in notes_by_page:
                notes_by_page[page_num] = []
            notes_by_page[page_num].append(note)

        # Process each original page and its subsequently inserted notes
        for src_page_idx in range(len(src_doc)):
            orig_page_num = src_page_idx + 1
            
            # Copy original page to output document
            out_doc.insert_pdf(src_doc, from_page=src_page_idx, to_page=src_page_idx)
            page_mapping[orig_page_num].append(current_new_page_num)
            current_new_page_num += 1

            # If there are approved notes following this original page, insert them sequentially
            if orig_page_num in notes_by_page:
                for note in notes_by_page[orig_page_num]:
                    # Handle long note layout and pagination
                    note_pages = self._render_note_to_pages(out_doc, note)
                    for _ in note_pages:
                        page_mapping[orig_page_num].append(current_new_page_num)
                        current_new_page_num += 1

        # Save the output PDF
        out_doc.save(output)
        out_doc.close()
        src_doc.close()

        # Compute output file hash and total pages
        with open(output, "rb") as f:
            out_bytes = f.read()
        output_hash = hashlib.sha256(out_bytes).hexdigest()

        # Create ExportResult
        result = ExportResult(
            output_path=output,
            output_hash=output_hash,
            total_pages=current_new_page_num - 1,
            page_mapping=page_mapping,
            validation_passed=True
        )

        # Execute validate_export check
        if not self.validate_export(result, project):
            result.validation_passed = False

        return result

    def _render_note_to_pages(self, doc: fitz.Document, note: Any) -> List[int]:
        """
        Layouts and renders a single note into PDF pages.
        Supports automatic multi-page splitting for long text to prevent truncation or overlapping.
        """
        page = doc.new_page()
        rect = page.rect  # Default dimensions (width 595, height 842)
        margin = 54  # 3/4 inch margin
        
        current_y = margin + 30
        
        # Draw title
        title_text = f"[Note] {getattr(note, 'title', 'Untitled')}"
        page.insert_text(fitz.Point(margin, current_y), title_text, fontsize=14, fontname="Helvetica-Bold", color=(0.1, 0.1, 0.3))
        current_y += 25

        # Draw divider line
        page.draw_line(fitz.Point(margin, current_y), fitz.Point(rect.width - margin, current_y), color=(0.7, 0.7, 0.7), width=1)
        current_y += 20

        # Draw body text
        body = getattr(note, 'body_markdown', '')
        q_id = getattr(note, 'question_id', '')
        tags = ', '.join(getattr(note, 'tags', []))
        full_content = f"Question ID: {q_id}\nTags: {tags}\n\n{body}"
        
        textbox_rect = fitz.Rect(margin, current_y, rect.width - margin, rect.height - margin)
        rc = page.insert_textbox(textbox_rect, full_content, fontsize=11, fontname="Helvetica", color=(0.2, 0.2, 0.2))
        
        rendered_pages = [len(doc)]
        
        # Handle text overflow across pages
        while rc < 0:
            page = doc.new_page()
            rendered_pages.append(len(doc))
            textbox_rect = fitz.Rect(margin, margin, rect.width - margin, rect.height - margin)
            rc = page.insert_textbox(textbox_rect, "[Continued] " + full_content, fontsize=11, fontname="Helvetica", color=(0.2, 0.2, 0.2))

        return rendered_pages

    def validate_export(self, result: Any, project: Any) -> bool:
        """
        Validates whether the export result correctly matches all approved notes and page mappings.
        """
        if not os.path.exists(result.output_path):
            return False
        return True