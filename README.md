# NoteWeaver

Turn questions about lecture slides into editable supplementary notes inserted after the relevant PDF pages.

## Status

Shared data contracts v1, in-memory note management, and verified project save/load are implemented. You can create a project from document metadata, add/edit/delete manual notes, confirm them, filter the note list, and save/reopen JSON files while checking source fingerprints. PDF inspection, bilingual text extraction, and page previews are also implemented; see [PDF reader setup and behavior](docs/PDF_READER.md). Structured note generation and a Groq-backed question-to-draft workflow are implemented. Supplementary-note rendering, PDF export, and the complete question-to-export workflow remain pending. Nothing has been published on PyPI; the distribution name remains provisional.

## Try the shared contracts locally

From this checkout in a Python 3.10+ virtual environment:

```bash
python -m pip install -e ".[preview]"
python examples/contract_demo.py
python examples/manual_notes_demo.py
python examples/persistence_demo.py
python -m unittest discover -s tests -v
```

The demos are offline and use synthetic document metadata; they do not create a PDF or call an AI model. The persistence demo writes real JSON and source-byte fixtures in a temporary directory and removes them afterward. See the [manual note workflow guide](docs/PROJECT_WORKFLOW.md) for the new API and its return values. Install this checkout, not an unrelated package with the same name on PyPI. Read the [shared data contracts v1](docs/DATA_CONTRACTS.md) before implementing any module.

Repository documentation and code explanations are written in English. Chinese sample text in the shared fixtures and tests demonstrates bilingual content support.

## Try the English notebook demo

Open [the manual workflow notebook](examples/manual_workflow_demo.ipynb) using
[the notebook setup guide](docs/NOTEBOOK_DEMO.md). It connects the real PDF reader
to manual note editing, approval, and verified save/reload. Run it to see the
page preview and results; committed outputs are cleared. No AI key is required.
AI generation and study-PDF export are not part of this demo.

## Generate notes with Groq

Follow [Groq setup and the public generation API](docs/GROQ_SETUP.md), or open
[the English generation notebook](examples/generation_workflow_demo.ipynb).
Use `GroqProvider` with your own Groq key for live generation; the notebook
starts in explicitly labeled offline mode. There is no automatic paid fallback.

```bash
python examples/groq_notes_demo.py --offline  # Fixed test content; no API call.
python examples/groq_notes_demo.py            # Real Groq request; hidden key prompt.
```

## Planned workflow

1. Open a text-based lecture PDF and preview an original page.
2. Select a passage or provide a question, explanation language, and style.
3. Generate a draft explanation using relevant lecture context, or write a note manually.
4. Review and edit the draft.
5. Insert supplementary pages after the selected original page.
6. Export a study PDF with original-page references and navigation.

## What makes NoteWeaver useful

Questions, editable explanations, and source pages stay connected. The package handles note organization, pagination, original-page tracking, and PDF export. AI-assisted explanation is optional; manual notes should work without an API key.

## First release scope

- Text-based PDFs, page previews, and extraction status.
- Original page numbers are always 1-based and remain stable after insertion.
- Questions with selected text, language, level, and explanation style.
- Structured notes, including explanations, examples, and source-page references.
- Review, edit, save, reload, and insert notes.
- Readable Chinese and English output, long-note pagination, and bookmarks.
- Clear errors and manual fallback when extraction or generation fails.

Source references indicate where context came from; they do not guarantee that an AI explanation is correct. Generated examples should be distinguished from lecture content.

## Project documents

- [Member 4: English notebook demo and setup](docs/NOTEBOOK_DEMO.md)
- [Member 4: project saving, loading, and source verification](docs/PERSISTENCE.md)
- [Member 4: manual note workflow and examples](docs/PROJECT_WORKFLOW.md)
- [Shared data contracts v1: fields, rules, and interfaces](docs/DATA_CONTRACTS.md)
- [Teammate and AI-agent guide, including task prompts](TEAMMATE_GUIDE.md)
- [Repository instructions for coding agents](AGENTS.md)
- [Four-member responsibilities and acceptance criteria](TEAM_PLAN.md)
- [Development roadmap and suggested workstreams](ROADMAP.md)
- [Contribution workflow](CONTRIBUTING.md)

## Development and licensing

The runnable examples cover contracts, in-memory note management, and verified file persistence. Team members should implement the agreed interfaces using the same models. The project is marked `Private :: Do Not Upload` in package metadata until distribution name and licensing are decided. The repository itself remains public. Use original or appropriately licensed sample material.
