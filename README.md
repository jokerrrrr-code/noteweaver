# NoteWeaver

A Python package for turning lecture questions into editable notes linked to
original PDF pages. Use it in a Python script or a Jupyter notebook.

**Available now:** read and preview text-based PDFs, write manual notes or
request AI drafts, review/edit notes, and save/reopen verified project JSON.
**Also available:** approved-note PDF export with Chinese/English pagination and bookmarks.
Both notebooks include export, page previews, and PDF/JSON download links.
School JupyterHub installation, notebooks, and one live OpenRouter-to-PDF workflow
have been checked; see the [school test record](https://github.com/jokerrrrr-code/noteweaver/blob/main/docs/SCHOOL_TEST_RECORD.md).
PyPI publication remains pending. Release candidate metadata targets **0.1.0**;
see the [release checklist](https://github.com/jokerrrrr-code/noteweaver/blob/main/docs/RELEASING.md).

## Start here

| I want to... | Open |
| --- | --- |
| Install and try the package | [Quick start](https://github.com/jokerrrrr-code/noteweaver/blob/main/docs/QUICKSTART.md) |
| Set up OpenRouter free-model generation | [OpenRouter setup](https://github.com/jokerrrrr-code/noteweaver/blob/main/docs/OPENROUTER_SETUP.md) |
| Review the university assignment | [Evaluator guide](https://github.com/jokerrrrr-code/noteweaver/blob/main/docs/EVALUATION.md) |
| Export approved notes to PDF | [PDF export guide](https://github.com/jokerrrrr-code/noteweaver/blob/main/docs/EXPORT.md) |
| Choose a runnable demonstration | [Examples index](https://github.com/jokerrrrr-code/noteweaver/blob/main/examples/README.md) |
| Find an API or file's purpose | [Documentation and repository map](https://github.com/jokerrrrr-code/noteweaver/blob/main/docs/README.md) |
| Contribute as a teammate | [Contributing](https://github.com/jokerrrrr-code/noteweaver/blob/main/CONTRIBUTING.md) and [team guide](https://github.com/jokerrrrr-code/noteweaver/blob/main/TEAMMATE_GUIDE.md) |

## Install and try without an API key

Requires Python 3.10+ and Git. In a macOS/Linux terminal:

```bash
git clone https://github.com/jokerrrrr-code/noteweaver.git
cd noteweaver
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[preview,export]"
python examples/groq_notes_demo.py --offline
```

For Windows activation and JupyterHub setup, follow the [quick start](https://github.com/jokerrrrr-code/noteweaver/blob/main/docs/QUICKSTART.md).
If you already have a checkout, use it instead of cloning over existing work.
Install this repository; PyPI publication is still a release milestone.

The offline command reads the bundled three-page PDF, creates a **fixed test
draft**, and saves/reopens `study.json` in a new `generated/groq-demo/run-*`
folder. It makes no model request and does not answer arbitrary questions.

## Choose your workflow

| Workflow | Entry point | API key | Output |
| --- | --- | --- | --- |
| Write and review your own notes | [Manual notebook](https://github.com/jokerrrrr-code/noteweaver/blob/main/examples/manual_workflow_demo.ipynb) | None | Editable project JSON and approved-note PDF |
| Test the connected generation workflow | `python examples/groq_notes_demo.py --offline` | None | Fixed test draft and JSON |
| Generate a real AI explanation | `python examples/groq_notes_demo.py` | Your Groq key | AI draft and JSON |
| Generate, edit, and review interactively | [Generation notebook](https://github.com/jokerrrrr-code/noteweaver/blob/main/examples/generation_workflow_demo.ipynb) | Your OpenRouter or Groq key in live mode | Editable project JSON and approved-note PDF |

Use the [notebook setup guide](https://github.com/jokerrrrr-code/noteweaver/blob/main/docs/NOTEBOOK_DEMO.md) to select the correct Python
kernel. Notebooks are committed with outputs cleared; run them to see results.
The manual sample exports on Run All. The generation notebook requires explicit
review confirmation before export; its default Run All keeps the draft.
The generation notebook starts in `MODE = "offline"`; set the first code cell
to `MODE = "openrouter"` or `MODE = "groq"` for a real request. Do not change
the provider cell's conditional branches. See [OpenRouter setup](https://github.com/jokerrrrr-code/noteweaver/blob/main/docs/OPENROUTER_SETUP.md)
or [Groq setup](https://github.com/jokerrrrr-code/noteweaver/blob/main/docs/GROQ_SETUP.md) for hidden key input, quotas, troubleshooting,
and the public `generate_note()` API.

## How the package fits together

```text
Original PDF -> original page + question -> manual note or AI draft
             -> review/edit -> confirm -> save/reopen project JSON

Approved notes -> supplementary pages -> new study PDF (export extra)
```

Notes keep their original page anchors and stable IDs. Editing returns a note
to draft; approval is an explicit review action. Saving and reopening verify
that the source PDF's bytes have not changed. JSON stores note data and the
source reference, not a copy of the PDF or API credentials.

## Current scope

| Capability | Status |
| --- | --- |
| PDF metadata, selectable text, and original-page previews | Implemented |
| Manual notes, editing, approval, filtering, and deletion | Implemented |
| Structured generation, offline fake provider, Groq, and OpenRouter configuration | Implemented; recorded English live examples for Groq and OpenRouter |
| Source verification and project save/reload | Implemented |
| English instructions and bilingual lecture/note content | Supported; see examples and tests |
| Supplementary PDF pages, pagination, bookmarks, and export | Implemented through the API, script, and both notebooks |
| OCR, handwriting recognition, and automatic topic search | Outside the first-release scope |
| Course JupyterHub validation | Sample workflows verified; evidence and limits in [school record](https://github.com/jokerrrrr-code/noteweaver/blob/main/docs/SCHOOL_TEST_RECORD.md) |
| PyPI publication | Pending |

AI output needs review. Source labels and schema checks do not prove factual
accuracy. Free API allowances depend on the user's provider account and quotas.

## Verify and contribute

After installing with the preview and export extras:

```bash
python -m unittest discover -s tests -v
```

Ordinary test runs are offline. Live provider testing requires explicit opt-in;
see the [evaluator guide](https://github.com/jokerrrrr-code/noteweaver/blob/main/docs/EVALUATION.md) for commands, expected results,
verification evidence, and contribution history.

For an offline PDF demonstration, run `python examples/export_demo.py`. See the
[export guide](https://github.com/jokerrrrr-code/noteweaver/blob/main/docs/EXPORT.md) for font coverage and dependency licensing.

Code is in [`src/noteweaver/`](https://github.com/jokerrrrr-code/noteweaver/blob/main/src/noteweaver/), tests in [`tests/`](https://github.com/jokerrrrr-code/noteweaver/blob/main/tests/),
guides in [`docs/`](https://github.com/jokerrrrr-code/noteweaver/blob/main/docs/README.md), and demonstrations in
[`examples/`](https://github.com/jokerrrrr-code/noteweaver/blob/main/examples/README.md). Keep personal inputs in ignored `local_data/`
and generated results in ignored `generated/`.

## Project and licensing

This is a four-member university assignment. Documentation, comments, and demo
instructions are in English. Chinese text appears in bilingual fixtures and
content examples. See the [team plan](https://github.com/jokerrrrr-code/noteweaver/blob/main/TEAM_PLAN.md) and [roadmap](https://github.com/jokerrrrr-code/noteweaver/blob/main/ROADMAP.md).

The proposed first release is `noteweaver` version `0.1.0`. The name has no
public PyPI project at the last check, but is not reserved. The team's original code and documentation are licensed under
[AGPL-3.0-only](https://github.com/jokerrrrr-code/noteweaver/blob/main/LICENSE);
see the [copyright and license notice](https://github.com/jokerrrrr-code/noteweaver/blob/main/NOTICE).
PDF export uses PyMuPDF. See the [release decisions and checks](https://github.com/jokerrrrr-code/noteweaver/blob/main/docs/RELEASING.md).
Metadata retains `Private :: Do Not Upload` until release readiness is confirmed.
The sample font has its own
[documented OFL license and provenance](https://github.com/jokerrrrr-code/noteweaver/blob/main/examples/data/fonts/README.md).
