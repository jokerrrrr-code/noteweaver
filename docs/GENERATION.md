# Note Generation (Member 2)

Turn lecture page text and a student question into an editable structured draft note.

## Responsibilities

- Accept a `DocumentInfo`, a `NoteRequest`, and the exact `tuple[PageContent, ...]` that matches `request.context_pages`.
- Return a `GeneratedNote` with `status="draft"`.
- Distinguish lecture-derived sections (`origin="lecture"`) from model-added material (`origin="ai"`).
- Run `validate_generation` before returning so other members can trust the shape.
- Isolate any live AI service behind a replaceable `NoteProvider`; never write API keys into project files or Git.

## Quick start (offline)

```python
from pathlib import Path
from noteweaver import (
    NoteGenerator, FakeNoteProvider, NoteRequest, PageContent, DocumentInfo,
)
from noteweaver.pdf_reader import PDFReader  # Member 1

reader = PDFReader()
source = Path("examples/data/sample_lecture_3p.pdf")
document = reader.inspect(source)
page = reader.read_page(source, 2)

request = NoteRequest(
    request_id="req-001",
    document_id=document.document_id,
    original_page=2,
    question="機會成本是否只是實際花掉的金錢？",
    context_pages=(2,),
    selected_text="機會成本",
    language="zh-Hant",
    style="example",
)

generator = NoteGenerator(FakeNoteProvider())  # or default_generator()
note = generator.generate(document, request, (page,))
print(note.title)
for section in note.sections:
    print(section.origin, section.kind, section.content[:60])
```

The fake provider never opens a network connection and produces deterministic Chinese or English content suitable for teammate integration tests.

## Provider interface

```python
from noteweaver.providers import NoteProvider, GenerationError

class NoteProvider(Protocol):
    def generate(
        self,
        document: DocumentInfo,
        request: NoteRequest,
        context: tuple[PageContent, ...],
    ) -> GeneratedNote:
        ...
```

- `FakeNoteProvider` — offline, fixed output, optional forced failure via `FakeNoteProvider(fail=True)`.
- `OpenAICompatibleProvider` — optional live path. Reads:
  - `NOTEWEAVER_API_KEY` or `OPENAI_API_KEY`
  - `NOTEWEAVER_BASE_URL` (default `https://api.openai.com/v1`)
  - `NOTEWEAVER_MODEL` (default `gpt-4o-mini`)

Keys stay in the process environment; they are never written to disk by this package.

## Error behaviour

| Situation | Exception | Notes |
| --- | --- | --- |
| Context pages ≠ `request.context_pages` | `ContractError` | Fail before calling the provider |
| Any context page not `extraction_status="ok"` | `ContractError` | Generation needs selectable text |
| Provider network / auth / timeout / malformed reply | `GenerationError` | Safe to retry; no key material in the message |
| Result has `status != "draft"` or cites pages outside context | `ContractError` | After the provider returns |

## Tests

```bash
# Offline suite (always runs)
python -m unittest tests.test_generation.FakeProviderTests -v

# Full generation tests (live tests skip without a key)
python -m unittest tests.test_generation -v
```

## Hand-off notes

- **Member 1**: supply `PageContent` with `extraction_status="ok"` via `read_page` / `read_neighboring_pages`. The generator never opens the PDF itself.
- **Member 3**: consume the returned `GeneratedNote` (still `draft` until Member 4 approves it). Layout should respect `origin` if you want visual distinction between lecture and AI material.
- **Member 4**: call `generator.generate(...)`, then attach the note (and the original `NoteRequest`) to the `ProjectState`. Keep the request history for later regeneration.

Do not implement PDF loading, note rendering, or the full Jupyter workflow inside this module.
