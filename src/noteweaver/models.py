"""Version-1 shared contracts. No PDF reader, renderer, or AI provider is included."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import hashlib
import json
from pathlib import Path
import re
from types import UnionType
from typing import Any, Literal, TypeVar, Union, get_args, get_origin, get_type_hints

SCHEMA_VERSION = 1
T = TypeVar("T", bound="Model")
ExtractionStatus = Literal["ok", "empty", "error"]
NoteStatus = Literal["draft", "approved"]
ExplanationStyle = Literal["simple", "step_by_step", "comparison", "example"]
SectionKind = Literal["explanation", "steps", "comparison", "example", "quiz", "answer", "personal"]
SectionOrigin = Literal["lecture", "ai", "user"]


class ContractError(ValueError):
    """Invalid shape, unsupported schema, or inconsistent cross-module data."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def _text(value: str, name: str) -> None:
    _require(bool(value.strip()), f"{name} must not be blank")


def _positive(value: int, name: str) -> None:
    _require(value > 0, f"{name} must be positive (page numbers are 1-based)")


def _pages(values: tuple[int, ...], name: str) -> None:
    for value in values:
        _positive(value, name)
    _require(len(set(values)) == len(values), f"{name} must not contain duplicates")


def _document_id(value: str) -> None:
    _require(re.fullmatch(r"sha256:[0-9a-f]{64}", value) is not None,
             "document_id must be sha256: followed by 64 lowercase hex digits")


