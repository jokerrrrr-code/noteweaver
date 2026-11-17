# Documentation and Repository Map

[Repository home](../README.md)

## Choose a guide

| Audience / task | Guide |
| --- | --- |
| New user | [Quick start](QUICKSTART.md) |
| Lecturer or reviewer | [Evaluator guide](EVALUATION.md) |
| Choose an example | [Examples index](../examples/README.md) |
| Run the manual notebook | [Notebook setup](NOTEBOOK_DEMO.md) |
| Export approved notes to PDF | [PDF export](EXPORT.md) |
| Generate notes through Groq | [Groq setup and public workflow](GROQ_SETUP.md) |
| Read or preview PDFs | [PDF reader](PDF_READER.md) |
| Create, edit, approve, or delete notes | [Manual note operations](PROJECT_WORKFLOW.md) |
| Save, reload, or relink a project | [Persistence](PERSISTENCE.md) |
| Implement a generation provider | [Generation](GENERATION.md) |
| Understand shared input/output types | [Data contracts](DATA_CONTRACTS.md) |
| Work as a contributor | [Contributing](../CONTRIBUTING.md), [team plan](../TEAM_PLAN.md), [agent guide](../TEAMMATE_GUIDE.md) |
| Check unfinished work | [Roadmap](../ROADMAP.md) |

## Top-level files and folders

| Path | Purpose |
| --- | --- |
| `README.md` | Main entry point: what works, installation, and links |
| `pyproject.toml` | Package metadata, Python requirement, dependencies, and build configuration |
| `src/noteweaver/` | Installable Python package; module map below |
| `tests/` | Behavior, failure-handling, and integration tests |
| `examples/` | Runnable scripts, notebooks, and original/licensed fixtures |
| `docs/` | User setup, evaluation, API behavior, and shared contracts |
| `TEAM_PLAN.md` | Four roles, interfaces, acceptance criteria, and handoffs |
| `TEAMMATE_GUIDE.md` | Contributor onboarding, Git workflow, and role-specific agent prompts |
| `ROADMAP.md` | Completed milestones and remaining release work |
| `CONTRIBUTING.md` | How to validate, commit, and submit changes |
| `AGENTS.md` | Repository instructions for coding agents |
| `.gitignore` | Excludes local credentials, environments, caches, and generated outputs |

`local_data/` and `generated/` are ignored working folders, not required download
contents. `.git/` stores version history and is managed by Git.

## Python module map

| Module | Responsibility | Main public entry points |
| --- | --- | --- |
| [`models.py`](../src/noteweaver/models.py) | Shared dataclasses, JSON validation, source identity, and page maps | `DocumentInfo`, `ProjectState`, `NoteRequest`, `GeneratedNote`, validators |
| [`interfaces.py`](../src/noteweaver/interfaces.py) | Protocol signatures for module boundaries | `PDFReader`, `NoteGenerator`, `PDFExporter` protocols |
| [`pdf_reader.py`](../src/noteweaver/pdf_reader.py) | PDF metadata, text extraction, neighboring pages, and actual page previews | Concrete `PDFReader`, `PagePreview`, `PreviewError`, `PreviewWarning` |
| [`project.py`](../src/noteweaver/project.py) | In-memory manual notes, editing, review state, and deletion | `create_project`, `add_manual_note`, `update_note`, `approve_note`, `delete_note`, `list_notes` |
| [`persistence.py`](../src/noteweaver/persistence.py) | Source-verified JSON save/load and safe file publication | `save_project`, `load_project` |
| [`generation.py`](../src/noteweaver/generation.py) | Validate generation inputs/outputs around a provider | Concrete `NoteGenerator`, `default_generator` |
| [`exporters.py`](../src/noteweaver/exporters.py) | Bilingual approved-note layout, safe PDF publication, maps and navigation | `PyMuPDFPDFExporter` |
| [`workflow.py`](../src/noteweaver/workflow.py) | Connect real PDF reading, generation, and project history | `generate_note` |
| [`providers/base.py`](../src/noteweaver/providers/base.py) | Provider contract and failure type | `NoteProvider`, `GenerationError` |
| [`providers/fake.py`](../src/noteweaver/providers/fake.py) | Fixed offline content for integration testing | `FakeNoteProvider` |
| [`providers/openai_compatible.py`](../src/noteweaver/providers/openai_compatible.py) | Configurable chat-completions transport and strict response parsing | `OpenAICompatibleProvider` |
| [`providers/groq.py`](../src/noteweaver/providers/groq.py) | Groq-specific endpoint, credentials, and defaults | `GroqProvider` |
| [`__init__.py`](../src/noteweaver/__init__.py) | Public package exports | `from noteweaver import ...` |
| [`providers/__init__.py`](../src/noteweaver/providers/__init__.py) | Provider exports | `from noteweaver.providers import ...` |
| [`py.typed`](../src/noteweaver/py.typed) | Marker for consumers of the package's type annotations | No executable code |

`interfaces.PDFExporter` is the protocol; `exporters.PyMuPDFPDFExporter` is the
working implementation. ExportResult and its synthetic JSON fixtures define
page maps; the fixtures themselves do not create a PDF.

## Test map

| Test file | What it checks |
| --- | --- |
| [`test_notebook_export.py`](../tests/test_notebook_export.py) | Actual notebook export cells: draft gate, current snapshot, repeat runs, and failures |
| [`test_pdf_exporter.py`](../tests/test_pdf_exporter.py) | Real shared-model export, pagination, Chinese, source/destination safety, links and bookmarks |
| [`test_contracts.py`](../tests/test_contracts.py) | Strict types, JSON, source identity, and page-map contracts |
| [`test_project.py`](../tests/test_project.py) | Note operations, stable identity/order, and approval invalidation |
| [`test_persistence.py`](../tests/test_persistence.py) | Save/load, path handling, source changes, and safe writes |
| [`test_pdf_reader.py`](../tests/test_pdf_reader.py) | Real PDF extraction, previews, bad inputs, and persistence integration |
| [`test_pdf_preview_safety.py`](../tests/test_pdf_preview_safety.py) | Source aliases, preview failures, and embedded fixture fonts |
| [`test_generation.py`](../tests/test_generation.py) | Fake generation, provider contracts, and opt-in live testing |
| [`test_generation_validation.py`](../tests/test_generation_validation.py) | Preflight validation, malformed provider output, and integration |
| [`test_groq_workflow.py`](../tests/test_groq_workflow.py) | Mocked Groq transport, credentials, errors, and PDF-to-project workflow |

Use the [evaluator guide](EVALUATION.md) for reproducible commands and the limits
of the current evidence. See the [examples index](../examples/README.md) for
script, notebook, fixture, and font-file purposes.
