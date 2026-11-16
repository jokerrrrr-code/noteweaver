# Manual Notebook Demo

[Repository home](../README.md) · [Documentation index](README.md)

Open [`examples/manual_workflow_demo.ipynb`](../examples/manual_workflow_demo.ipynb)
for a guided demonstration of the implemented manual workflow with a real PDF.
No AI provider, credentials, or model request is involved.

For optional real AI generation, see the separate [Groq generation notebook
and setup guide](GROQ_SETUP.md). This manual notebook remains API-free.

## Setup and launch

From the repository root, activate a Python 3.10+ virtual environment, then run:

```bash
python -m pip install -e ".[preview]"
python -m pip install jupyterlab ipykernel nbconvert
python -m ipykernel install --user --name noteweaver --display-name "Python (NoteWeaver)"
python -m jupyterlab examples/manual_workflow_demo.ipynb
```

Select **Python (NoteWeaver)** as the notebook kernel. Installing into one Python
environment and running another kernel can cause `ModuleNotFoundError`.
The preview extra installs PDFium and Pillow; these are required to see the image.
Jupyter tooling is for running the demo, not a new package runtime dependency.

On JupyterHub, install the checkout and preview extra into the environment used
by the selected kernel. Open the notebook in the cloned repository; use the
existing JupyterHub interface rather than starting another JupyterLab server.
If custom kernel registration is restricted, use the environment provided by
your university. Local execution does not establish that JupyterHub installation
has been verified; the team must still test its actual course environment.

## Run and inspect

Run cells in order, or use **Restart Kernel and Run All Cells** for the scripted
sample. Run All includes demonstration approvals. When using your own notes,
read their contents before executing each approval cell.

1. Read the bundled three-page lecture and extract original page 2.
2. Display a real preview, with a clear message if it is unavailable.
3. Create a project and a manually written English draft note.
4. Edit the note while preserving its ID and original-page anchor.
5. Review and approve the sample note.
6. Save JSON, reopen it, and verify content, identity, anchor, and review state.
7. Edit the approved note, observe the return to draft, and review it again.
8. Reject an invalid page without losing existing notes or modifying the PDF.

Each setup-cell execution creates a unique `generated/notebook-demo/run-*`
folder containing previews and `study.json`. This directory is ignored by Git.
A restart and full rerun never overwrites a previous run. Rerunning the initial
save cell alone raises `FileExistsError`; later cells demonstrate an explicit
update using `overwrite=True` for that run's JSON.

The original lecture must remain available when reopening the project. JSON
contains editable project data and a source reference, not the PDF itself.
The notebook works with a kernel working directory at the repository root or
inside `examples`; do not move it outside the checkout without adapting paths.

Expected final result: one approved English note anchored to original page 2,
a verified saved project, and unchanged original PDF bytes. The assertions in
the notebook check these outcomes. The invalid-page error is intentional and
caught; an unexpected exception should stop execution.

## Repeatable execution check

After the setup above, execute without opening a browser from the repository root:

```bash
mkdir -p generated/notebook-validation
python -m nbconvert --to notebook --execute examples/manual_workflow_demo.ipynb \
  --ExecutePreprocessor.kernel_name=noteweaver \
  --ExecutePreprocessor.timeout=90 \
  --output=executed-demo.ipynb --output-dir=generated/notebook-validation
python -m unittest discover -s tests -v
```

The executed copy keeps its outputs locally. Before committing changes to the
source notebook, clear its outputs and execution counts. This avoids publishing
personal file paths, lecture content, or note text from later experiments.

## Scope and teammate handoff

This demo integrates Member 1's reader with Member 4's existing project and
persistence functions. It does not add a second data model or a new public API.
Member 2's generation and Member 3's supplementary-page rendering/export are
not invoked or simulated. An approved note is ready for a future exporter;
no study PDF is produced by this notebook.

Notebook prose, comments, and personal-note examples are in English. Chinese
text appears only as bilingual lecture fixture content. Manual notes are not
translated automatically, and approval does not certify factual accuracy.
