from dataclasses import replace
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import pypdf

from noteweaver import (
    ContractError,
    DocumentInfo,
    PageContent,
    add_manual_note,
    create_project,
    document_id_for_file,
    load_project,
    save_project,
    validate_page,
    verify_source,
)
from noteweaver.pdf_reader import (
    PDFReader,
    PagePreview,
    inspect_pdf,
    preview_pdf_page,
    read_pdf_page,
)

SAMPLE_PDF = Path(__file__).resolve().parents[1] / "examples" / "data" / "sample_lecture_3p.pdf"


class PDFReaderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="noteweaver-pdf-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.preview_dir = self.root / "previews"
        self.reader = PDFReader(preview_dir=self.preview_dir)

    def test_inspect_three_page_pdf_and_preserve_source_bytes(self) -> None:
        before_bytes = SAMPLE_PDF.read_bytes()
        doc = self.reader.inspect(SAMPLE_PDF)
        self.assertIsInstance(doc, DocumentInfo)
        self.assertEqual(doc.filename, "sample_lecture_3p.pdf")
        self.assertEqual(doc.page_count, 3)
        self.assertEqual(doc.document_id, document_id_for_file(SAMPLE_PDF))
        self.assertEqual(inspect_pdf(SAMPLE_PDF), doc)
        self.assertEqual(SAMPLE_PDF.read_bytes(), before_bytes)

        renamed = self.root / "renamed_lecture.pdf"
        shutil.copyfile(SAMPLE_PDF, renamed)
        renamed_doc = self.reader.inspect(renamed)
        self.assertEqual(renamed_doc.document_id, doc.document_id)
        self.assertEqual(renamed_doc.filename, "renamed_lecture.pdf")
        self.assertEqual(renamed_doc.page_count, 3)

    def test_read_page_2_extracts_chinese_and_english_text_and_preview(self) -> None:
        doc = self.reader.inspect(SAMPLE_PDF)
        page2 = self.reader.read_page(SAMPLE_PDF, 2)
        validate_page(doc, page2)

        self.assertIsInstance(page2, PageContent)
        self.assertEqual(page2.document_id, doc.document_id)
        self.assertEqual(page2.original_page, 2)
        self.assertEqual(page2.extraction_status, "ok")
        self.assertIsNone(page2.error_message)
        self.assertIn("機會成本是為某個選擇而放棄的最佳替代方案價值。", page2.text)
        self.assertIn("Opportunity cost is the value of the next-best alternative forgone.", page2.text)

        self.assertIsNotNone(page2.preview_path)
        preview_file = Path(page2.preview_path)
        self.assertTrue(preview_file.is_file())
        self.assertEqual(preview_file.parent, self.preview_dir.resolve())
        self.assertTrue(preview_file.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))

    def test_read_pages_1_and_3_and_disable_preview(self) -> None:
        doc = self.reader.inspect(SAMPLE_PDF)
        page1 = self.reader.read_page(SAMPLE_PDF, 1, render_preview=False)
        page3 = read_pdf_page(SAMPLE_PDF, 3, render_preview=False)

        validate_page(doc, page1)
        validate_page(doc, page3)
        self.assertEqual(page1.original_page, 1)
        self.assertEqual(page1.extraction_status, "ok")
        self.assertIsNone(page1.preview_path)
        self.assertIn("稀少性與資源分配", page1.text)
        self.assertIn("Scarcity and Resource Allocation", page1.text)

        self.assertEqual(page3.original_page, 3)
        self.assertEqual(page3.extraction_status, "ok")
        self.assertIsNone(page3.preview_path)
        self.assertIn("邊際分析與課堂思考題", page3.text)
        self.assertIn("Marginal Analysis and Review", page3.text)

    def test_out_of_range_and_non_integer_pages_raise_contract_error(self) -> None:
        for invalid_page in (0, 4, -1, 99, True, False, 2.0, "2", None):
            with self.subTest(invalid_page=invalid_page), self.assertRaises(ContractError):
                self.reader.read_page(SAMPLE_PDF, invalid_page)  # type: ignore[arg-type]
            with self.subTest(preview_invalid_page=invalid_page), self.assertRaises(ContractError):
                self.reader.preview_page(SAMPLE_PDF, invalid_page)  # type: ignore[arg-type]

    def test_missing_file_directory_and_invalid_source_paths(self) -> None:
        missing = self.root / "does_not_exist.pdf"
        with self.assertRaises(FileNotFoundError):
            self.reader.inspect(missing)
        with self.assertRaises(FileNotFoundError):
            self.reader.read_page(missing, 1)

        with self.assertRaises(IsADirectoryError):
            self.reader.inspect(self.root)
        with self.assertRaises(IsADirectoryError):
            self.reader.read_page(self.root, 1)

        for bad_source in ("", "   ", "bad\0path.pdf", None, 123):
            with self.subTest(bad_source=bad_source):
                with self.assertRaises(ContractError):
                    self.reader.inspect(bad_source)  # type: ignore[arg-type]
                with self.assertRaises(ContractError):
                    self.reader.read_page(bad_source, 1)  # type: ignore[arg-type]

    def test_corrupted_empty_and_encrypted_pdf_files_raise_contract_error(self) -> None:
        corrupted = self.root / "corrupted.pdf"
        corrupted.write_bytes(b"This is not a valid PDF file")
        with self.assertRaises(ContractError):
            self.reader.inspect(corrupted)

        zero_byte = self.root / "empty.pdf"
        zero_byte.write_bytes(b"")
        with self.assertRaises(ContractError):
            self.reader.inspect(zero_byte)

        encrypted = self.root / "encrypted.pdf"
        writer = pypdf.PdfWriter()
        writer.add_blank_page(width=595, height=842)
        writer.encrypt("secret-password")
        with encrypted.open("wb") as stream:
            writer.write(stream)
        with self.assertRaisesRegex(ContractError, "encrypted"):
            self.reader.inspect(encrypted)

    def test_blank_page_returns_empty_extraction_status(self) -> None:
        mixed_pdf = self.root / "with_blank_page.pdf"
        source_reader = pypdf.PdfReader(str(SAMPLE_PDF))
        writer = pypdf.PdfWriter()
        writer.add_page(source_reader.pages[0])
        writer.add_blank_page(width=595, height=842)
        writer.add_page(source_reader.pages[1])
        with mixed_pdf.open("wb") as stream:
            writer.write(stream)

        doc = self.reader.inspect(mixed_pdf)
        self.assertEqual(doc.page_count, 3)

        blank_page = self.reader.read_page(mixed_pdf, 2)
        validate_page(doc, blank_page)
        self.assertEqual(blank_page.original_page, 2)
        self.assertEqual(blank_page.extraction_status, "empty")
        self.assertEqual(blank_page.text, "")
        self.assertIsNone(blank_page.error_message)
        self.assertIsNotNone(blank_page.preview_path)
        self.assertTrue(Path(blank_page.preview_path).is_file())

    def test_failed_page_extraction_returns_error_status_with_sanitized_message(self) -> None:
        doc = self.reader.inspect(SAMPLE_PDF)
        with patch.object(
            pypdf.PageObject,
            "extract_text",
            side_effect=RuntimeError("Font cmap decode failed; api_key=sk-secret-12345"),
        ):
            failed_page = self.reader.read_page(SAMPLE_PDF, 2, render_preview=False)

        validate_page(doc, failed_page)
        self.assertEqual(failed_page.original_page, 2)
        self.assertEqual(failed_page.extraction_status, "error")
        self.assertEqual(failed_page.text, "")
        self.assertIsNotNone(failed_page.error_message)
        self.assertIn("Page 2 text extraction failed", failed_page.error_message or "")
        self.assertNotIn("sk-secret-12345", failed_page.error_message or "")
        self.assertIn("[REDACTED]", failed_page.error_message or "")

    def test_notebook_preview_object_supports_repr_png_and_escaped_repr_html(self) -> None:
        custom_out = self.root / "custom_preview" / "page2.png"
        preview = preview_pdf_page(SAMPLE_PDF, 2, output_path=custom_out)
        self.assertIsInstance(preview, PagePreview)
        self.assertEqual(preview.page.original_page, 2)
        self.assertEqual(Path(preview.preview_path), custom_out.resolve())
        self.assertTrue(custom_out.is_file())
        self.assertTrue(preview._repr_png_().startswith(b"\x89PNG\r\n\x1a\n"))

        html_output = preview._repr_html_()
        self.assertIn("data:image/png;base64,", html_output)
        self.assertIn("Original Page 2 of 3", html_output)
        self.assertIn("機會成本", html_output)

        untrusted_page = replace(preview.page, text="<script>alert('xss')</script>")
        untrusted_preview = replace(preview, page=untrusted_page)
        self.assertNotIn("<script>", untrusted_preview._repr_html_())
        self.assertIn("&lt;script&gt;", untrusted_preview._repr_html_())

    def test_read_pages_and_neighboring_pages_for_member2_context(self) -> None:
        pages = self.reader.read_pages(SAMPLE_PDF, (1, 2), render_preview=False)
        self.assertEqual([p.original_page for p in pages], [1, 2])

        with self.assertRaises(ContractError):
            self.reader.read_pages(SAMPLE_PDF, (2, 2))
        with self.assertRaises(ContractError):
            self.reader.read_pages(SAMPLE_PDF, ())

        neighbors_mid = self.reader.read_neighboring_pages(SAMPLE_PDF, 2, radius=1, render_preview=False)
        self.assertEqual([p.original_page for p in neighbors_mid], [1, 2, 3])

        neighbors_start = self.reader.read_neighboring_pages(SAMPLE_PDF, 1, radius=1, render_preview=False)
        self.assertEqual([p.original_page for p in neighbors_start], [1, 2])

    def test_integration_with_member4_project_and_persistence(self) -> None:
        doc = self.reader.inspect(SAMPLE_PDF)
        project = create_project(doc, SAMPLE_PDF)
        project = add_manual_note(
            project,
            original_page=2,
            title="機會成本重點整理",
            content="機會成本包含時間與隱性價值。",
        )
        json_path = save_project(project, self.root / "study.json")
        reloaded = load_project(json_path)
        verify_source(reloaded, SAMPLE_PDF)
        self.assertEqual(reloaded.document, doc)


if __name__ == "__main__":
    unittest.main()
