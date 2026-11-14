"""NoteWeaver's implemented surface currently consists of shared contracts."""

from .models import (
    SCHEMA_VERSION,
    ContractError,
    DocumentInfo,
    ExportResult,
    GeneratedNote,
    NotePageLocation,
    NoteRequest,
    NoteSection,
    OriginalPageLocation,
    PageContent,
    ProjectState,
    document_id_for_file,
    validate_export,
    validate_generation,
    validate_page,
    validate_request,
    verify_source,
)

__all__ = [
    "SCHEMA_VERSION", "ContractError", "DocumentInfo", "ExportResult",
    "GeneratedNote", "NotePageLocation", "NoteRequest", "NoteSection",
    "OriginalPageLocation", "PageContent", "ProjectState", "document_id_for_file",
    "validate_export", "validate_generation", "validate_page", "validate_request",
    "verify_source",
]
