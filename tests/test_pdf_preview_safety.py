"""Regression checks for source preservation and truthful preview failures."""
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import warnings
from unittest.mock import patch

import pypdf
import pypdfium2

from noteweaver import ContractError
from noteweaver.pdf_reader import PDFReader, PreviewError, PreviewWarning

SAMPLE = Path(__file__).resolve().parents[1] / "examples/data/sample_lecture_3p.pdf"


class PreviewSafetyTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / "lecture.pdf"
        shutil.copyfile(SAMPLE, self.source)
        self.original = self.source.read_bytes()
        self.reader = PDFReader(preview_dir=self.root / "cache")

    def assert_source_unchanged(self):
        self.assertEqual(self.source.read_bytes(), self.original)
        self.assertEqual(len(pypdf.PdfReader(self.source).pages), 3)

    def test_direct_and_normalized_source_destinations_are_rejected(self):
        for destination in (self.source, self.root / "unused/../lecture.pdf"):
            with self.subTest(destination=destination), self.assertRaises(ContractError):
                self.reader.preview_page(self.source, 2, output_path=destination)
            self.assert_source_unchanged()

    def test_symbolic_and_hard_link_source_aliases_are_rejected(self):
        for link_type in ("symlink", "hardlink"):
            alias = self.root / f"{link_type}.png"
            if link_type == "symlink":
                alias.symlink_to(self.source)
            else:
                alias.hardlink_to(self.source)
            with self.subTest(link_type=link_type), self.assertRaises(ContractError):
                self.reader.preview_page(self.source, 2, output_path=alias)
            self.assert_source_unchanged()

    def test_cache_aliases_are_rejected_by_both_apis(self):
        document = self.reader.inspect(self.source)
        name = document.document_id.removeprefix("sha256:")[:16] + "_page_2.png"
        cache = self.root / "cache"
        cache.mkdir()
        destination = cache / name
        for link_type in ("symlink", "hardlink"):
            if link_type == "symlink":
                destination.symlink_to(self.source)
            else:
                destination.hardlink_to(self.source)
            for method in (self.reader.read_page, self.reader.preview_page):
                with self.subTest(link_type=link_type, method=method.__name__):
                    with self.assertRaises(ContractError):
                        method(self.source, 2)
                    self.assert_source_unchanged()
            destination.unlink()

    def test_missing_renderer_preserves_text_and_creates_no_image(self):
        with patch.dict(sys.modules, {"pypdfium2": None}):
            with self.assertWarnsRegex(PreviewWarning, "preview dependencies"):
                page = self.reader.read_page(self.source, 2)
            self.assertEqual(page.extraction_status, "ok")
            self.assertIsNone(page.error_message)
            self.assertIsNone(page.preview_path)
            self.assertIn("機會成本", page.text)
            with self.assertRaisesRegex(PreviewError, "preview dependencies"):
                self.reader.preview_page(self.source, 2)
        self.assertFalse((self.root / "cache").exists())
        self.assert_source_unchanged()

    def test_text_only_read_needs_no_renderer_and_emits_no_warning(self):
        with patch.dict(sys.modules, {"pypdfium2": None}), warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            page = self.reader.read_page(self.source, 2, render_preview=False)
        self.assertEqual(caught, [])
        self.assertIsNone(page.preview_path)
        self.assertIn("Opportunity cost", page.text)

    def test_missing_pillow_does_not_create_a_substitute_image(self):
        with patch.object(pypdfium2.PdfBitmap, "to_pil", side_effect=ImportError("Pillow absent")):
            with self.assertRaisesRegex(PreviewError, "preview dependencies"):
                self.reader.preview_page(self.source, 2)
        self.assertFalse((self.root / "cache").exists())

    def test_renderer_failure_does_not_return_a_stale_cached_preview(self):
        preview = self.reader.preview_page(self.source, 2)
        cached = Path(preview.preview_path)
        before = cached.read_bytes()
        with patch.object(pypdfium2, "PdfDocument", side_effect=RuntimeError("secret renderer detail")):
            with self.assertWarns(PreviewWarning) as warning:
                page = self.reader.read_page(self.source, 2)
            self.assertNotIn("secret renderer detail", str(warning.warning))
            self.assertIsNone(page.preview_path)
            self.assertEqual(page.extraction_status, "ok")
            with self.assertRaises(PreviewError):
                self.reader.preview_page(self.source, 2)
        self.assertEqual(cached.read_bytes(), before)
        self.assert_source_unchanged()

    def test_write_failure_preserves_existing_preview_and_cleans_temporary_file(self):
        preview = self.reader.preview_page(self.source, 2)
        cached = Path(preview.preview_path)
        before = cached.read_bytes()
        with patch("noteweaver.pdf_reader.os.replace", side_effect=PermissionError("private detail")):
            with self.assertWarns(PreviewWarning) as warning:
                page = self.reader.read_page(self.source, 2)
            self.assertNotIn("private detail", str(warning.warning))
            self.assertIsNone(page.preview_path)
            with self.assertRaises(PermissionError):
                self.reader.preview_page(self.source, 2)
        self.assertEqual(cached.read_bytes(), before)
        self.assertEqual(list(cached.parent.glob(".noteweaver-preview-*.tmp")), [])
        self.assert_source_unchanged()

    def test_preview_failure_does_not_replace_extraction_error(self):
        with patch.object(pypdf.PageObject, "extract_text", side_effect=ValueError("bad text")):
            with patch.dict(sys.modules, {"pypdfium2": None}), self.assertWarns(PreviewWarning):
                page = self.reader.read_page(self.source, 2)
        self.assertEqual(page.extraction_status, "error")
        self.assertIn("text extraction failed", page.error_message)
        self.assertIsNone(page.preview_path)

    def test_nonfinite_and_invalid_scales_are_rejected(self):
        for scale in (float("nan"), float("inf"), -float("inf"), 0, -1, True, "2"):
            with self.subTest(scale=scale):
                with self.assertRaises(ContractError):
                    PDFReader(preview_scale=scale)
                with self.assertRaises(ContractError):
                    self.reader.preview_page(self.source, 2, scale=scale)

    def test_sample_has_embedded_truetype_font_and_unicode_mapping_on_each_page(self):
        for page in pypdf.PdfReader(SAMPLE).pages:
            embedded = []
            for reference in page["/Resources"]["/Font"].values():
                font = reference.get_object()
                descriptor = font.get("/FontDescriptor")
                if descriptor and "/FontFile2" in descriptor.get_object():
                    embedded.append(font)
            self.assertTrue(embedded, "The bilingual fixture must embed its glyphs")
            self.assertTrue(all("/ToUnicode" in font for font in embedded))
            self.assertTrue(any(ord(character) > 0x3000 for character in page.extract_text()))


if __name__ == "__main__":
    unittest.main()
