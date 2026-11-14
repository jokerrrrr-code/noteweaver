"""Member 1: PDF loading, 1-based page text extraction, and notebook previews."""

from __future__ import annotations

import base64
from collections.abc import Sequence
from dataclasses import dataclass
import html
import io
from pathlib import Path
import re
import struct
import tempfile
import zlib

import pypdf
from pypdf.errors import PdfReadError, PdfStreamError

from .models import (
    ContractError,
    DocumentInfo,
    PageContent,
    document_id_for_file,
    validate_page,
)

_SECRET_PATTERN = re.compile(
    r"(?i)\b(api[_-]?key|token|secret|password|authorization|bearer)\s*([:=])\s*\S+"
)


def _validate_source_path(source: str | Path) -> Path:
    """Validate source argument type and check that the file exists."""
    if not isinstance(source, (str, Path)) or (
        isinstance(source, str) and not source.strip()
    ):
        raise ContractError("source must be a nonblank string or Path")
    if "\0" in str(source):
        raise ContractError("source must not contain null characters")
    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"PDF source file not found: {path}")
    if path.is_dir():
        raise IsADirectoryError(f"PDF source path is a directory: {path}")
    return path


def _validate_page_number(original_page: int, name: str = "original_page") -> int:
    """Enforce strict 1-based integer page numbers without boolean/float coercion."""
    if type(original_page) is not int or original_page <= 0:
        raise ContractError(f"{name} must be a positive integer (page numbers are 1-based)")
    return original_page


def _sanitize_error_message(error: Exception, original_page: int) -> str:
    """Build a displayable extraction error reason with potential secrets redacted."""
    raw = str(error).strip()
    if raw:
        redacted = _SECRET_PATTERN.sub(r"\1\2[REDACTED]", raw)
        return f"Page {original_page} text extraction failed ({type(error).__name__}): {redacted}"
    return f"Page {original_page} text extraction failed ({type(error).__name__})"


def _open_pdf_reader(path: Path) -> pypdf.PdfReader:
    """Open a PDF with pypdf and reject unreadable, encrypted, or empty files."""
    with path.open("rb") as stream:
        header = stream.read(1024)
    if b"%PDF-" not in header:
        raise ContractError(f"Invalid or unreadable PDF file '{path.name}': missing %PDF- header")

    try:
        reader = pypdf.PdfReader(str(path), strict=False)
        if reader.is_encrypted:
            try:
                decrypt_result = reader.decrypt("")
            except Exception as error:
                raise ContractError(
                    f"PDF file is encrypted and requires a password: {path.name}"
                ) from error
            if decrypt_result == 0:
                raise ContractError(
                    f"PDF file is encrypted and requires a password: {path.name}"
                )
        page_count = len(reader.pages)
    except ContractError:
        raise
    except (PdfReadError, PdfStreamError, ValueError, TypeError, EOFError, KeyError, IndexError) as error:
        raise ContractError(f"Invalid or unreadable PDF file '{path.name}': {error}") from error
    except OSError:
        raise
    except Exception as error:
        raise ContractError(f"Failed to read PDF structure from '{path.name}': {error}") from error

    if page_count <= 0:
        raise ContractError(f"PDF file has no pages: {path.name}")
    return reader


def _minimal_png_bytes(width: int = 320, height: int = 420) -> bytes:
    """Create a valid minimal light-gray PNG using only the Python standard library."""
    raw_rows = bytearray()
    for y in range(height):
        raw_rows.append(0)
        border = y in (0, height - 1)
        for x in range(width):
            if border or x in (0, width - 1):
                raw_rows.extend((30, 58, 95))
            else:
                raw_rows.extend((248, 250, 252))

    def _chunk(tag: bytes, payload: bytes) -> bytes:
        crc = zlib.crc32(tag + payload) & 0xFFFFFFFF
        return struct.pack(">I", len(payload)) + tag + payload + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    idat = zlib.compress(bytes(raw_rows), level=6)
    return b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", idat) + _chunk(b"IEND", b"")


