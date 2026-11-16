# PDF Loading, Text Extraction, and Page Previews

[Repository home](../README.md) · [Documentation index](README.md)

This module implements `PDFReader` (from `src/noteweaver/interfaces.py`) in `src/noteweaver/pdf_reader.py`. It loads text-based lecture PDFs, computes stable SHA-256 document identities via `document_id_for_file()`, extracts 1-based page text while distinguishing `ok`, `empty`, and `error` states, validates page bounds with `validate_page()`, and generates page previews ready for Jupyter Notebooks.

## Dependencies and installation

Install the local checkout and PDF dependencies (`pypdf` for text extraction; `pypdfium2` and `pillow` for high-resolution page preview rendering):

```bash
python -m pip install -e ".[preview]"
python examples/pdf_reader_demo.py
python -m unittest discover -s tests -v
```

`examples/pdf_reader_demo.py` opens the bundled 3-page bilingual lecture fixture (`examples/data/sample_lecture_3p.pdf`), inspects its metadata (`page_count == 3`), extracts Chinese and English text from original page 2, renders a PNG preview, and verifies error handling for invalid pages (`0` and `4`) and missing files.

## Public API

Import `PDFReader`, `PagePreview`, and convenience functions from `noteweaver.pdf_reader`:

| Class / Function | Parameters | Return value and behavior |
| --- | --- | --- |
| `PDFReader(preview_dir=None, *, render_preview=True, preview_scale=2.0)` | Optional preview cache directory, toggle, and render scale | Reader instance implementing `interfaces.PDFReader` |
| `reader.inspect(source)` | `source: str or Path` | `DocumentInfo(document_id, filename, page_count)` using `document_id_for_file(source)` |
| `reader.read_page(source, original_page, *, render_preview=None, preview_dir=None)` | `source: str or Path`, 1-based `original_page: int` | `PageContent` validated with `validate_page(document, page)` |
| `reader.preview_page(source, original_page, *, output_path=None, scale=None)` | `source: str or Path`, 1-based `original_page: int` | `PagePreview` with `_repr_png_()` and `_repr_html_()` for Jupyter Notebooks |
| `reader.read_pages(source, original_pages, *, render_preview=None)` | Sequence of unique 1-based page numbers | `tuple[PageContent, ...]` in requested order |
| `reader.read_neighboring_pages(source, original_page, *, radius=1, include_empty=False)` | Target 1-based page and neighbor window radius | `tuple[PageContent, ...]` for Member 2 context selection |
| `inspect_pdf(source)` | `source: str or Path` | Shorthand for `PDFReader().inspect(source)` |
| `read_pdf_page(source, original_page, *, preview_dir=None, render_preview=True)` | `source: str or Path`, 1-based `original_page: int` | Shorthand for `PDFReader(...).read_page(...)` |
| `preview_pdf_page(source, original_page, *, output_path=None, scale=2.0)` | `source: str or Path`, 1-based `original_page: int` | Shorthand for `PDFReader(...).preview_page(...)` |

## Displaying page previews in Jupyter Notebook

1. **Rich inline preview with `preview_page()`**:
   ```python
   from noteweaver.pdf_reader import PDFReader

   reader = PDFReader()
   preview = reader.preview_page("examples/data/sample_lecture_3p.pdf", 2)
   preview
   ```
2. **File-based preview via `PageContent.preview_path`**:
   ```python
   from IPython.display import Image, display
   from noteweaver.pdf_reader import PDFReader

   reader = PDFReader(preview_dir="generated/previews")
   page2 = reader.read_page("examples/data/sample_lecture_3p.pdf", 2)
   if page2.preview_path is not None:
       display(Image(filename=page2.preview_path))
   else:
       print("Preview unavailable; extracted text is still accessible.")
   ```


## Preview failures and source safety

Previews render the actual PDF page using PDFium and Pillow. The reader never
substitutes extracted text or a blank placeholder for a failed rendering.

- `read_page()` treats a preview as optional. Missing rendering dependencies,
  rendering failures, or write failures emit `PreviewWarning` and return
  `preview_path=None`. Extracted text, `extraction_status`, and `error_message`
  retain their text-extraction meaning. A stale cached image is not returned.
- `preview_page()` explicitly requests an image. Missing dependencies or failed
  rendering raise `PreviewError`; file-write failures raise `OSError` subclasses.
  Import these exception classes from `noteweaver.pdf_reader`.
- For text only, use `PDFReader(render_preview=False)` or pass
  `render_preview=False` to `read_page()`. Only the base installation is needed.
- Output paths referring to the source PDF, including normalized paths and hard
  links, raise `ContractError`. Symbolic-link destinations are also rejected.
  These checks apply to explicit output paths and generated cache paths. Invalid
  destinations are errors even when previews are optional.
- Preview files are written to a temporary file and atomically replaced, so a
  failed write does not truncate an existing preview. Rendering scales must be
  positive and finite.

## Bilingual fixture and verification

The three-page sample embeds a licensed Chinese font subset. Its original
English and Chinese lecture text and 1-based page order are preserved. See the
[font provenance and rebuild instructions](../examples/data/fonts/README.md).
The subset is fixture-specific; it must not be used to render arbitrary notes.
This fixture fix does not repair missing or incorrect fonts in user-supplied PDFs.

Regenerating the sample changes its document fingerprint. Recreate projects tied
to the previous sample instead of bypassing source verification. Shared models,
persisted JSON schemas, and page-anchor semantics remain unchanged.

`tests/test_pdf_preview_safety.py` checks source aliases, cache aliases, absent
rendering dependencies, rendering and write failures, preservation of extraction
errors, invalid scales, and embedded font resources. Also visually inspect all
three pages after changing the fixture: successful text extraction alone cannot
prove that the displayed glyphs are correct.
