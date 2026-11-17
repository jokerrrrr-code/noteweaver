"""Shared contracts, note management, generation, and verified project persistence."""

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
from .generation import NoteGenerator, default_generator
from .workflow import generate_note
from .exporters import PyMuPDFPDFExporter
from .providers import GenerationError, FakeNoteProvider, NoteProvider, OpenAICompatibleProvider, GroqProvider

__all__ = [
    "PyMuPDFPDFExporter", "SCHEMA_VERSION", "ContractError", "DocumentInfo", "ExportResult",
    "GeneratedNote", "NotePageLocation", "NoteRequest", "NoteSection",
    "OriginalPageLocation", "PageContent", "ProjectState", "document_id_for_file",
    "validate_export", "validate_generation", "validate_page", "validate_request",
    "verify_source",
    "add_manual_note", "approve_note", "create_project", "delete_note", "list_notes",
    "update_note",
    "load_project", "save_project",
    "NoteGenerator", "default_generator", "generate_note", "GroqProvider",
    "GenerationError", "FakeNoteProvider", "NoteProvider", "OpenAICompatibleProvider",
]
