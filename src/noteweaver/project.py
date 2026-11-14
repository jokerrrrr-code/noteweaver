"""In-memory note operations; no PDF, persistence, or provider I/O."""

from dataclasses import replace
from pathlib import Path
from uuid import uuid4

from .models import (
    ContractError, DocumentInfo, GeneratedNote, NoteSection, NoteStatus, ProjectState,
)


def create_project(document: DocumentInfo, source_path: str | Path) -> ProjectState:
    """Create an empty project from reader metadata; does not open the source.

    Relative paths retain the contract's project-JSON-relative meaning. Source
    existence, fingerprint verification, and save/load belong to the I/O layer.
    """
    return ProjectState(document=document, source_path=(
        str(source_path) if isinstance(source_path, Path) else source_path
    ))


def add_manual_note(
    project: ProjectState, *, original_page: int, title: str, content: str,
    language: str = "zh-Hant",
) -> ProjectState:
    """Append a user-written draft. The new ID is in returned_project.notes[-1]."""
    note = GeneratedNote(
        note_id=str(uuid4()), document_id=project.document.document_id,
        original_page=original_page, title=title,
        sections=(NoteSection(kind="personal", content=content, origin="user"),),
        language=language,
    )
    return replace(project, notes=project.notes + (note,))


def _note_index(project: ProjectState, note_id: str) -> int:
    if type(note_id) is not str or not note_id.strip():
        raise ContractError("note_id must be a nonblank string")
    for index, note in enumerate(project.notes):
        if note.note_id == note_id:
            return index
    raise KeyError(f"note_id not found: {note_id}")


def _replace_note(project: ProjectState, index: int, note: GeneratedNote) -> ProjectState:
    return replace(project, notes=project.notes[:index] + (note,) + project.notes[index + 1:])


def update_note(
    project: ProjectState, note_id: str, *, title: str | None = None,
    content: str | None = None,
) -> ProjectState:
    """Edit title and/or replace the ENTIRE body, always returning to draft.

    None means leave that field unchanged; supply at least one field. Body
    replacement becomes one user-authored personal section, with no lecture
    source claims. Title-only edits preserve sections and sources. IDs, anchor,
    language, request linkage, and project order are retained in both cases.
    """
    index = _note_index(project, note_id)
    if title is None and content is None:
        raise ContractError("provide title or content to update a note")
    note = project.notes[index]
    sections = note.sections
    sources = note.source_pages
    if content is not None:
        sections = (NoteSection(kind="personal", content=content, origin="user"),)
        sources = ()
    edited = replace(
        note, title=note.title if title is None else title,
        sections=sections, source_pages=sources, status="draft",
    )
    return _replace_note(project, index, edited)


def approve_note(project: ProjectState, note_id: str) -> ProjectState:
    """Mark a note approved. Call only after explicit user confirmation.

    Repeating approval is safe. This records review state, not factual accuracy.
    """
    index = _note_index(project, note_id)
    return _replace_note(project, index, replace(project.notes[index], status="approved"))


def delete_note(project: ProjectState, note_id: str) -> ProjectState:
    """Remove one note, keeping other notes and request history in order."""
    index = _note_index(project, note_id)
    return replace(project, notes=project.notes[:index] + project.notes[index + 1:])


def list_notes(
    project: ProjectState, *, original_page: int | None = None,
    status: NoteStatus | None = None,
) -> tuple[GeneratedNote, ...]:
    """Return notes in project order, optionally filtering by page and status."""
    if original_page is not None and (
        type(original_page) is not int or not 1 <= original_page <= project.document.page_count
    ):
        raise ContractError("original_page must be an integer within the document (1-based)")
    if status is not None and (type(status) is not str or status not in ("draft", "approved")):
        raise ContractError("status must be draft or approved")
    return tuple(
        note for note in project.notes
        if (original_page is None or note.original_page == original_page)
        and (status is None or note.status == status)
    )
