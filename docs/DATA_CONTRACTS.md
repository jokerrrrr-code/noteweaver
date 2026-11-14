# NoteWeaver Shared Data Contracts v1

This document, `src/noteweaver/models.py`, `interfaces.py`, and `examples/data/` define the common agreement between the four modules. Models, validators, JSON conversion, and [in-memory note operations](PROJECT_WORKFLOW.md) are implemented. PDF reading, AI calls, PDF rendering, file save/load, and full integration remain pending.

## 1. Data flow

```text
Member 1: PDF → DocumentInfo + PageContent
Member 4: student question → NoteRequest
Member 2: DocumentInfo + NoteRequest + tuple[PageContent, ...] → GeneratedNote (draft)
Member 4: preview / edit / confirm → ProjectState (approved notes are eligible for export)
Member 3: source PDF + ProjectState → new PDF + ExportResult
```

Manual notes use `GeneratedNote(request_id=None, sections=user-authored content)` and bypass member 2 without requiring AI credentials. The name GeneratedNote is retained for compatibility with the team plan; it represents both generated and manual notes.

## 2. Common rules

- All public page numbers start at **1**. `original_page` always refers to the original lecture, never the shifted output page number.
- `document_id` is `sha256:` followed by the lowercase hexadecimal SHA-256 digest of all original PDF bytes. Renaming does not change identity; changing bytes does. Use `document_id_for_file()` to calculate it. This function does not certify that the file is a PDF.
- All IDs are nonblank strings. Use `str(uuid.uuid4())` for real request and note IDs; fixtures use readable IDs such as `request-001`. IDs do not change when content or titles are edited.
- Python uses frozen dataclasses and tuples; JSON uses objects and arrays. Decode with `from_dict()` or `from_json()`, not `GeneratedNote(**json_dict)`, which skips nested conversion.
- Types are strict: strings such as `"2"`, floats such as `2.0`, and booleans are not coerced into page integers. Unknown fields, unknown enumeration values, and blank required text raise ContractError.
- Text is Unicode; save JSON as UTF-8. Version 1 content is plain text and may include line breaks and formula source text. It is not arbitrary HTML, and full Markdown/LaTeX rendering is not guaranteed. Member 3 must not silently discard unsupported content.
- Page lists must not contain duplicates. The notes array determines the order of notes attached to the same original page; do not sort by UUID or title.
- Model content is data, not executable code, HTML, or instructions.

## 3. DocumentInfo: original document (member 1)

| Field | Python type | Rule |
| --- | --- | --- |
| `document_id` | `str` | Required SHA-256 identity in the format above |
| `filename` | `str` | Nonblank display name, such as lecture.pdf; not the document identity |
| `page_count` | `int` | Positive; obtained by the actual PDF reader |

The source path is stored separately in ProjectState.source_path. Do not use a path as a stable document ID.

## 4. PageContent: page content (member 1 → members 2 and 4)

| Field | Python type | Required / default |
| --- | --- | --- |
| `document_id` | `str` | Required |
| `original_page` | `int` | Required positive integer |
| `text` | `str` | Required |
| `extraction_status` | `Literal['ok', 'empty', 'error']` | Required |
| `preview_path` | `str or None` | None; optional local preview image path |
| `error_message` | `str or None` | None |

- `ok`: text must not be blank; error_message must be None.
- `empty`: no extractable text, such as a blank or potentially scanned page; text must be the empty string. This status does not claim to identify the page type.
- `error`: extraction failed; text must be empty and error_message must contain a displayable reason without credentials.
- `validate_page(document, page)` also verifies document identity and the upper page bound.
- Previews are regenerable cache files, not part of the project format. Extracted text does not imply understanding images or formulas.

Example: [page.json](../examples/data/page.json).

## 5. NoteRequest: student question (member 4 → member 2)

| Field | Python type | Required / default |
| --- | --- | --- |
| `request_id` | `str` | Required; use a new ID for each generation attempt |
| `document_id` | `str` | Required |
| `original_page` | `int` | Required; the original page to which the resulting note is anchored |
| `question` | `str` | Required nonblank text |
| `context_pages` | `tuple[int, ...]` | Required; includes the target original page and records context actually supplied |
| `selected_text` | `str or None` | None; selected source text, which the UI may verify separately |
| `language` | `str` | zh-Hant; en is another example; v1 only validates that it is nonblank |
| `level` | `str` | first-year; nonblank learning-level description |
| `style` | `ExplanationStyle` | simple |

