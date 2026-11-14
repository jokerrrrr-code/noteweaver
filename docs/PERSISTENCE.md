# Member 4: Project Saving and Loading (Step 3)

Projects can now be saved to UTF-8 JSON files and reopened with source verification. Notes retain their IDs, original pages, content, order, language, sections, source claims, request history, and draft/approved state. The implementation reuses schema v1 without adding fields or changing the shared models.

This feature does not parse PDFs, generate notes, or export a study PDF. Source checks compare actual bytes with the stored fingerprint; they do not verify PDF structure or the metadata's page count. Real DocumentInfo values will come from member 1's reader.

## Run the demonstration

After installing the checkout, run from the repository root:

```bash
python examples/persistence_demo.py
python -m unittest discover -s tests -v
```

The demo creates a temporary source-byte fixture and real JSON files. It adds two notes to original page 2, approves one, saves, reopens, edits, saves again, relinks a renamed source, and rejects modified source content. The source fixture is not a PDF. All temporary files are removed when the demo finishes.

## Public functions

Import both functions from `noteweaver`:

| Function | Behavior |
| --- | --- |
| `save_project(project, path, *, overwrite=False) -> Path` | Verify source bytes, write the project, and return the absolute JSON path |
| `load_project(path, *, source_path=None) -> ProjectState` | Decode and validate JSON, verify the source, and return a project with an absolute source path |

Both path parameters accept nonblank strings or pathlib.Path values. The source file and destination parent directory must already exist. No directory creation is implicit. A relative JSON path is relative to the current working directory, as with ordinary file APIs.

Saving does not modify the input ProjectState. Loading returns a new ProjectState. If the stored source path was relative, the returned project's path is absolute; the other fields remain unchanged.

## Typical use

This example assumes that `project` is an existing ProjectState whose source path identifies a real, unchanged source. Use an absolute source path when creating a project from a reader.

```python
from pathlib import Path
from noteweaver import load_project, save_project, update_note

folder = Path("local_data")
folder.mkdir(exist_ok=True)
project_file = save_project(project, folder / "revision.json")
reopened = load_project(project_file)

note_id = reopened.notes[0].note_id
reopened = update_note(reopened, note_id, content="My revised explanation.")
save_project(reopened, project_file, overwrite=True)
```

Editing after approval still resets the note to draft, and save/load preserves that state. No confirmation is performed automatically. Do not use the all-zero fingerprint from the old JSON fixtures for actual source files; calculate the real fingerprint instead.

## Source paths and portability

Source path rules are explicit:

1. On save, a relative `project.source_path` is interpreted relative to the **destination JSON directory**, following the shared contract. Prefer absolute paths for newly created in-memory projects to avoid ambiguity.
2. The JSON stores a relative source path when possible. For example, `projects/study.json` may store `../lectures/week1.pdf`.
3. On load, a stored relative source path is resolved relative to the JSON file's directory, not the process's working directory.
4. The loaded ProjectState contains the resolved absolute source path. Saving that object to a different directory recomputes the relative path correctly.
5. A source on a different Windows drive cannot be expressed as a relative path; its absolute path is stored instead.

Moving the JSON and source together with the same folder relationship preserves a relative reference. Moving only the JSON or only the source may require relinking. If the JSON itself is opened through a symbolic link, relative source paths use the resolved JSON file's directory.

Saving an original in-memory project with an unresolved relative path to a different directory reinterprets that path against the new directory. For Save As, use the object returned by load_project, or provide an absolute source path when creating the project.

## Relink a moved source

```python
reopened = load_project("local_data/revision.json", source_path="lectures/renamed.pdf")
```

Here the override resolves to `local_data/lectures/renamed.pdf`. An absolute override also works. The replacement must have the original fingerprint; renaming is acceptable, changed content is not. This operation does not modify the saved JSON. Save the returned project with `overwrite=True` if you want to persist the new reference.

There is no unchecked-load option. A missing source raises FileNotFoundError; a different fingerprint raises ContractError. Existing notes are not silently reattached to a revised lecture.

## Existing files and interrupted writes

- The default refuses to replace any existing file with FileExistsError. Set `overwrite=True` only when replacing a project is intended.
- Saving over the source document or a hard-link alias is rejected. Symbolic-link destinations are also rejected, including dangling links. No operation writes to the source document.
- The complete JSON is written to a temporary sibling file and flushed with fsync before publication. Explicit overwrite uses os.replace; a new-file save uses an exclusive hard link so a concurrent file is not overwritten.
- Failures before publication leave an existing project unchanged. Temporary files are cleaned up on normal completion and handled exceptions.
- The destination filesystem must support the required hard-link/replace operations. Unsupported operations raise OSError; there is no non-atomic fallback.
- This is not a backup or multi-user synchronization system. Concurrent explicit overwrites can replace one another. Forced process termination may leave a temporary file, and directory-level durability across power loss is not guaranteed.

## Error behavior

| Error | Examples |
| --- | --- |
| `ContractError` | Malformed JSON, non-UTF-8 input, unknown fields, unsupported schema version, invalid note relationships, changed source fingerprint, invalid arguments, or a source/symlink destination |
| `FileNotFoundError` | Missing project, missing source, or missing destination parent |
| `FileExistsError` | Existing destination without overwrite=True, including a concurrent creation |
| `IsADirectoryError` | A file path identifies a directory |
| Other `OSError` subclasses | Permission failures, disk failures, or unsupported filesystem operations |

Existing schema validation remains strict, including explicit schema_version, unique IDs, and original-page bounds. No schema migration is performed.

## Tests and team handoff

The persistence tests cover bilingual content, request/section preservation, review state, working-directory independence, Save As, moved folders and sources, changed source bytes, invalid encodings/schema, overwrite handling, source aliases, and injected write failures. Run the full suite so the existing contract and editing behavior remain covered.

Implementation is in `src/noteweaver/persistence.py`; tests are in `tests/test_persistence.py`. Both functions are exported from the package root. The in-memory functions stay in project.py; no dependency on reader, provider, or exporter implementations is introduced.

Member 4's next step is module integration. Member 3 should still verify the source immediately before PDF export, because it may have changed since the project was loaded. JSON stores note/project data only, not the PDF, preview images, or provider configuration. Keep personal project files in ignored local directories.
