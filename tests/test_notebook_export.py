"""Exercise the real export cells to protect notebook review and replay behavior."""

from contextlib import redirect_stdout
from dataclasses import replace
import importlib.util
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from noteweaver import (
    ContractError, PyMuPDFPDFExporter, add_manual_note, approve_note,
    create_project, load_project, save_project, update_note,
)
from noteweaver.pdf_reader import PDFReader

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ('manual_workflow_demo.ipynb', 'generation_workflow_demo.ipynb')


@unittest.skipUnless(importlib.util.find_spec('pymupdf'), 'Install the export extra')
class NotebookExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.run = Path(self.temp.name).resolve()
        # Keep the platform alias in source_path to exercise save/load normalization.
        self.source = Path(self.temp.name) / 'lecture.pdf'
        self.source.write_bytes((ROOT / 'examples/data/sample_lecture_3p.pdf').read_bytes())
        self.project = add_manual_note(
            create_project(PDFReader(render_preview=False).inspect(self.source), self.source),
            original_page=2, title='Reviewed sample', content='Current reviewed content.', language='en',
        )
        self.note_id = self.project.notes[0].note_id

    def namespace(self, notebook, project):
        nb = json.loads((ROOT / 'examples' / notebook).read_text())
        code = next(''.join(c['source']) for c in nb['cells'] if c.get('id') == 'export-pdf')
        namespace = dict(project=project, root=self.run, repo_root=self.run, run_dir=self.run,
                         Path=Path, tempfile=tempfile, save_project=save_project,
                         load_project=load_project, ContractError=ContractError)
        return code, namespace

    def execute(self, code, namespace):
        capture = StringIO()
        with redirect_stdout(capture):
            exec(compile(code, '<notebook export cell>', 'exec'), namespace)
        return capture.getvalue()

    def test_drafts_do_not_create_a_pdf(self):
        for notebook in NOTEBOOKS:
            with self.subTest(notebook=notebook):
                code, ns = self.namespace(notebook, self.project)
                output = self.execute(code, ns)
                self.assertIsNone(ns['export_result'])
                self.assertIn('No approved notes', output)
                self.assertEqual(list(self.run.glob('export-*')), [])
                self.assertEqual(ns['project'], self.project)

    def test_current_project_is_exported_and_replays_preserve_earlier_results(self):
        for notebook in NOTEBOOKS:
            with self.subTest(notebook=notebook):
                approved = approve_note(self.project, self.note_id)
                code, ns = self.namespace(notebook, approved)
                # An older reopened variable must not supply current export content.
                ns['reopened'] = self.project
                before = self.source.read_bytes()
                self.execute(code, ns)
                first = Path(ns['export_result'].output_path)
                first_bytes = first.read_bytes()
                self.assertEqual(ns['export_result'].output_page_count, 4)
                self.assertEqual(replace(load_project(ns['export_project_file']), source_path=approved.source_path), approved)
                ns['project'] = update_note(approved, self.note_id, content='New wording needs review.')
                self.execute(code, ns)
                self.assertIsNone(ns['export_result'])
                self.assertIsNone(ns['export_project_file'])
                ns['project'] = approve_note(ns['project'], self.note_id)
                self.execute(code, ns)
                second = Path(ns['export_result'].output_path)
                self.assertNotEqual(first, second)
                self.assertEqual(first.read_bytes(), first_bytes)
                self.assertEqual(self.source.read_bytes(), before)
                saved = load_project(ns['export_project_file'])
                self.assertEqual(saved.notes[0].sections[0].content, 'New wording needs review.')
                self.assertEqual(replace(saved, source_path=ns['project'].source_path), ns['project'])

    def test_failure_clears_previous_result_without_changing_notes(self):
        for notebook in NOTEBOOKS:
            with self.subTest(notebook=notebook):
                approved = approve_note(self.project, self.note_id)
                code, ns = self.namespace(notebook, approved)
                self.execute(code, ns)
                previous = Path(ns['export_result'].output_path)
                content = previous.read_bytes()
                with patch.object(PyMuPDFPDFExporter, 'export', side_effect=ValueError('Unsupported glyph')):
                    output = self.execute(code, ns)
                self.assertIn('Export failed:', output)
                self.assertIsNone(ns['export_result'])
                self.assertIsNone(ns['export_project_file'])
                self.assertEqual(previous.read_bytes(), content)
                self.assertEqual(ns['project'], approved)


if __name__ == '__main__':
    unittest.main()
