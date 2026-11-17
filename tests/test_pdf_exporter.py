"""Exporter acceptance checks using real shared models and offline workflows."""

from dataclasses import replace
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from noteweaver import (
    ContractError, ExportResult, FakeNoteProvider, PyMuPDFPDFExporter,
    add_manual_note, approve_note, create_project, generate_note,
    load_project, save_project, validate_export,
)
from noteweaver.pdf_reader import PDFReader

HAS_EXPORT = importlib.util.find_spec("pymupdf") is not None
FIXTURE = Path(__file__).resolve().parents[1] / "examples/data/sample_lecture_3p.pdf"


@unittest.skipUnless(HAS_EXPORT, 'Install the export extra for PDF exporter tests')
class PDFExporterTests(unittest.TestCase):
    def setUp(self):
        import pymupdf
        self.pdf = pymupdf
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'lecture.pdf'
        self.source.write_bytes(FIXTURE.read_bytes())
        self.original_bytes = self.source.read_bytes()
        self.project = create_project(PDFReader().inspect(self.source), self.source)
        self.exporter = PyMuPDFPDFExporter()
        self.output = self.root / 'study.pdf'

    def note(self, project=None, *, page=2, title='Opportunity cost', content='Choose the next best alternative.', approve=True):
        project = add_manual_note(project or self.project, original_page=page,
                                  title=title, content=content, language='en')
        return approve_note(project, project.notes[-1].note_id) if approve else project

    def test_real_models_order_maps_original_pixels_and_draft_filter(self):
        project = self.note(content='FIRST_MARKER')
        project = self.note(project, content='SECOND_MARKER')
        project = self.note(project, page=1, content='DRAFT_MUST_NOT_APPEAR', approve=False)
        result = self.exporter.export(self.source, project, self.output)
        self.assertIsInstance(result, ExportResult)
        validate_export(project, result)
        self.assertEqual([p.output_page for p in result.original_to_output_pages], [1, 2, 5])
        self.assertEqual([p.output_pages for p in result.note_to_output_pages], [(3,), (4,)])
        with self.pdf.open(self.source) as original, self.pdf.open(self.output) as study:
            self.assertEqual(len(study), 5)
            self.assertIn('FIRST_MARKER', study[2].get_text())
            self.assertIn('SECOND_MARKER', study[3].get_text())
            self.assertNotIn('DRAFT_MUST_NOT_APPEAR', ''.join(p.get_text() for p in study))
            for i, location in enumerate(result.original_to_output_pages):
                self.assertEqual(original[i].get_pixmap().samples,
                                 study[location.output_page - 1].get_pixmap().samples)
            self.assertTrue(any(row[1].startswith('Note 1:') for row in study.get_toc()))
        self.assertEqual(self.source.read_bytes(), self.original_bytes)

    def test_no_notes_returns_valid_original_map(self):
        result = self.exporter.export(self.source, self.project, self.output)
        validate_export(self.project, result)
        self.assertEqual(result.output_page_count, 3)
        self.assertEqual(result.note_to_output_pages, ())

    def test_long_text_and_long_title_terminate_without_missing_or_duplicate_lines(self):
        lines = [f'UniqueLine{i:03d}: Every sentence must survive pagination.' for i in range(180)]
        project = self.note(content='\n'.join(lines), title='A long title with wrapped words ' * 14)
        result = self.exporter.export(self.source, project, self.output)
        locations = result.note_to_output_pages[0].output_pages
        self.assertGreater(len(locations), 2)
        self.assertLess(len(locations), 15)
        with self.pdf.open(self.output) as study:
            text = ''.join(study[i - 1].get_text() for i in locations)
            for line in lines:
                self.assertEqual(text.count(line), 1, line)
            for i in locations:
                page = study[i - 1]
                self.assertIn('Original page 2', page.get_text())
                for word in page.get_text('words'):
                    self.assertGreaterEqual(word[0], 53)
                    self.assertLessEqual(word[2], page.rect.width - 53)
                    self.assertGreaterEqual(word[1], 20)
                    self.assertLessEqual(word[3], page.rect.height - 15)

    def test_chinese_and_formula_source_round_trip(self):
        body = '免費講座仍然有機會成本。\n学习需要时间。\nFormula source: E = mc^2; \\frac{a}{b}; α + β = ∑x'
        project = self.note(title='機會成本筆記', content=body)
        result = self.exporter.export(self.source, project, self.output)
        with self.pdf.open(self.output) as study:
            text = ''.join(study[i-1].get_text() for i in result.note_to_output_pages[0].output_pages)
            for line in body.splitlines():
                self.assertIn(line, text)
            self.assertIn('機會成本筆記', text)
            self.assertNotIn('?', text)

    def test_fake_generation_editing_persistence_and_export(self):
        project = generate_note(self.project, original_page=2, question='Explain opportunity cost',
                                language='en', provider=FakeNoteProvider())
        self.assertEqual(project.notes[0].status, 'draft')
        project = approve_note(project, project.notes[0].note_id)
        save_project(project, self.root/'project.json')
        restored = load_project(self.root/'project.json')
        result = self.exporter.export(self.source, restored, self.output)
        validate_export(restored, result)
        with self.pdf.open(self.output) as study:
            text = ''.join(study[p-1].get_text() for p in result.note_to_output_pages[0].output_pages)
            self.assertIn('Lecture-based claim', text)
            self.assertIn('AI-added material', text)
            self.assertIn('Source pages:', text)
            for section in restored.notes[0].sections:
                compact = lambda s: ''.join(s.split())
                self.assertIn(compact(section.content), compact(text))

    def test_reject_wrong_source_and_page_count(self):
        for document in (replace(self.project.document, document_id='sha256:'+'0'*64),
                         replace(self.project.document, page_count=4)):
            with self.subTest(document=document), self.assertRaises(ContractError):
                self.exporter.export(self.source, replace(self.project, document=document), self.output)
            self.assertFalse(self.output.exists())

    def test_reject_same_path_symlink_and_hardlink(self):
        aliases = [self.source, self.root/'symlink.pdf', self.root/'hardlink.pdf']
        aliases[1].symlink_to(self.source)
        os.link(self.source, aliases[2])
        for output in aliases:
            with self.subTest(output=output), self.assertRaises(ValueError):
                self.exporter.export(self.source, self.project, output)
        self.assertEqual(self.source.read_bytes(), self.original_bytes)

    def test_never_overwrite_existing_or_dangling_destination(self):
        self.output.write_bytes(b'existing user data')
        with self.assertRaises(FileExistsError):
            self.exporter.export(self.source, self.project, self.output)
        self.assertEqual(self.output.read_bytes(), b'existing user data')
        self.output.unlink()
        self.output.symlink_to(self.root/'missing.pdf')
        with self.assertRaises(FileExistsError):
            self.exporter.export(self.source, self.project, self.output)

    def test_changed_source_during_render_is_rejected_and_temp_cleaned(self):
        from noteweaver.models import verify_source
        calls = 0
        def verify(project, path):
            nonlocal calls
            calls += 1
            if calls == 2:
                path.write_bytes(path.read_bytes() + b'\nchanged')
            verify_source(project, path)
        with patch('noteweaver.exporters.verify_source', side_effect=verify):
            with self.assertRaises(ContractError):
                self.exporter.export(self.source, self.note(), self.output)
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.root.glob('.noteweaver-*')), [])

    def test_publish_failure_preserves_destination_and_cleans_temp(self):
        def collision(temporary, output):
            output.write_bytes(b'created concurrently')
            raise FileExistsError('Destination created concurrently')
        with patch('noteweaver.exporters.os.link', side_effect=collision):
            with self.assertRaises(FileExistsError):
                self.exporter.export(self.source, self.note(), self.output)
        self.assertEqual(self.output.read_bytes(), b'created concurrently')
        self.assertEqual(list(self.root.glob('.noteweaver-*')), [])
        self.assertEqual(self.source.read_bytes(), self.original_bytes)

    def test_unsupported_glyph_raises_instead_of_substitution(self):
        with self.assertRaisesRegex(ValueError, 'U\\+1F642'):
            self.exporter.export(self.source, self.note(content='Unsupported glyph: 🙂'), self.output)
        self.assertFalse(self.output.exists())

    def test_existing_bookmarks_and_internal_links_follow_original_pages(self):
        with self.pdf.open(self.source) as doc:
            doc.set_toc([[1, 'Original chapter three', 3]])
            doc[0].insert_link({'kind': self.pdf.LINK_GOTO, 'from': self.pdf.Rect(20,20,100,40),
                                'page': 2, 'to': self.pdf.Point(0,0)})
            data = doc.tobytes()
        self.source.write_bytes(data)
        project = create_project(PDFReader().inspect(self.source), self.source)
        project = self.note(project)
        result = self.exporter.export(self.source, project, self.output)
        validate_export(project, result)
        with self.pdf.open(self.output) as doc:
            self.assertEqual(doc.get_toc()[0], [1, 'Original chapter three', 4])
            self.assertEqual(doc[0].get_links()[0]['page'], 3)


if __name__ == '__main__':
    unittest.main()
