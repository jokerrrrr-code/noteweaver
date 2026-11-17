# NoteWeaver

Turn lecture questions into editable notes attached to the original PDF pages.
Review your notes, then export a study PDF with supplementary pages inserted
where they belong. Use NoteWeaver from a Python script or a Jupyter notebook.

**No API key is needed for manual notes or PDF export.** AI generation is optional
and uses your own OpenRouter or Groq key. English and Chinese text are supported.

## Try it

Requires Python 3.10+ and Git. In a macOS/Linux terminal:

```bash
git clone https://github.com/jokerrrrr-code/noteweaver.git
cd noteweaver
python3 -m venv .venv
source .venv/bin/activate
python -m pip install ".[preview,export]"
python examples/export_demo.py
```

This offline example adds two supplied, approved English/Chinese notes to the
sample lecture and prints the paths to a **five-page study PDF** and editable
project JSON under `generated/export-demo/`. It makes no AI request.

For Windows, JupyterHub, or your own lecture, follow the
[quick start](https://github.com/jokerrrrr-code/noteweaver/blob/main/docs/guides/QUICKSTART.md).
Version **0.1.0** is prepared; **PyPI publication is pending**. Install the repository
using the commands above until the published distribution is verified.

## Choose your next step

| I want to… | Start here |
| --- | --- |
| Read, edit, and export notes interactively | [Manual notebook](https://github.com/jokerrrrr-code/noteweaver/blob/main/examples/manual_workflow_demo.ipynb) and [notebook guide](https://github.com/jokerrrrr-code/noteweaver/blob/main/docs/guides/NOTEBOOK_DEMO.md) |
| Generate an AI explanation for a lecture page | [Generation notebook](https://github.com/jokerrrrr-code/noteweaver/blob/main/examples/generation_workflow_demo.ipynb), [OpenRouter setup](https://github.com/jokerrrrr-code/noteweaver/blob/main/docs/guides/OPENROUTER_SETUP.md), or [Groq setup](https://github.com/jokerrrrr-code/noteweaver/blob/main/docs/guides/GROQ_SETUP.md) |
| Use the Python API or find an example | [Documentation](https://github.com/jokerrrrr-code/noteweaver/blob/main/docs/README.md) and [examples](https://github.com/jokerrrrr-code/noteweaver/blob/main/examples/README.md) |
| Evaluate the university assignment | [Evaluator guide and test evidence](https://github.com/jokerrrrr-code/noteweaver/blob/main/docs/validation/EVALUATION.md) |
| Contribute or work with a coding agent | [Contributor guide and four-member roles](https://github.com/jokerrrrr-code/noteweaver/blob/main/CONTRIBUTING.md) |

## Current scope

```text
Lecture PDF → original page + question → manual note or AI draft
            → review/edit → approve → save project → export study PDF
```

- Read selectable PDF text and preview original pages.
- Create, edit, delete, and approve notes; editing returns them to draft.
- Save/reopen JSON with stable page anchors and source fingerprint verification.
- Export approved notes with bilingual pagination, bookmarks, and page maps.

The generation notebook defaults to **fixed offline test content** and requires
explicit review before export. Live AI needs network access and provider quota;
its output must be checked. Source labels do not establish factual correctness.
OCR, handwriting, automatic topic search, and rich Markdown/LaTeX rendering are
outside the current scope. Keep the original lecture alongside your saved JSON.

## Project and license

A four-member university Python-package project, with English documentation and
intentional bilingual fixtures. See the [changelog](https://github.com/jokerrrrr-code/noteweaver/blob/main/CHANGELOG.md),
[roadmap](https://github.com/jokerrrrr-code/noteweaver/blob/main/docs/development/ROADMAP.md),
and [release checklist](https://github.com/jokerrrrr-code/noteweaver/blob/main/docs/development/RELEASING.md).

Original code and documentation use [AGPL-3.0-only](https://github.com/jokerrrrr-code/noteweaver/blob/main/LICENSE).
[NOTICE](https://github.com/jokerrrrr-code/noteweaver/blob/main/NOTICE) and
[third-party notices](https://github.com/jokerrrrr-code/noteweaver/blob/main/THIRD_PARTY_NOTICES.md)
cover attribution and dependencies; the sample font retains its OFL license.
