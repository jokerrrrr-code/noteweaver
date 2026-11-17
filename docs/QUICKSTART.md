# Quick Start

[Repository home](../README.md) · [All documentation](README.md)

Use this guide to install NoteWeaver and try a real lecture PDF. The package
produces editable project JSON and, with the export extra, study PDFs.

## 1. Get the repository

You need Git and Python 3.10 or newer. In a terminal:

```bash
git clone https://github.com/jokerrrrr-code/noteweaver.git
cd noteweaver
```

Already cloned it? Open that checkout and inspect `git status`. On a clean
`main` branch, use `git pull --ff-only origin main` to update. Save your own
changes before switching branches; do not reset them to follow this guide.
All commands below run from the repository root unless stated otherwise.

## 2. Create an environment and install

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[preview,export]"
```

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[preview,export]"
```

In PowerShell, you can run the later commands with
`.\.venv\Scripts\python.exe` instead of `python`; activation is optional.
For a Python kernel already supplied by JupyterHub, install the checkout in
that kernel's environment rather than creating an unrelated interpreter.

The base package installs `pypdf`. The `preview` extra adds `pypdfium2` and
Pillow for page images. The `export` extra adds PyMuPDF for PDF output.
Install both extras for the full test suite. Text reading, manual notes,
and generation without previews can use `python -m pip install -e .`.

## 3. Try the complete offline example

```bash
python examples/groq_notes_demo.py --offline
```

Expected behavior:

1. Read the included lecture's original page 2.
2. Produce a clearly labeled fixed test draft, with no API request.
3. Print the note sections and leave the note in `draft` state.
4. Save and verify a new project at `generated/groq-demo/run-*/study.json`.

The exact folder and note ID vary per run. Repeating this command creates a
new folder instead of replacing a previous project. The output is JSON, not
a PDF with inserted notes. The original lecture remains unchanged.

For a real PDF preview and text-extraction checks:

```bash
python examples/pdf_reader_demo.py
```

That script uses temporary preview files, which it removes when finished. Use
a notebook below if you want to see the page image inline.

To export reviewed bilingual sample notes to PDF, run:

```bash
python examples/export_demo.py
```

See [PDF export](EXPORT.md) for saved projects and long-note pagination.

## 4. Use a notebook

```bash
python -m pip install jupyterlab ipykernel nbconvert
python -m ipykernel install --user --name noteweaver --display-name "Python (NoteWeaver)"
python -m jupyterlab examples/manual_workflow_demo.ipynb
```

Select **Python (NoteWeaver)** as the kernel. Start with the manual notebook:
it reads a real PDF, creates and edits a sample note, demonstrates review,
and saves/reopens the project without a key.

For generation, open `examples/generation_workflow_demo.ipynb` in the same
JupyterLab window. Its default offline mode runs without credentials. Change
`MODE` to `"groq"` and follow the hidden key prompt for a real AI request.

On JupyterHub, open the notebook in the existing browser interface; do not
start a second JupyterLab server. Follow your university's kernel permissions.
The actual course JupyterHub environment still needs team acceptance testing.

Read [Notebook setup and replay behavior](NOTEBOOK_DEMO.md) for details.

## 5. Generate a real AI note

```bash
python examples/groq_notes_demo.py
```

In an interactive terminal, enter your Groq key at the hidden prompt. If
`GROQ_API_KEY` is already configured, it is used directly. No key is committed
or stored in project JSON. This command sends the sample's page 2 and question
to Groq; your account plan and quotas apply.

For your own PDF:

```bash
python examples/groq_notes_demo.py /path/to/lecture.pdf --page 2 \
  --question "Explain this page with a student example." --language en
```

Replace the path and question with your own values. Use `--language zh-Hant`
for Traditional Chinese output. The question and note language are independent
of the English language used for repository documentation.

See [Groq setup](GROQ_SETUP.md) for the public Python API and error handling.

## 6. Check the installation

```bash
python -m unittest discover -s tests -v
python -m pip check
```

Tests do not call live AI unless explicitly enabled. A skipped live-provider
test is expected during ordinary verification. See [evaluation instructions](EVALUATION.md).

## Common questions

| Problem | What to do |
| --- | --- |
| `ModuleNotFoundError: noteweaver` | Install this checkout into the Python environment used by your terminal or notebook kernel. |
| Notebook imports an older version | Update the checkout, reinstall into that kernel if needed, then restart the kernel. |
| No preview image | Install `.[preview]` into the active environment; check the emitted preview warning. |
| Output looks like a fixed opportunity-cost example | You are using the fake provider. Choose Groq mode for a real answer. |
| Missing or rejected key | Use your own valid Groq key through the hidden prompt or `GROQ_API_KEY`. |
| HTTP 429 | Wait for the applicable quota window before deliberately retrying. |
| Certificate verification failure | Follow the trusted CA instructions in [Groq setup](GROQ_SETUP.md); keep HTTPS verification enabled. |
| `FileExistsError` when saving | Choose a new project filename, or use `overwrite=True` when replacing that project is intended. |
| Source fingerprint mismatch | Reopen with the original unchanged PDF; revised PDFs need a new project. |
| Cannot find the exported study PDF | The generation/manual notebooks save JSON. Run the separate export API or `export_demo.py` with approved notes; see [PDF export](EXPORT.md). |

## Where to go next

- [All runnable examples](../examples/README.md)
- [Manual note API](PROJECT_WORKFLOW.md)
- [Project saving, loading, and path rules](PERSISTENCE.md)
- [Generation and Groq API](GROQ_SETUP.md)
- [Repository and API map](README.md)
