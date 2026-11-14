"""Shared contracts, note management, and verified project persistence."""

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
from .project import (
    add_manual_note, approve_note, create_project, delete_note, list_notes, update_note,
)
from .persistence import load_project, save_project

__all__ = [
    "SCHEMA_VERSION", "ContractError", "DocumentInfo", "ExportResult",
    "GeneratedNote", "NotePageLocation", "NoteRequest", "NoteSection",
    "OriginalPageLocation", "PageContent", "ProjectState", "document_id_for_file",
    "validate_export", "validate_generation", "validate_page", "validate_request",
    "verify_source",
    "add_manual_note", "approve_note", "create_project", "delete_note", "list_notes",
    "update_note",
    "load_project", "save_project",
]
