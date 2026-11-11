# NoteWeaver

Turn questions about lecture slides into editable supplementary notes inserted after the relevant PDF pages.

## Status

Planning and initial repository setup. The Python package is not implemented or published on PyPI yet. The name is provisional pending package-name availability checks.

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

- [Development roadmap and suggested workstreams](ROADMAP.md)
- [Contribution workflow](CONTRIBUTING.md)

## Development and licensing

Installation instructions and a runnable example will be added with the implementation. No working API is claimed yet. The team should choose a license before distribution and use original or appropriately licensed sample lecture material.
