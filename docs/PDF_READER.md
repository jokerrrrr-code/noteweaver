# Member 1: PDF Loading, Text Extraction, and Page Previews

This module implements `PDFReader` (from `src/noteweaver/interfaces.py`) in `src/noteweaver/pdf_reader.py`. It loads text-based lecture PDFs, computes stable SHA-256 document identities via `document_id_for_file()`, extracts 1-based page text while distinguishing `ok`, `empty`, and `error` states, validates page bounds with `validate_page()`, and generates page previews ready for Jupyter Notebooks.

## Dependencies and installation

Install the local checkout and PDF dependencies (`pypdf` for text extraction; `pypdfium2` and `pillow` for high-resolution page preview rendering):

```bash
python -m pip install -e .
python -m pip install pypdf pypdfium2 pillow
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
   display(Image(filename=page2.preview_path))
   ```
