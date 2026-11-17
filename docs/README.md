# Documentation

[Repository home](../README.md) · [Examples](../examples/README.md) · [Contributing](../CONTRIBUTING.md)

## Use NoteWeaver

| Guide | What you will do |
| --- | --- |
| [Quick start](guides/QUICKSTART.md) | Install, export your first study PDF, and choose a script or notebook |
| [Notebook workflows](guides/NOTEBOOK_DEMO.md) | Review/edit notes, save/reopen projects, export, preview, and download |
| [OpenRouter setup](guides/OPENROUTER_SETUP.md) | Configure the OpenRouter notebook/API and diagnose service errors |
| [Groq setup](guides/GROQ_SETUP.md) | Configure the Groq script/notebook/API and diagnose service errors |

Jupyter is an optional interface. The package also works in ordinary Python
scripts. Manual notes and export need no AI credentials; fake-provider examples
use fixed content rather than generating real answers.

## Python API and contracts

| Reference | Implementation / entry points |
| --- | --- |
| [Read and preview PDFs](api/PDF_READER.md) | `pdf_reader.py`: concrete `PDFReader`, `PagePreview`, preview errors/warnings |
| [Create and review notes](api/PROJECT_WORKFLOW.md) | `project.py`: create, add, edit, filter, delete, approve |
| [Save, reload, and relink](api/PERSISTENCE.md) | `persistence.py`: `save_project`, `load_project` |
| [Generate structured drafts](api/GENERATION.md) | `generation.py`, `workflow.py`, `providers/`: `NoteGenerator`, `generate_note`, fake and live providers |
| [Export approved notes](api/EXPORT.md) | `exporters.py`: `PyMuPDFPDFExporter` |
| [Shared data contracts](api/DATA_CONTRACTS.md) | `models.py`, `interfaces.py`: dataclasses, validation, JSON schemas, and protocols |

The package's public imports are in `src/noteweaver/__init__.py`. Its version is
in `_version.py`, and `py.typed` marks its type annotations. Protocols describe
interfaces; concrete reader/exporter implementations live in the modules above.
Tests under `tests/` follow these responsibilities; notebook tests execute the
actual provider/export cells. Run them using [the contributor guide](../CONTRIBUTING.md#set-up-and-verify).

## Evaluate the assignment

| Record | Purpose |
| --- | --- |
| [Evaluator guide](validation/EVALUATION.md) | Reproducible checks, contribution history, and the presentation walkthrough |
| [School JupyterHub record](validation/SCHOOL_TEST_RECORD.md) | Dated school evidence, including real OpenRouter generation and PDF export |
| [Release artifact validation](validation/RELEASE_VALIDATION.md) | Wheel/source installation checks and their tested-environment limits |

These records distinguish historical runs, local mocks, and live requests.
They do not imply that every platform or future provider response is verified.

## Develop and release

- [Contributor guide](../CONTRIBUTING.md): four-member roles, Git workflow, testing, and a coding-agent prompt.
- [Roadmap](development/ROADMAP.md): completed milestones and remaining work.
- [Release checklist](development/RELEASING.md): naming, licensing, packaging, and publication gates.
- [Changelog](../CHANGELOG.md), [project license](../LICENSE), [notice](../NOTICE), and [dependency notices](../THIRD_PARTY_NOTICES.md).

The former root-level `TEAM_PLAN.md` and `TEAMMATE_GUIDE.md` are consolidated into
`CONTRIBUTING.md`. The roadmap now lives under `docs/development/`. Earlier versions
remain available in Git history.

## Repository layout

```text
README.md              Start here
CONTRIBUTING.md        Team roles and development workflow
AGENTS.md              Instructions for coding agents
pyproject.toml         Package metadata and dependencies
MANIFEST.in            Source archive contents
src/noteweaver/        Python package
examples/              Runnable scripts, two notebooks, and licensed fixtures
tests/                 Offline unit and integration tests
docs/guides/           Installation, notebooks, and AI setup
docs/api/              Public operations and shared contracts
docs/development/      Roadmap and release checklist
docs/validation/       Evaluation and dated test evidence
```

`local_data/` and `generated/` are ignored working folders. They are not required
repository contents and must not hold files intended for publication.