Accepted styles: `simple`, `step_by_step`, `comparison`, and `example`.

Member 2 may select context first, but must record the final page set in the request before generation. Actual context pages must match that set exactly, with all pages marked ok. For target pages without extractable text, v1 uses manual notes or an explicit limitation message rather than pretending OCR exists.

## 6. NoteSection and GeneratedNote: structured notes (members 2 or 4 → member 3)

### NoteSection

| Field | Type / allowed values | Meaning |
| --- | --- | --- |
| `kind` | explanation, steps, comparison, example, quiz, answer, personal | Section category used by the renderer for headings and styles |
| `content` | Nonblank str | Plain text; preserve line breaks |
| `origin` | lecture, ai, user | Lecture-based content, model-added content/inference, or user-written/rewritten content |

The lecture label is a source claim, **not** a fact-check result. AI paraphrases of lecture content may still be wrong; the renderer must preserve this distinction. User-rewritten sections can be labeled user.

### GeneratedNote

| Field | Python type | Required / default |
| --- | --- | --- |
| `note_id` | `str` | Required; stable during editing |
| `document_id` | `str` | Required |
| `original_page` | `int` | Required |
| `title` | `str` | Required nonblank text |
| `sections` | `tuple[NoteSection, ...]` | Required; at least one section, rendered in this order |
| `source_pages` | `tuple[int, ...]` | Empty tuple; original pages referenced by the note as a whole |
| `request_id` | `str or None` | None; generated notes link to their generation request |
| `language` | `str` | zh-Hant |
| `status` | `Literal['draft', 'approved']` | draft |

- Lecture sections require source_pages; AI sections require request_id.
- Generated source pages must be a subset of context_pages, never pages the model did not receive.
- `validate_generation(document, request, context, note)` checks actual context, request ID, document identity, original page, language, reference bounds, and draft status. It does not establish factual correctness.
- Manual notes use user sections and may have no request or source pages. A manual note that cites the lecture can use lecture sections with source pages.
- Newly generated notes are drafts. Member 4 records approval only after explicit student confirmation. Editing or regeneration must return the note to draft. Models validate state values; the operation layer enforces state transitions.
- Regeneration uses a new request_id. Replacing a note may preserve its note_id. Replace only after generation succeeds; retain the old note on failure.

Example of editing a frozen model:

```python
from dataclasses import replace
edited = replace(note, title="My revised title", status="draft")
```

The example assumes an existing note. For implemented public editing operations, see the [workflow guide](PROJECT_WORKFLOW.md).

## 7. ProjectState: project persistence data (member 4)

| Field | Python type | Required / default |
| --- | --- | --- |
| `schema_version` | `int` | Python default 1; JSON must explicitly declare 1 |
| `document` | `DocumentInfo` | Required |
| `source_path` | `str` | Required; relative paths are relative to the project JSON file |
| `requests` | `tuple[NoteRequest, ...]` | Empty tuple |
| `notes` | `tuple[GeneratedNote, ...]` | Empty tuple; preserves editing and same-page insertion order |

A v1 project corresponds to one original PDF. Request IDs and note IDs must each be unique within the project. A note with request_id must reference a stored request and match its original page, language, and context bounds. Note anchors and source pages must not exceed the document page count.

Serialization is implemented:

```python
from pathlib import Path
from noteweaver import ProjectState

project = ProjectState.from_json(Path("examples/data/project.json").read_text(encoding="utf-8"))
json_text = project.to_json()
restored = ProjectState.from_json(json_text)
assert restored == project
```

Member 4 must still implement file save/load operations and path resolution; member 3 also checks the source before export. Both can call `verify_source(project, resolved_path)` to verify unchanged original bytes. If a file moves, users may select another file with the same hash. Different hashes must not silently reuse existing page anchors.

Project files do not embed PDFs, previews, or API keys. Store private lectures and notes in ignored local directories. Rejection of unknown fields can catch misplaced settings but cannot detect credentials embedded in arbitrary text.