def document_id_for_file(path: str | Path) -> str:
    """Hash source bytes, not its name. Does not parse or certify a PDF."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _typed(value: Any, expected: Any, name: str, *, decode: bool = False) -> Any:
    """Strict validation for this small contract vocabulary, without coercion."""
    origin, args = get_origin(expected), get_args(expected)
    if origin in (Union, UnionType):
        for option in args:
            try:
                return _typed(value, option, name, decode=decode)
            except ContractError:
                pass
        raise ContractError(f"{name} has an invalid type")
    if origin is Literal:
        _require(any(type(value) is type(item) and value == item for item in args),
                 f"{name} must be one of {args}")
        return value
    if origin is tuple:
        _require(type(value) is (list if decode else tuple),
                 f"{name} must be {'a JSON array' if decode else 'a tuple'}")
        return tuple(_typed(item, args[0], f"{name}[{i}]", decode=decode)
                     for i, item in enumerate(value))
    if isinstance(expected, type) and issubclass(expected, Model):
        if decode:
            return expected.from_dict(value)
        _require(type(value) is expected, f"{name} must be {expected.__name__}")
        return value
    _require(type(value) is expected, f"{name} must have type {expected}")
    return value


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        _require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


class Model:
    """Frozen dataclasses below support strict nested JSON round trips."""

    def __post_init__(self) -> None:
        hints = get_type_hints(type(self))
        for field in fields(self):
            _typed(getattr(self, field.name), hints[field.name], field.name)

    def to_dict(self) -> dict[str, Any]:
        # JSON has arrays, not Python tuples; UTF-8 text is preserved.
        return json.loads(self.to_json())

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2, allow_nan=False)

    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        _require(type(data) is dict, f"{cls.__name__} must be a JSON object")
        hints = get_type_hints(cls)
        names = {field.name for field in fields(cls)}
        _require(not (set(data) - names), f"{cls.__name__} has unknown fields")
        if cls is ProjectState:
            _require("schema_version" in data, "project must declare schema_version")
        values = {key: _typed(value, hints[key], key, decode=True)
                  for key, value in data.items()}
        try:
            return cls(**values)
        except TypeError as error:
            raise ContractError(f"{cls.__name__}: missing required fields") from error

    @classmethod
    def from_json(cls: type[T], text: str) -> T:
        try:
            data = json.loads(text, object_pairs_hook=_unique_object)
        except (json.JSONDecodeError, TypeError) as error:
            raise ContractError("invalid JSON") from error
        return cls.from_dict(data)


@dataclass(frozen=True)
class DocumentInfo(Model):
    document_id: str
    filename: str
    page_count: int

    def __post_init__(self) -> None:
        super().__post_init__()
        _document_id(self.document_id)
        _text(self.filename, "filename")
        _positive(self.page_count, "page_count")


@dataclass(frozen=True)
class PageContent(Model):
    document_id: str
    original_page: int
    text: str
    extraction_status: ExtractionStatus
    preview_path: str | None = None
    error_message: str | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        _document_id(self.document_id)
        _positive(self.original_page, "original_page")
        if self.preview_path is not None:
            _text(self.preview_path, "preview_path")
        if self.extraction_status == "ok":
            _text(self.text, "text for an ok page")
        else:
            _require(self.text == "", "empty/error pages must have empty text")
        if self.extraction_status == "error":
            _require(self.error_message is not None, "error page needs error_message")
            _text(self.error_message, "error_message")
        else:
            _require(self.error_message is None, "only error pages have error_message")


@dataclass(frozen=True)
class NoteRequest(Model):
    request_id: str
    document_id: str
    original_page: int
    question: str
    context_pages: tuple[int, ...]
    selected_text: str | None = None
    language: str = "zh-Hant"
    level: str = "first-year"
    style: ExplanationStyle = "simple"

    def __post_init__(self) -> None:
        super().__post_init__()
        _document_id(self.document_id)
        _positive(self.original_page, "original_page")
        for name in ("request_id", "question", "language", "level"):
            _text(getattr(self, name), name)
        if self.selected_text is not None:
            _text(self.selected_text, "selected_text")
        _pages(self.context_pages, "context_pages")
        _require(self.original_page in self.context_pages,
                 "context_pages must include the target original_page")


@dataclass(frozen=True)
class NoteSection(Model):
    kind: SectionKind
    content: str
    origin: SectionOrigin

    def __post_init__(self) -> None:
        super().__post_init__()
        _text(self.content, "section content")


@dataclass(frozen=True)
class GeneratedNote(Model):
    """Shared shape for AI drafts AND manually entered notes."""

    note_id: str
    document_id: str
    original_page: int
    title: str
    sections: tuple[NoteSection, ...]
    source_pages: tuple[int, ...] = ()
    request_id: str | None = None
    language: str = "zh-Hant"
    status: NoteStatus = "draft"

    def __post_init__(self) -> None:
        super().__post_init__()
        _document_id(self.document_id)
        _positive(self.original_page, "original_page")
        for name in ("note_id", "title", "language"):
            _text(getattr(self, name), name)
        if self.request_id is not None:
            _text(self.request_id, "request_id")
        _require(bool(self.sections), "a note needs at least one section")
        _pages(self.source_pages, "source_pages")
        if any(section.origin == "lecture" for section in self.sections):
            _require(bool(self.source_pages), "lecture sections need source_pages")
        if any(section.origin == "ai" for section in self.sections):
            _require(self.request_id is not None, "AI sections need request_id")


def validate_page(document: DocumentInfo, page: PageContent) -> None:
    _require(page.document_id == document.document_id, "page belongs to another document")
    _require(page.original_page <= document.page_count, "page is outside document")


def validate_request(document: DocumentInfo, request: NoteRequest) -> None:
    _require(request.document_id == document.document_id, "request belongs to another document")
    _require(all(page <= document.page_count for page in request.context_pages),
             "context page is outside document")


def _validate_note_request(request: NoteRequest, note: GeneratedNote) -> None:
    _require(note.request_id == request.request_id, "note/request ID mismatch")
    _require(note.document_id == request.document_id, "note/request document mismatch")
    _require(note.original_page == request.original_page, "note/request page mismatch")
    _require(note.language == request.language, "note/request language mismatch")
    _require(set(note.source_pages) <= set(request.context_pages),
             "source_pages must be within supplied context")


def validate_generation(document: DocumentInfo, request: NoteRequest,
                        context: tuple[PageContent, ...], note: GeneratedNote) -> None:
    """Check supplied pages and response linkage, not factual correctness."""
    validate_request(document, request)
    _typed(context, tuple[PageContent, ...], "context")
    for page in context:
        validate_page(document, page)
        _require(page.extraction_status == "ok", "generation needs successfully extracted text")
    page_numbers = tuple(page.original_page for page in context)
    _pages(page_numbers, "context")
    _require(set(page_numbers) == set(request.context_pages),
             "actual context must match request.context_pages exactly")
    _validate_note_request(request, note)
    _require(note.status == "draft", "new generated notes must be drafts")


@dataclass(frozen=True)
class ProjectState(Model):
    document: DocumentInfo
    source_path: str
    requests: tuple[NoteRequest, ...] = ()
    notes: tuple[GeneratedNote, ...] = ()
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        super().__post_init__()
        _require(self.schema_version == SCHEMA_VERSION, "unsupported schema_version")
        _text(self.source_path, "source_path")
        requests = {item.request_id: item for item in self.requests}
        _require(len(requests) == len(self.requests), "duplicate request_id")
        _require(len({item.note_id for item in self.notes}) == len(self.notes), "duplicate note_id")
        for request in self.requests:
            validate_request(self.document, request)
        for note in self.notes:
            _require(note.document_id == self.document.document_id, "note belongs to another document")
            _require(note.original_page <= self.document.page_count, "note page is outside document")
            _require(all(page <= self.document.page_count for page in note.source_pages),
                     "note source page is outside document")
            if note.request_id is not None:
                _require(note.request_id in requests, "note references missing request")
                _validate_note_request(requests[note.request_id], note)


@dataclass(frozen=True)
class OriginalPageLocation(Model):
    original_page: int
    output_page: int

    def __post_init__(self) -> None:
        super().__post_init__()
        _positive(self.original_page, "original_page")
        _positive(self.output_page, "output_page")


@dataclass(frozen=True)
class NotePageLocation(Model):
    note_id: str
    output_pages: tuple[int, ...]

    def __post_init__(self) -> None:
        super().__post_init__()
        _text(self.note_id, "note_id")
        _require(bool(self.output_pages), "a rendered note needs output pages")
        _pages(self.output_pages, "output_pages")
        _require(self.output_pages == tuple(range(self.output_pages[0], self.output_pages[-1] + 1)),
                 "a note's output pages must be contiguous and ascending")


@dataclass(frozen=True)
class ExportResult(Model):
    document_id: str
    output_path: str
    output_page_count: int
    original_to_output_pages: tuple[OriginalPageLocation, ...]
    note_to_output_pages: tuple[NotePageLocation, ...] = ()

    def __post_init__(self) -> None:
        super().__post_init__()
        _document_id(self.document_id)
        _text(self.output_path, "output_path")
        _positive(self.output_page_count, "output_page_count")
        originals = self.original_to_output_pages
        _require(bool(originals), "export must contain original pages")
        _require(tuple(item.original_page for item in originals) == tuple(range(1, len(originals) + 1)),
                 "original page map must be complete and ordered from page 1")
        original_outputs = tuple(item.output_page for item in originals)
        _require(original_outputs == tuple(sorted(original_outputs)), "original pages must keep order")
        _require(len({item.note_id for item in self.note_to_output_pages}) == len(self.note_to_output_pages),
                 "duplicate exported note_id")
        occupied = list(original_outputs)
        for item in self.note_to_output_pages:
            occupied.extend(item.output_pages)
        _require(sorted(occupied) == list(range(1, self.output_page_count + 1)),
                 "output pages must be covered exactly once, without gaps or overlap")


def validate_export(project: ProjectState, result: ExportResult) -> None:
    """Verify approved-note order/placement against a project; no PDF I/O."""
    _require(result.document_id == project.document.document_id, "export document mismatch")
    _require(len(result.original_to_output_pages) == project.document.page_count,
             "export must include every original page")
    approved = tuple(note for note in project.notes if note.status == "approved")
    locations = {item.note_id: item.output_pages for item in result.note_to_output_pages}
    _require(set(locations) == {note.note_id for note in approved},
             "export must contain all approved notes and no drafts or unknown notes")
    next_page = 1
    for original in result.original_to_output_pages:
        _require(original.output_page == next_page, "original page is misplaced")
        next_page += 1
        for note in approved:
            if note.original_page == original.original_page:
                pages = locations[note.note_id]
                _require(pages == tuple(range(next_page, next_page + len(pages))),
                         "note must follow its original page in project note order")
                next_page += len(pages)


def verify_source(project: ProjectState, path: str | Path) -> None:
    """Call on reload and before export. Missing/unreadable files raise OSError."""
    _require(document_id_for_file(path) == project.document.document_id,
             "source document changed; do not silently reuse page anchors")
