# PDF Export

[Repository home](../../README.md) · [Documentation index](../README.md)

`PyMuPDFPDFExporter` inserts approved notes after their original PDF pages and
returns the shared `ExportResult`. It does not call AI or approve notes.

## Install and try

```bash
python -m pip install -e ".[preview,export]"
python examples/export_demo.py
python examples/export_demo.py --long
python -m unittest discover -s tests -v
```

The first demo creates two supplied, reviewed sample notes (English and
Traditional Chinese) on original page 2. The five-page output is original page
1, original page 2, English note, Chinese note, original page 3. The long version
exercises continuation pages. Each run saves `study.pdf` and `study.json` in a
new ignored `generated/export-demo/run-*` folder and prints both page maps.

To export an existing project without changing its approval states:

```bash
python examples/export_demo.py --project generated/your-run/study.json
```

Replace the path with your project. Drafts are excluded. A project containing no
approved notes produces the original pages plus navigation, with no note pages.
Both [notebooks](../guides/NOTEBOOK_DEMO.md) also export approved notes, display a real
output-page preview, and offer PDF/JSON downloads. The generation notebook
requires explicit confirmation; its default Run All keeps drafts and skips export.

## Public API

```python
from pathlib import Path
from noteweaver import PyMuPDFPDFExporter, load_project, validate_export

project = load_project("local_data/reviewed-project.json")
result = PyMuPDFPDFExporter().export(
    Path(project.source_path), project, Path("local_data/study.pdf")
)
validate_export(project, result)
print(result.output_page_count)
print(result.original_to_output_pages)
print(result.note_to_output_pages)
```

The parent directory must exist and the destination must be new. Pass an
unchanged source PDF, a real `ProjectState`, and a destination path. All public
page numbers are 1-based. The package uses `GeneratedNote.original_page`, ordered
`NoteSection` values, `OriginalPageLocation`, and `NotePageLocation`; it does not
define an alternative project or note format. The project remains unchanged.

Review/edit notes through the existing [project API](PROJECT_WORKFLOW.md), then
call `approve_note` only after review. Save those states with `save_project` if
you want them retained. Reloading alone never approves a draft.

## Layout and navigation

- Preserve the original page content/order and insert approved notes in stored
  order after each original page. Each note starts on a new A4 page.
- Wrap titles and text using actual glyph widths. Pagination consumes remaining
  text and preserves paragraph breaks; long words can split across lines.
- Render section kinds and origins, including lecture-based claims, AI-added
  material, and user-written content. Source claims are not factual verification.
- Label each supplementary page with its original page, note ordinal, continuation
  page number, and output page number.
- Return complete original/note page maps, checked by `validate_export`.
- Add original-page/note bookmarks and remap existing explicit internal page
  links and page bookmarks to their new destinations.

Content is plain text. Markdown, HTML, and LaTeX syntax are printed literally;
there is no rich formula layout or execution. The bundled backend font supports
English and common Traditional/Simplified Chinese. A missing glyph (for example,
an unsupported emoji) raises `ValueError` identifying its code point instead of
silently producing dots or question marks. Other scripts, complex text shaping,
PDF forms/signatures, and unusual named destinations are not certified by these
checks. Password-protected PDFs requiring authentication are rejected.

## Source and destination protection

The exporter verifies the source fingerprint, reads a verified byte snapshot,
and checks the actual page count. It verifies the on-disk source again before
publishing. Wrong fingerprints/page counts raise `ContractError`.

The source itself and its symbolic/hard-link aliases are rejected. Any existing
output, including a dangling symbolic link, is refused. Export writes a temporary
sibling PDF, validates its page count, then publishes through an exclusive hard
link so a concurrent destination is not overwritten. Temporary files are removed
on success and handled failures. Unsupported filesystem operations raise
`OSError`; there is no unsafe overwrite fallback. This is not a synchronization
or power-loss recovery mechanism; forced termination can leave a temporary file.

## Dependency and font provenance

The `export` extra installs PyMuPDF. Other workflows can import NoteWeaver without
that extra; creating an exporter explains how to install it if missing. Exporter
tests are skipped explicitly when the extra is absent, so full verification must
install `.[preview,export]`. All tests use the existing unittest runner.

Rendering uses PyMuPDF/MuPDF's bundled **Droid Sans Fallback** through
`Font("cjk")`, embedded in the output. It does not depend on installed system
fonts or the small fixture-only font in `examples/data/fonts/`.
See the [backend font documentation](https://pymupdf.readthedocs.io/en/latest/font.html)
and [upstream Droid font notice](https://github.com/ArtifexSoftware/mupdf/blob/master/resources/fonts/droid/NOTICE).
No additional font binary is vendored here.

PyMuPDF/MuPDF provides AGPL and commercial licensing options; see its
[license information](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright).
The team must account for dependency terms when deciding the package license
and release. This change does not choose a package-wide license or publish PyPI.

## Validation

Verified locally on Python 3.14 with PyMuPDF 1.26.7 and 2.1; see the
[evaluator guide](../validation/EVALUATION.md) for installation evidence and limits.

`tests/test_pdf_exporter.py` uses actual shared models and tests approved/draft
filtering, multiple notes, complete maps, original-page rendered pixels, long
content/title wrapping, Chinese/formula text extraction, fake generation through
save/reload/export, source changes, aliases, concurrent output creation, missing
glyphs, and remapped bookmarks/links. Representative English and multipage Chinese
outputs are also rendered and visually inspected during release review.
