"""Export approved notes to a study PDF without an AI request.

Default: reviewed English/Chinese demonstration notes on the bundled PDF.
Use --project path/to/study.json to export your own already-approved notes.
"""

from argparse import ArgumentParser
from pathlib import Path
import tempfile

from noteweaver import (
    PyMuPDFPDFExporter, add_manual_note, approve_note, create_project,
    load_project, save_project, validate_export,
)
from noteweaver.pdf_reader import PDFReader

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, help='Saved project; existing review states are preserved')
    parser.add_argument('--long', action='store_true', help='Use a long bilingual demo note to inspect pagination')
    args = parser.parse_args()
    if args.project and args.long:
        parser.error('--long is only available for the bundled demonstration')
    if args.project:
        project = load_project(args.project)
        source = Path(project.source_path)
    else:
        source = ROOT / 'examples/data/sample_lecture_3p.pdf'
        project = create_project(PDFReader(render_preview=False).inspect(source), source)
        print('OFFLINE DEMO: approving the supplied sample notes, not personal or AI-generated notes.')
        content = 'A free lecture still uses time. The next best use of that time is its opportunity cost.'
        project = add_manual_note(project, original_page=2, title='Opportunity cost: a student example',
                                  content=content, language='en')
        project = approve_note(project, project.notes[-1].note_id)
        content = '免費講座仍然有機會成本。\n參加講座的時間，不能同時用來溫習或休息。'
        if args.long:
            content += '\n\n' + '\n'.join(
                f'Example {i:03d}: 選擇一項活動，就需要放棄另一個選項。 Consider the next best alternative.'
                for i in range(1, 121)
            )
        project = add_manual_note(project, original_page=2, title='機會成本：學生例子',
                                  content=content, language='zh-Hant')
        project = approve_note(project, project.notes[-1].note_id)
    folder = ROOT / 'generated/export-demo'
    folder.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix='run-', dir=folder))
    saved = save_project(project, run / 'study.json')
    restored = load_project(saved)
    result = PyMuPDFPDFExporter().export(source, restored, run / 'study.pdf')
    validate_export(restored, result)
    print(f'Exported {len(result.note_to_output_pages)} approved notes; drafts were excluded.')
    print(f'PDF: {result.output_path}')
    print(f'Project: {saved}')
    print(f'Total pages: {result.output_page_count}')
    print('Original page map:', [(p.original_page, p.output_page) for p in result.original_to_output_pages])
    print('Note page map:', [(p.note_id, p.output_pages) for p in result.note_to_output_pages])


if __name__ == '__main__':
    main()
