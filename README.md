# NoteWeaver

Turn questions about lecture slides into editable supplementary notes inserted after the relevant PDF pages.

## Status

Shared data contracts v1 are implemented: validated Python models, JSON serialization, module interface signatures, synthetic examples, and contract tests. PDF reading, AI generation, rendering, and the end-user workflow are not implemented yet. Nothing has been published on PyPI; the distribution name remains provisional.

## Try the shared contracts locally

From this checkout in a Python 3.10+ virtual environment:

```bash
python -m pip install -e .
python examples/contract_demo.py
python -m unittest discover -s tests -v
```

The demo is offline: it validates synthetic data and does not create a PDF or call an AI model. Install this checkout, not an unrelated package with the same name on PyPI. See [共用資料格式 v1](docs/DATA_CONTRACTS.md) before implementing any module.

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

- [共用資料格式 v1、欄位規則與模組介面](docs/DATA_CONTRACTS.md)
- [組員與 AI agent 使用指南（含可複製指令）](TEAMMATE_GUIDE.md)
- [Repository instructions for coding agents](AGENTS.md)
- [四人小組分工與交付標準](TEAM_PLAN.md)
- [Development roadmap and suggested workstreams](ROADMAP.md)
- [Contribution workflow](CONTRIBUTING.md)

## Development and licensing

The runnable example currently covers contracts only. Team members should implement the agreed interfaces using the same models. The project is marked `Private :: Do Not Upload` in package metadata until distribution name and licensing are decided. The repository itself remains public. Use original or appropriately licensed sample material.
