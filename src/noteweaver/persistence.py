"""UTF-8 project files, portable source paths, and source fingerprint checks."""

from dataclasses import replace
import os
from pathlib import Path
import tempfile

from .models import ContractError, ProjectState, verify_source


def _path(value: str | Path, name: str) -> Path:
    if not isinstance(value, (str, Path)) or (isinstance(value, str) and not value.strip()):
        raise ContractError(f"{name} must be a nonblank string or Path")
    if "\0" in str(value):
        raise ContractError(f"{name} must not contain null characters")
    return Path(value)


def _resolve_source(value: str | Path, project_file: Path) -> Path:
    source = _path(value, "source_path")
    if not source.is_absolute():
        source = project_file.parent / source
    return source.resolve(strict=True)


def _stored_source(source: Path, directory: Path) -> str:
    try:
        return os.path.relpath(source, directory)
    except ValueError:
        # Windows cannot represent a relative path between different drives.
        return str(source)


def save_project(
    project: ProjectState, path: str | Path, *, overwrite: bool = False,
) -> Path:
    """Save validated project JSON, returning its absolute file path.

    Verify source bytes before writing. Relative project.source_path values are
    resolved against the destination JSON directory, never the working directory.
    Store a relative source path when possible; the input object is unchanged.
    Existing files require overwrite=True. Reject source-file aliases and
    symbolic-link destinations. The destination parent must already exist.

    Write and fsync a temporary sibling, then publish it with an exclusive hard
    link (new file) or os.replace (explicit overwrite). An error before publication
    leaves an existing project untouched. No PDF parsing or schema migration occurs.
    """
    if type(project) is not ProjectState:
        raise ContractError("project must be a ProjectState")
    if type(overwrite) is not bool:
        raise ContractError("overwrite must be a boolean")
    destination = _path(path, "path")
    if destination.is_symlink():
        raise ContractError("cannot save a project through a symbolic-link destination")
    destination = destination.resolve()
    source = _resolve_source(project.source_path, destination)
    if destination == source or (destination.exists() and destination.samefile(source)):
        raise ContractError("project destination must not be the source document")
    if destination.is_dir():
        raise IsADirectoryError(f"project destination is a directory: {destination}")
    if destination.exists() and not overwrite:
        raise FileExistsError(f"project already exists: {destination}; use overwrite=True to replace it")
    verify_source(project, source)
    stored = replace(project, source_path=_stored_source(source, destination.parent))
    payload = stored.to_json() + "\n"

    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=destination.parent,
            prefix=f".{destination.name}.", suffix=".tmp", delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if overwrite:
            os.replace(temporary, destination)
        else:
            # Unlike a check followed by replace, this cannot clobber a file
            # another process created while the temporary file was being written.
            os.link(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return destination


def load_project(path: str | Path, *, source_path: str | Path | None = None) -> ProjectState:
    """Load strict v1 JSON and verify its source; return an absolute source path.

    Stored relative paths (and relative source overrides) resolve against the
    resolved JSON file's directory. An override relinks a moved source only when
    its bytes match the saved fingerprint. It does not modify the JSON file.
    Returning an absolute source path makes subsequent Save As operations safe.
    Missing/unreadable files raise OSError subclasses; invalid data or changed
    source bytes raise ContractError. There is no unchecked-load option.
    """
    project_file = _path(path, "path").resolve(strict=True)
    try:
        text = project_file.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ContractError("project file must contain UTF-8 JSON") from error
    project = ProjectState.from_json(text)
    source = _resolve_source(project.source_path if source_path is None else source_path, project_file)
    verify_source(project, source)
    return replace(project, source_path=str(source))
