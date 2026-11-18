# Quick Start

[Repository home](../../README.md) · [Documentation](../README.md)

Use NoteWeaver from Python scripts or notebooks. This walkthrough first produces
a study PDF without an API key. PyPI publication is pending; install this checkout.

## 1. Get the repository

You need Git and Python 3.10 or newer:

```bash
git clone https://github.com/jokerrrrr-code/noteweaver.git
cd noteweaver
```

Already cloned it? Inspect `git status` and save your changes first. On a clean
`main`, update with `git pull --ff-only origin main`. All commands below run from
the repository root.

## 2. Install

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install ".[preview,export]"
```

Windows PowerShell (activation is optional):

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install ".[preview,export]"
```

In PowerShell, use `.\.venv\Scripts\python.exe` in place of `python` below.
The `preview` extra supplies page images; `export` supplies PDF output. Text-only
reading, manual note management, and generation can use `python -m pip install .`.
Contributors should use an [editable install](../CONTRIBUTING.md#set-up-and-verify).

On school JupyterHub, install into the existing notebook kernel instead:

```python
%pip install ".[preview,export]"
```

Run this cell in a notebook at the repository root and restart the kernel after
installation. Open the example notebooks in JupyterHub's existing file browser;
do not start a second server. Follow your university's kernel permissions.

## 3. Export your first study PDF

```bash
python examples/export_demo.py
```

The demo reads the bundled three-page lecture and inserts supplied English and
Chinese sample notes after original page 2. It prints paths to `study.pdf` and
`study.json` inside a new `generated/export-demo/run-*` folder.

The PDF has **five pages**: original pages 1 and 2, two note pages, then original
page 3. The demo approves its supplied sample notes; review your own notes before
approving them. Each run uses a new folder and preserves the source PDF.

For the PDF API or an already-saved project, see [PDF export](../api/EXPORT.md).
The [examples index](../../examples/README.md) explains the other scripts.

## 4. Choose a notebook or Python API

| Goal | Entry point |
| --- | --- |
| Edit and review notes interactively | [Manual notebook](../../examples/manual_workflow_demo.ipynb) |
| Generate and review an AI draft | [Generation notebook](../../examples/generation_workflow_demo.ipynb) |
| Work in a Python script with your own lecture | [Manual note API](../api/PROJECT_WORKFLOW.md), [PDF reader](../api/PDF_READER.md), and [persistence](../api/PERSISTENCE.md) |

For local Jupyter installation, kernel selection, downloads, and cell replay,
follow [the notebook guide](NOTEBOOK_DEMO.md). Jupyter is not a runtime requirement
for Python scripts.

The generation notebook starts in `MODE = "offline"`: fixed test content, no key,
and no real answer to arbitrary questions. To call an AI service, choose
`MODE = "openrouter"` or `MODE = "groq"` in its first code cell and follow
[OpenRouter setup](OPENROUTER_SETUP.md) or [Groq setup](GROQ_SETUP.md). Each live
generation sends selected lecture text and the question to that service.

Review the draft, then set `CONFIRM_REVIEW = True` and run the confirmation,
save, export, and preview cells. Do not rerun generation simply to export.
Keep the original lecture PDF with the saved JSON; JSON does not embed it.

## 5. Verify or troubleshoot

From the repository root, with both extras installed:

```bash
python -m unittest discover -s tests -v
python -m pip check
```

Ordinary tests are offline; a skipped opt-in live test is expected. See the
[evaluator guide](../validation/EVALUATION.md) and [school test record](../validation/SCHOOL_TEST_RECORD.md)
for evidence and environment limits.

| Problem | Next step |
| --- | --- |
| `ModuleNotFoundError: noteweaver` or old imports | Install into the actual script/kernel environment; restart the kernel after reinstalling. |
| No preview image | Install the `preview` extra and read the preview warning. |
| Fixed opportunity-cost response | Offline mode uses a fake provider; choose an explicit live mode for a real answer. |
| Key, access, quota, or certificate error | Follow the selected provider's setup/troubleshooting guide. Keep HTTPS verification enabled. |
| No PDF after generation | Review and approve the draft, then run export; default Run All leaves drafts unapproved. |
| `FileExistsError` when saving JSON | Choose a new name, or explicitly use `overwrite=True` for an intended replacement. |
| Source fingerprint mismatch | Use the unchanged original PDF; a revised PDF needs a new project. |
