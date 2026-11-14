"""Member 1 demonstration: inspect a 3-page lecture PDF, extract page 2, and preview it."""

from pathlib import Path
import tempfile

from noteweaver import ContractError, validate_page
from noteweaver.pdf_reader import PDFReader


def main() -> None:
    sample_pdf = Path(__file__).parent / "data" / "sample_lecture_3p.pdf"

    with tempfile.TemporaryDirectory(prefix="noteweaver-reader-demo-") as temp_dir:
        reader = PDFReader(preview_dir=temp_dir)

        document = reader.inspect(sample_pdf)
        print(f"Document filename: {document.filename}")
        print(f"Document ID:       {document.document_id}")
        print(f"Page count:        {document.page_count}")
        assert document.page_count == 3

        page2 = reader.read_page(sample_pdf, 2)
        validate_page(document, page2)
        assert page2.original_page == 2
        assert page2.extraction_status == "ok"
        assert page2.preview_path is not None and Path(page2.preview_path).is_file()

        print(f"\n--- Original Page {page2.original_page} ({page2.extraction_status}) ---")
        print(page2.text)
        print(f"Preview image saved at: {page2.preview_path}")

        notebook_preview = reader.preview_page(sample_pdf, 2)
        assert notebook_preview._repr_png_().startswith(b"\x89PNG\r\n\x1a\n")
        assert "Original Page 2 of 3" in notebook_preview._repr_html_()
        print(f"Notebook preview PNG size: {len(notebook_preview.png_bytes)} bytes")

        context_pages = reader.read_neighboring_pages(sample_pdf, 2, radius=1)
        print("Neighboring context pages:", [p.original_page for p in context_pages])

        for bad_page in (0, 4):
            try:
                reader.read_page(sample_pdf, bad_page)
            except ContractError as error:
                print(f"Out-of-range page {bad_page} rejected: {error}")

        try:
            reader.inspect(Path(temp_dir) / "missing.pdf")
        except FileNotFoundError as error:
            print(f"Missing file rejected: {error.filename or error}")

    print("\nReader demo finished cleanly; source PDF was not modified.")


if __name__ == "__main__":
    main()
