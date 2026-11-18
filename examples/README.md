# Examples and Fixtures 

[Repository home](../README.md) · [Installation](../docs/guides/QUICKSTART.md) · [All documentation](../docs/README.md)

Run scripts from the repository root after installing the checkout. The preview
extra is required for preview demos; install `.[preview,export]` for the full suite. It is not needed
for text-only generation. Keep notebooks inside the checkout so they can find
the sample PDF.

## Recommended entry points

| Goal | Entry point | Needs a key? | Result |
| --- | --- | --- | --- |
| Export approved notes | `python examples/export_demo.py` | No | Five-page study PDF and project JSON |
| Test offline generation | `python examples/groq_notes_demo.py --offline` | No | Real PDF input, fixed draft, and saved project JSON |
| Manual notebook walkthrough | [manual_workflow_demo.ipynb](manual_workflow_demo.ipynb) | No | Page preview, personal note, editing/review, save/reload, PDF export and downloads |
| AI notebook walkthrough | [generation_workflow_demo.ipynb](generation_workflow_demo.ipynb) | Only in OpenRouter/Groq mode | Generated draft, optional editing/review, save/reload; PDF export after confirmation |
| Real AI command-line run | `python examples/groq_notes_demo.py` | Groq key | Live draft and verified project JSON |

Follow [notebook setup](../docs/guides/NOTEBOOK_DEMO.md) or
[OpenRouter setup](../docs/guides/OPENROUTER_SETUP.md) / [Groq setup](../docs/guides/GROQ_SETUP.md) as appropriate. GitHub displays notebook
source; execute it in Jupyter to see the cleared outputs.

## Every script

| File | Purpose | Inputs and side effects |
| --- | --- | --- |
| [export_demo.py](export_demo.py) | Export reviewed bilingual samples or an existing project | No AI calls; default approves supplied demo notes only; `--project` preserves user review states; `--long` exercises pagination; saves `generated/export-demo/run-*` |
| [contract_demo.py](contract_demo.py) | Validate the shared schemas and a synthetic export map | Reads synthetic JSON fixtures; no PDF creation or AI call |
| [manual_notes_demo.py](manual_notes_demo.py) | Add, edit, approve, filter, and delete personal notes | Uses synthetic document metadata; no PDF/file writes or AI calls |
| [persistence_demo.py](persistence_demo.py) | Save/reload, relink a source, and reject changed bytes | Uses temporary synthetic source bytes and JSON; removes them afterward |
| [pdf_reader_demo.py](pdf_reader_demo.py) | Inspect the real sample PDF, read page 2, and create previews | Uses temporary PNG files and removes them afterward |
| [generation_demo.py](generation_demo.py) | Inspect the lower-level generator/provider boundary | Reads the real sample, uses fixed fake output, and may cache a preview in the system temporary directory; does not save a project |
| [groq_notes_demo.py](groq_notes_demo.py) | Connect PDF input, generation, and verified project persistence | Live by default with key prompt; `--offline` selects fixed test content; saves new `generated/groq-demo/run-*` folders |
| [build_sample_pdf.py](build_sample_pdf.py) | Maintainer-only fixture rebuild | Requires ReportLab/fontTools and overwrites the bundled sample PDF; optional `--source-font` also rebuilds the font subset |

The fixture builder is not an installation step. Rebuilding changes the PDF's
fingerprint and can invalidate projects linked to the old fixture. Follow the
[font provenance and rebuild guide](data/fonts/README.md) before using it.

## Fixture files

| File | Purpose |
| --- | --- |
| [sample_lecture_3p.pdf](data/sample_lecture_3p.pdf) | Original three-page bilingual lecture; real PDF input for demos and tests |
| [page.json](data/page.json) | Synthetic PageContent example for contract tests |
| [project.json](data/project.json) | Synthetic project, request, and notes for contract tests |
| [export.json](data/export.json) | Synthetic ExportResult page map; not an exported PDF |
| [fonts/NoteWeaverDemo-Regular.ttf](data/fonts/NoteWeaverDemo-Regular.ttf) | Fixture-specific embedded font subset, not a complete Chinese note-rendering font |
| [fonts/OFL.txt](data/fonts/OFL.txt) | Font license |
| [fonts/README.md](data/fonts/README.md) | Font source, hash, license, and rebuild steps |

The JSON fixtures' all-zero document hash is intentionally synthetic. For a real
project, use metadata from `PDFReader.inspect()` and retain the original PDF.

## Generated files and replay

- Notebook export snapshots: each run contains new `export-*` folders with PDF/JSON and previews.
- PDF export results: `generated/export-demo/run-*`.
- Manual notebook results: `generated/notebook-demo/run-*`.
- Generation notebook results: `generated/groq-notebook/run-*`.
- Command-line generation results: `generated/groq-demo/run-*`.
- Temporary demo output is removed automatically where stated above.

The `generated/` and `local_data/` folders are ignored by Git. A saved JSON file
contains note content and a source reference, not the source PDF or provider key.
Read the notebook instructions before rerunning individual save/approval cells.
Clear outputs before committing notebook edits.

All instructions and code comments are in English. Chinese appears as deliberate
bilingual sample content. The export demo and both notebooks produce study PDFs from approved notes.
The generation notebook defaults to a draft and skips export until review is confirmed.