def _render_page_png_bytes(
    source_path: Path,
    original_page: int,
    *,
    scale: float = 2.0,
    fallback_text: str = "",
) -> bytes:
    """Render a 1-based PDF page to PNG bytes for preview files and notebooks."""
    if type(scale) not in (int, float) or scale <= 0:
        raise ContractError("preview_scale must be a positive number")

    page_index = original_page - 1

    try:
        import pypdfium2 as pdfium  # type: ignore[import-not-found]

        pdf_doc = pdfium.PdfDocument(str(source_path))
        try:
            pdf_page = pdf_doc[page_index]
            try:
                bitmap = pdf_page.render(scale=float(scale))
                pil_image = bitmap.to_pil()
                buffer = io.BytesIO()
                pil_image.save(buffer, format="PNG")
                return buffer.getvalue()
            finally:
                pdf_page.close()
        finally:
            pdf_doc.close()
    except Exception:
        pass

    try:
        from PIL import Image, ImageDraw  # type: ignore[import-not-found]

        image = Image.new("RGB", (600, 840), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.rectangle([20, 20, 580, 72], fill=(30, 58, 95))
        draw.text((36, 38), f"{source_path.name} - Original Page {original_page}", fill=(255, 255, 255))
        y = 96
        for line in (fallback_text or "[No extractable text on this page]").splitlines()[:28]:
            draw.text((36, y), line[:72], fill=(31, 41, 55))
            y += 24
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()
    except Exception:
        return _minimal_png_bytes()


@dataclass(frozen=True)
class PagePreview:
    """Notebook-ready preview bundle for a 1-based original PDF page."""

    document: DocumentInfo
    page: PageContent
    preview_path: str
    png_bytes: bytes

    def __post_init__(self) -> None:
        if type(self.document) is not DocumentInfo:
            raise ContractError("document must be a DocumentInfo")
        if type(self.page) is not PageContent:
            raise ContractError("page must be a PageContent")
        validate_page(self.document, self.page)
        if type(self.preview_path) is not str or not self.preview_path.strip():
            raise ContractError("preview_path must be a nonblank string")
        if type(self.png_bytes) is not bytes or not self.png_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ContractError("png_bytes must contain valid PNG image bytes")

    def _repr_png_(self) -> bytes:
        """IPython / Jupyter hook for direct PNG image display."""
        return self.png_bytes

    def _repr_html_(self) -> str:
        """IPython / Jupyter hook rendering the page image and safe metadata card."""
        encoded = base64.b64encode(self.png_bytes).decode("ascii")
        safe_filename = html.escape(self.document.filename)
        safe_status = html.escape(self.page.extraction_status)
        if self.page.extraction_status == "ok":
            snippet = self.page.text[:300] + ("..." if len(self.page.text) > 300 else "")
            safe_body = f"<pre style='margin:8px 0 0;white-space:pre-wrap;font-size:12px;color:#1f2937;'>{html.escape(snippet)}</pre>"
        elif self.page.extraction_status == "empty":
            safe_body = "<p style='margin:8px 0 0;font-size:12px;color:#6b7280;'><em>No extractable text on this page (blank or scanned).</em></p>"
        else:
            safe_err = html.escape(self.page.error_message or "Unknown extraction error")
            safe_body = f"<p style='margin:8px 0 0;font-size:12px;color:#b91c1c;'><strong>Extraction error:</strong> {safe_err}</p>"

        return (
            "<div style='border:1px solid #cbd5e1;border-radius:8px;padding:12px;"
            "max-width:680px;background:#f8fafc;font-family:sans-serif;'>"
            "<div style='display:flex;justify-content:space-between;align-items:center;"
            "margin-bottom:8px;color:#0f172a;font-size:13px;font-weight:600;'>"
            f"<span>{safe_filename} — Original Page {self.page.original_page} of {self.document.page_count}</span>"
            f"<span style='background:#e2e8f0;padding:2px 8px;border-radius:12px;font-size:11px;'>"
            f"status: {safe_status}</span>"
            "</div>"
            f"<img src='data:image/png;base64,{encoded}' "
            f"alt='Page {self.page.original_page} preview' "
            "style='max-width:100%;height:auto;border:1px solid #e2e8f0;border-radius:4px;background:#ffffff;'/>"
            f"{safe_body}"
            "</div>"
        )


class PDFReader:
    """Concrete implementation of interfaces.PDFReader for Member 1."""

    def __init__(
        self,
        preview_dir: str | Path | None = None,
        *,
        render_preview: bool = True,
        preview_scale: float = 2.0,
    ) -> None:
        if type(render_preview) is not bool:
            raise ContractError("render_preview must be a boolean")
        if type(preview_scale) not in (int, float) or preview_scale <= 0:
            raise ContractError("preview_scale must be a positive number")
        if preview_dir is not None:
            if not isinstance(preview_dir, (str, Path)) or (
                isinstance(preview_dir, str) and not preview_dir.strip()
            ):
                raise ContractError("preview_dir must be a nonblank string, Path, or None")
            if "\0" in str(preview_dir):
                raise ContractError("preview_dir must not contain null characters")
            self._preview_dir: Path | None = Path(preview_dir)
        else:
            self._preview_dir = None
        self.render_preview = render_preview
        self.preview_scale = float(preview_scale)

    def _resolve_preview_file(
        self,
        document: DocumentInfo,
        original_page: int,
        preview_dir: str | Path | None = None,
    ) -> Path:
        if preview_dir is not None:
            if not isinstance(preview_dir, (str, Path)) or (
                isinstance(preview_dir, str) and not preview_dir.strip()
            ):
                raise ContractError("preview_dir must be a nonblank string or Path")
            target_dir = Path(preview_dir)
        elif self._preview_dir is not None:
            target_dir = self._preview_dir
        else:
            target_dir = Path(tempfile.gettempdir()) / "noteweaver_previews"

        target_dir.mkdir(parents=True, exist_ok=True)
        short_hash = document.document_id.removeprefix("sha256:")[:16]
        return (target_dir / f"{short_hash}_page_{original_page}.png").resolve()

    def inspect(self, source: str | Path) -> DocumentInfo:
        """Read page count and compute SHA-256 document identity without modifying source."""
        path = _validate_source_path(source)
        doc_id = document_id_for_file(path)
        reader = _open_pdf_reader(path)
        return DocumentInfo(
            document_id=doc_id,
            filename=path.name,
            page_count=len(reader.pages),
        )

    def read_page(
        self,
        source: str | Path,
        original_page: int,
        *,
        render_preview: bool | None = None,
        preview_dir: str | Path | None = None,
    ) -> PageContent:
        """Extract 1-based page text, classify status ('ok'|'empty'|'error'), and validate page."""
        _validate_page_number(original_page, "original_page")
        if render_preview is not None and type(render_preview) is not bool:
            raise ContractError("render_preview must be a boolean or None")

        path = _validate_source_path(source)
        doc_id = document_id_for_file(path)
        reader = _open_pdf_reader(path)
        document = DocumentInfo(
            document_id=doc_id,
            filename=path.name,
            page_count=len(reader.pages),
        )

        probe = PageContent(
            document_id=document.document_id,
            original_page=original_page,
            text="",
            extraction_status="empty",
        )
        validate_page(document, probe)

        pdf_page = reader.pages[original_page - 1]

        text = ""
        status = "empty"
        error_message: str | None = None

        try:
            extracted = pdf_page.extract_text()
        except Exception as error:
            status = "error"
            text = ""
            error_message = _sanitize_error_message(error, original_page)
        else:
            cleaned = (extracted or "").strip()
            if cleaned:
                status = "ok"
                text = cleaned
            else:
                status = "empty"
                text = ""

        should_render = self.render_preview if render_preview is None else render_preview
        preview_path_str: str | None = None
        if should_render:
            preview_file = self._resolve_preview_file(document, original_page, preview_dir)
            png_bytes = _render_page_png_bytes(
                path,
                original_page,
                scale=self.preview_scale,
                fallback_text=text,
            )
            preview_file.write_bytes(png_bytes)
            preview_path_str = str(preview_file)

        page_content = PageContent(
            document_id=document.document_id,
            original_page=original_page,
            text=text,
            extraction_status=status,  # type: ignore[arg-type]
            preview_path=preview_path_str,
            error_message=error_message,
        )
        validate_page(document, page_content)
        return page_content

    def read_pages(
        self,
        source: str | Path,
        original_pages: Sequence[int],
        *,
        render_preview: bool | None = None,
    ) -> tuple[PageContent, ...]:
        """Read an ordered, duplicate-free sequence of 1-based pages for Member 2 context."""
        if isinstance(original_pages, (str, bytes)) or not isinstance(original_pages, Sequence):
            raise ContractError("original_pages must be a sequence of 1-based page integers")
        page_tuple = tuple(original_pages)
        if not page_tuple:
            raise ContractError("original_pages must not be empty")
        for p in page_tuple:
            _validate_page_number(p, "original_pages item")
        if len(set(page_tuple)) != len(page_tuple):
            raise ContractError("original_pages must not contain duplicates")
        return tuple(
            self.read_page(source, p, render_preview=render_preview) for p in page_tuple
        )

    def read_neighboring_pages(
        self,
        source: str | Path,
        original_page: int,
        *,
        radius: int = 1,
        include_empty: bool = False,
        render_preview: bool | None = None,
    ) -> tuple[PageContent, ...]:
        """Read target page and neighboring pages within [page - radius, page + radius]."""
        _validate_page_number(original_page, "original_page")
        if type(radius) is not int or radius < 0:
            raise ContractError("radius must be a non-negative integer")
        if type(include_empty) is not bool:
            raise ContractError("include_empty must be a boolean")

        document = self.inspect(source)
        probe = PageContent(
            document_id=document.document_id,
            original_page=original_page,
            text="",
            extraction_status="empty",
        )
        validate_page(document, probe)

        start_page = max(1, original_page - radius)
        end_page = min(document.page_count, original_page + radius)
        pages = tuple(
            self.read_page(source, p, render_preview=render_preview)
            for p in range(start_page, end_page + 1)
        )
        if include_empty:
            return pages
        return tuple(
            p for p in pages if p.original_page == original_page or p.extraction_status == "ok"
        )

    def preview_page(
        self,
        source: str | Path,
        original_page: int,
        *,
        output_path: str | Path | None = None,
        scale: float | None = None,
    ) -> PagePreview:
        """Render a notebook-displayable PagePreview (supports _repr_png_ and _repr_html_)."""
        _validate_page_number(original_page, "original_page")
        effective_scale = self.preview_scale if scale is None else scale
        if type(effective_scale) not in (int, float) or effective_scale <= 0:
            raise ContractError("scale must be a positive number")

        path = _validate_source_path(source)
        document = self.inspect(path)
        page_content = self.read_page(path, original_page, render_preview=False)

        if output_path is not None:
            if not isinstance(output_path, (str, Path)) or (
                isinstance(output_path, str) and not output_path.strip()
            ):
                raise ContractError("output_path must be a nonblank string or Path")
            if "\0" in str(output_path):
                raise ContractError("output_path must not contain null characters")
            preview_file = Path(output_path).resolve()
            preview_file.parent.mkdir(parents=True, exist_ok=True)
        else:
            preview_file = self._resolve_preview_file(document, original_page)

        png_bytes = _render_page_png_bytes(
            path,
            original_page,
            scale=float(effective_scale),
            fallback_text=page_content.text,
        )
        preview_file.write_bytes(png_bytes)

        updated_page = PageContent(
            document_id=page_content.document_id,
            original_page=page_content.original_page,
            text=page_content.text,
            extraction_status=page_content.extraction_status,
            preview_path=str(preview_file),
            error_message=page_content.error_message,
        )
        validate_page(document, updated_page)
        return PagePreview(
            document=document,
            page=updated_page,
            preview_path=str(preview_file),
            png_bytes=png_bytes,
        )


def inspect_pdf(source: str | Path) -> DocumentInfo:
    """Convenience function to inspect a PDF file and return its DocumentInfo."""
    return PDFReader().inspect(source)


def read_pdf_page(
    source: str | Path,
    original_page: int,
    *,
    preview_dir: str | Path | None = None,
    render_preview: bool = True,
) -> PageContent:
    """Convenience function to read a 1-based PDF page and return its PageContent."""
    return PDFReader(preview_dir=preview_dir, render_preview=render_preview).read_page(
        source, original_page
    )


def preview_pdf_page(
    source: str | Path,
    original_page: int,
    *,
    output_path: str | Path | None = None,
    scale: float = 2.0,
) -> PagePreview:
    """Convenience function to produce a Jupyter-displayable PagePreview for a 1-based page."""
    return PDFReader(preview_scale=scale).preview_page(
        source, original_page, output_path=output_path, scale=scale
      )
