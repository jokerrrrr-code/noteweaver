# NoteWeaver

Turn questions about lecture slides into editable supplementary notes inserted after the relevant PDF pages.

## Status

Shared data contracts v1 and in-memory note management are implemented. You can create a project from document metadata, add/edit/delete manual notes, confirm them, and filter the note list. PDF reading, AI generation, rendering, file save/load, and the complete end-user workflow are not implemented yet. Nothing has been published on PyPI; the distribution name remains provisional.

## Try the shared contracts locally

From this checkout in a Python 3.10+ virtual environment:

```bash
python -m pip install -e .
python examples/contract_demo.py
python examples/manual_notes_demo.py
python -m unittest discover -s tests -v
```

Both demos are offline and use synthetic document metadata; they do not create a PDF or call an AI model. See the [manual note workflow guide](docs/PROJECT_WORKFLOW.md) for the new API and its return values. Install this checkout, not an unrelated package with the same name on PyPI. Read the [shared data contracts v1](docs/DATA_CONTRACTS.md) before implementing any module.

Repository documentation and code explanations are written in English. Chinese sample text in the shared fixtures and tests demonstrates bilingual content support.

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

- [Member 4: manual note workflow and examples](docs/PROJECT_WORKFLOW.md)
- [Shared data contracts v1: fields, rules, and interfaces](docs/DATA_CONTRACTS.md)
- [Teammate and AI-agent guide, including task prompts](TEAMMATE_GUIDE.md)
- [Repository instructions for coding agents](AGENTS.md)
- [Four-member responsibilities and acceptance criteria](TEAM_PLAN.md)
- [Development roadmap and suggested workstreams](ROADMAP.md)
- [Contribution workflow](CONTRIBUTING.md)

## Development and licensing

The runnable examples cover contracts and in-memory note management. Team members should implement the agreed interfaces using the same models. The project is marked `Private :: Do Not Upload` in package metadata until distribution name and licensing are decided. The repository itself remains public. Use original or appropriately licensed sample material.