## 8. ExportResult: output page maps (member 3 → member 4)

| Field | Python type | Meaning |
| --- | --- | --- |
| `document_id` | `str` | Original document identity |
| `output_path` | `str` | New PDF path returned by the exporter; the model itself does not create the file |
| `output_page_count` | `int` | Actual number of output pages |
| `original_to_output_pages` | `tuple[OriginalPageLocation, ...]` | Each item contains original_page and output_page, both 1-based |
| `note_to_output_pages` | `tuple[NotePageLocation, ...]` | Each item contains note_id and output_pages; long notes may span multiple pages |

Use arrays of objects instead of integer-keyed dictionaries, because JSON converts object keys to strings.

```json
{
  "original_to_output_pages": [
    {"original_page": 1, "output_page": 1},
    {"original_page": 2, "output_page": 2},
    {"original_page": 3, "output_page": 4}
  ],
  "note_to_output_pages": [
    {"note_id": "note-001", "output_pages": [3]}
  ]
}
```

This excerpt shows mapping fields only. See [export.json](../examples/data/export.json) for a complete example.

- V1 exports **approved notes only**; drafts stay in the project and may be previewed separately.
- Render original pages in order. After each original page, insert its approved notes in project.notes order.
- All pages belonging to one note are contiguous. Every output page belongs to exactly one original page or note, without overlap or omission.
- `validate_export(project, result)` checks mapping completeness, placement, and order. It does not open a PDF or inspect actual content/layout; member 3 owns those tests.
- Export to a new file and reject output paths that identify the source file, including aliases resolving to the same file.

## 9. Module interfaces

`src/noteweaver/interfaces.py` defines Protocol signatures and expectations, not PDF or AI implementations. Implementations provide the matching methods; inheritance from the Protocol is not required.

```python
# Member 1: reader
inspect(source: Path) -> DocumentInfo
read_page(source: Path, original_page: int) -> PageContent

# Member 2: generator
generate(document: DocumentInfo, request: NoteRequest,
         context: tuple[PageContent, ...]) -> GeneratedNote

# Member 3: exporter
export(source: Path, project: ProjectState, output: Path) -> ExportResult

# Member 4: editing is implemented in project.py;
# file persistence and orchestration of the above modules remain pending.
```

The block above illustrates signatures, not executable Python. Type/field mismatches, unsupported versions, and inconsistent associations use ContractError. File I/O failures retain OSError subclasses. Member 2 defines provider connection/authentication errors; do not return an empty successful note to represent failure. Integrate error presentation as modules become available.

## 10. Common fixtures and quick start

- [project.json](../examples/data/project.json): a three-page document, one question, an approved supplementary note, and a manual draft.
- [page.json](../examples/data/page.json): page 2 context.
- [export.json](../examples/data/export.json): four output pages; the manual draft is not exported.
- [contract_demo.py](../examples/contract_demo.py): data-flow and JSON round-trip validation.

These original synthetic fixtures make **no real model calls and create no PDF**. The all-zero SHA-256 value is a placeholder. The demo.pdf, preview, and output paths do not refer to existing files. Real sources require a freshly computed hash from the reader. Chinese fixture content demonstrates Unicode and bilingual support; documentation and explanatory messages are in English.

From the repository root with Python 3.10+ (validated locally on Python 3.14):

```bash
python -m pip install -e .
python examples/contract_demo.py
python -m unittest discover -s tests -v
```

Use a virtual environment. These commands install the local checkout, not a PyPI release. The contracts have no third-party runtime dependencies; builds require setuptools. Package metadata currently prevents upload; confirm distribution naming, licensing, and feature readiness before release.

## 11. Changing the format

All members import existing types from `noteweaver.models` rather than duplicating them. Field changes require matching documentation, JSON fixture, and contract-test updates, plus an explanation of affected modules. Without migration logic, do not silently accept unknown schema versions. The v1 loader rejects unknown fields. Breaking changes require a version increment and a migration plan.

Implementation references: [Python dataclasses](https://docs.python.org/3/library/dataclasses.html), [typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol), and the [Python packaging guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/).
