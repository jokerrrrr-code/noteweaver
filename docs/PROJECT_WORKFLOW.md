# Member 4: Manual Note Management (Step 2)

This version provides in-memory project and note operations. It requires no network connection, AI credentials, or other members' modules. A manual note is text entered by the user, not handwriting recognition. PDF reading, generation, export, and file save/load are not integrated yet.

## Quick start

Install the local development package as described in the [README](../README.md), then run these commands from the repository root:

```bash
python examples/manual_notes_demo.py
python -m unittest discover -s tests -v
```

The demo adds, approves, edits, approves again, and deletes a note. After editing, the number of notes eligible for export becomes 0; confirming again makes it 1. The demo uses original sample text and synthetic document metadata. It does not open a real PDF or save any files.

## Available API

Import the following functions directly from `noteweaver`:

| Function | Parameters | Return value and behavior |
| --- | --- | --- |
| `create_project` | `document: DocumentInfo, source_path: str or Path` | Empty `ProjectState`; does not open or verify the source file |
| `add_manual_note` | `project`; keyword arguments `original_page, title, content, language='zh-Hant'` | New project with a draft note appended |
| `update_note` | `project, note_id`; keyword arguments `title=None, content=None` | New project with the selected note edited and reset to draft |
| `approve_note` | `project, note_id` | New project with the selected note marked approved |
| `delete_note` | `project, note_id` | New project without the selected note; retains other notes and request history |
| `list_notes` | `project`; keyword arguments `original_page=None, status=None` | Matching `tuple[GeneratedNote, ...]` in project order |

**Every mutation returns a new ProjectState. Assign it with `project = operation(project, ...)`.** Ignoring the return value leaves your original project unchanged. Earlier states can be retained for comparison, and invalid operations do not corrupt existing data.

## Example: adding and editing a note

```python
from noteweaver import (
    DocumentInfo, create_project, add_manual_note,
    approve_note, update_note, list_notes,
)

# Synthetic metadata for this example only. In production, use reader.inspect().
document = DocumentInfo("sha256:" + "0" * 64, "demo.pdf", 3)
project = create_project(document, "local_data/demo.pdf")
project = add_manual_note(
    project, original_page=2, title="Opportunity cost",
    content="The value of the next-best alternative forgone.", language="en",
)
note_id = project.notes[-1].note_id

# A real UI must wait for explicit user confirmation before calling this.
project = approve_note(project, note_id)
project = update_note(project, note_id, content="Opportunity cost also includes time.")

print(project.notes[0].status)                      # draft
print(project.notes[0].original_page)               # 2
print(project.notes[0].note_id == note_id)           # True
print(len(list_notes(project, status="approved")))  # 0
```

The shared model defaults to `zh-Hant`; pass `language='en'` for English notes. This metadata records the content language; manual-note operations do not translate text.

## Editing and approval rules

- New notes use UUIDs and one section with `kind='personal'` and `origin='user'`. They have no generation request or source claim.
- Original page numbers are 1-based and must be within the document's page count. Title, content, and language must not be blank.
- Editing preserves the note ID, document identity, original page, language, and position in the project.
- For `update_note`, `None` means leave a field unchanged. Supply at least title or content. Every valid edit resets the note to draft, even when the supplied text equals the old value.
- **The content argument replaces the entire body, not an individual section.** It becomes a single user-authored section and clears previous `source_pages` claims. The original `request_id` remains as a record of the generation association. Section-level editing is not available in this version.
- Title-only edits preserve existing sections and source pages.
- Approval is repeatable. It records user confirmation, not verified factual correctness. Do not approve automatically after generation or editing.
- When both list filters are provided, a note must match both. No matches returns an empty tuple.
- No operation reads or writes a PDF. `create_project` does not check whether its source path exists. Relative source paths retain the shared contract's meaning: relative to the eventual project JSON file.

## Errors and tests

- `ContractError`: invalid content or types, out-of-range pages, invalid filters, blank IDs, or an update without any fields.
- `KeyError`: a valid string ID that does not identify a note in the project.

The new tests cover Chinese and English text, unique IDs, note order, approval invalidation, preservation of old data after invalid operations, source labels on body replacement, filtering, and deletion. Existing contract tests remain in use; the shared models and JSON schema are unchanged.

## Next steps and handoff

Member 4's step 3 will add actual file saving/loading, path resolution, and source verification. Results from these operations are standard ProjectState objects, so existing `to_json()` serialization works; serialization alone is not a complete save/load workflow.

Member 1 will supply real DocumentInfo values. Member 2 returns GeneratedNote objects using the same structure. Member 3 accepts the same ProjectState and exports approved notes according to the common contract. This implementation does not replace those members' modules.
