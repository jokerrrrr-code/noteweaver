# Note Generation

[Repository home](../../README.md) · [Documentation index](../README.md)

Turn lecture page text and a student question into an editable structured draft note.

## Responsibilities

- Accept a `DocumentInfo`, a `NoteRequest`, and the exact `tuple[PageContent, ...]` that matches `request.context_pages`.
- Return a `GeneratedNote` with `status="draft"`.
- Distinguish lecture-derived sections (`origin="lecture"`) from model-added material (`origin="ai"`).
- Validate shared input types, document identity, page bounds, unique context pages, and extraction status before invoking a provider.
- Run `validate_generation` before returning so other members can trust the shape.
- Isolate any live AI service behind a replaceable `NoteProvider`; never write API keys into project files or Git.

For a complete PDF-to-draft workflow, use `generate_note()` and `GroqProvider`
as documented in [Groq setup](../guides/GROQ_SETUP.md).

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

Keys are read from the environment or explicit constructor arguments and held
in memory; they are never written to disk by the providers.

## Error behaviour

| Situation | Exception | Notes |
| --- | --- | --- |
| Invalid input types, wrong document, out-of-range/duplicate pages, or context pages ≠ `request.context_pages` | `ContractError` | Fail before calling the provider; no lecture text is sent |
| Any context page not `extraction_status="ok"` | `ContractError` | Generation needs selectable text |
| Provider network / auth / timeout / malformed reply | `GenerationError` | Safe to retry; no key material in the message |
| Result has `status != "draft"` or cites pages outside context | `ContractError` | After the provider returns |

## Strict response handling

The live provider requires a JSON object with a nonblank string `title` and a
nonempty `sections` array. Each section must be an object with valid shared
`kind`/`origin` values and nonblank string `content`. Numbers, booleans, nulls,
arrays, and objects are not converted into note text. Invalid response shapes
raise `GenerationError` with a generic message that excludes the raw payload.
Valid English/Chinese text and internal line breaks are preserved; surrounding
whitespace is trimmed. The returned note remains a draft.

Input validation runs before the provider call, while output validation still
runs afterward. A rejected request does not consume a provider call. This
validates identity and structure, not the factual accuracy of generated content.

## Tests

`tests/test_generation_validation.py` adds offline regressions for preflight
rejection without provider calls, strict mocked HTTP responses, bilingual
success cases, and integration with editing and verified persistence. These
checks never contact a real service. The existing live test requires both an API key and explicit
`NOTEWEAVER_RUN_OPENAI_TESTS=1`. Ordinary test runs remain offline even when
credentials are configured.

```bash
python -m unittest discover -s tests -p 'test_generation_validation.py' -v

# Offline suite (always runs)
python -m unittest discover -s tests -p 'test_generation.py' -k FakeProviderTests -v

# Full generation tests (live tests skip without explicit opt-in and a key)
python -m unittest discover -s tests -p 'test_generation.py' -v
```

## Hand-off notes

- **Member 1**: supply `PageContent` with `extraction_status="ok"` via `read_page` / `read_neighboring_pages`. The generator never opens the PDF itself.
- **Member 3**: consume the returned `GeneratedNote` (still `draft` until Member 4 approves it). Layout should respect `origin` if you want visual distinction between lecture and AI material.
- **Member 4**: the public `generate_note()` operation now creates the request, calls the generator, and attaches both to a new `ProjectState` only on success. The lower-level generator remains available for custom context handling.

Do not implement PDF loading, note rendering, or the full Jupyter workflow inside this module.
