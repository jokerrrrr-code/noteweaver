# Notebook Workflows: Review, Export, and Download

[Repository home](../../README.md) · [Documentation index](../README.md)

Both notebooks connect the real reader, editable project state, verified JSON
persistence, and approved-note PDF exporter:

- [Manual workflow](../../examples/manual_workflow_demo.ipynb): supplied English
  personal note; no AI provider, key, or model request.
- [Generation workflow](../../examples/generation_workflow_demo.ipynb): fixed offline
  content by default, or explicit OpenRouter/Groq mode for a real answer.
  See [OpenRouter setup](OPENROUTER_SETUP.md) or [Groq setup](GROQ_SETUP.md).

## Setup and launch

From the repository root, activate a Python 3.10+ environment:

```bash
python -m pip install -e ".[preview,export]"
python -m pip install jupyterlab ipykernel nbconvert
python -m ipykernel install --user --name noteweaver --display-name "Python (NoteWeaver)"
python -m jupyterlab examples/manual_workflow_demo.ipynb
```

Select **Python (NoteWeaver)**. Install into the same environment as the selected
kernel. The `preview` extra provides page images; `export` provides the PDF
exporter. Jupyter tooling is for these demonstrations, not a package runtime
requirement. Open the generation notebook in the same JupyterLab window.

On JupyterHub, install the checkout and both extras into its selected kernel's
environment, then open the notebooks in the existing browser interface. Do not
start a separate JupyterLab server. Follow the university's kernel permissions.
See the [school test record](../validation/SCHOOL_TEST_RECORD.md) for the tested environment
and remaining release checks.

Keep the notebooks in the checkout. Kernels can start at the repository root or
inside `examples`. Each setup run creates a new ignored run folder.

## Manual walkthrough

Run cells in order, or restart and Run All to replay the supplied sample,
including its demonstration approvals. Read your own notes before executing an
approval cell.

1. Read the three-page bilingual lecture and preview original page 2.
2. Create and edit a manual English note, then confirm it after review.
3. Save/reopen JSON and check identity, content, page anchor, and review state.
4. Edit again, observe the return to draft, and explicitly review again.
5. Demonstrate an invalid-page error without losing existing work.
6. Export the current approved note and its matching project snapshot.
7. Inspect the original/note page maps and actual supplementary-page preview.
8. Download the study PDF and editable JSON, or use Jupyter's file browser.

The short supplied sample produces four pages: original pages 1 and 2, the note,
and original page 3. Long notes can produce additional pages. Source bytes stay
unchanged; approval records a review decision, not factual correctness.

## Generation walkthrough

A default Run All uses the fake provider, saves a **draft**, and skips PDF export.
It does not approve content automatically. To finish the demonstration:

1. Read the displayed draft; optionally set `REVISED_CONTENT` and run the edit cell.
2. Set `CONFIRM_REVIEW = True` and run the confirmation cell after reviewing.
3. Run the save, export, and preview/download cells below it.

For a real request, change only `MODE` in the first code cell to `"openrouter"`
or `"groq"`, then execute setup, provider selection, and generation in order.
The OpenRouter mode uses `openrouter/free` with a service-specific hidden key
prompt or `OPENROUTER_API_KEY`; it requires no extra SDK.

You do not need to rerun the provider or generation cells to export. In either
live mode, rerunning generation makes a new request; exporting never calls AI.
If several notes exist, all currently approved notes export in stored order;
drafts remain in the JSON and are excluded from the PDF.

## Files, replay, and errors

Each export creates a new `export-*` folder inside its run:

- Manual: `generated/notebook-demo/run-*/export-*`.
- Generation: `generated/groq-notebook/run-*/export-*`.

Each successful export contains `study.pdf`, the matching `study.json`, and a
`previews/` directory if rendering succeeds. Earlier exports are never replaced.
The manual notebook's initial save still refuses an existing JSON; its later
review cells deliberately update that run's working JSON with `overwrite=True`.

The exporter snapshots the **current** project, not an older reopened variable.
After an edit, the note is a draft again. Review it before rerunning export.
An export attempt with no approved notes creates no PDF and clears the latest
result. Export failures also clear the latest result and leave previous files
and notes unchanged; a verified JSON snapshot may remain in the new folder.
A preview/download cell refuses a stale result if the project changed since
export. Old cell outputs or files remain historical snapshots, not live views.

The preview uses an output page number from `note_to_output_pages`. Change
`PREVIEW_OUTPUT_PAGE` to inspect another output page; it is not an original-page
anchor. If preview dependencies fail, a clear message is shown and successful
PDF/JSON downloads remain available.

Download links embed the file bytes, so they do not depend on server-root paths.
Some browser/security policies may block embedded downloads. In that case,
open the printed export folder in Jupyter's file browser and download the files
there. Local verification checks link bytes and rendered previews; it does not
certify every browser or JupyterHub policy.

The JSON does not contain the lecture PDF. Keep the unchanged lecture and use
`load_project(..., source_path=...)` to relink it after moving downloaded files;
see [persistence path rules](../api/PERSISTENCE.md). Do not publish personal notebook
outputs: previews and embedded downloads contain the note/project content.

## Repeatable execution

After setup, execute the manual demonstration without opening a browser:

```bash
mkdir -p generated/notebook-validation
python -m nbconvert --to notebook --execute examples/manual_workflow_demo.ipynb \
  --ExecutePreprocessor.kernel_name=noteweaver \
  --ExecutePreprocessor.timeout=90 \
  --output=executed-demo.ipynb --output-dir=generated/notebook-validation
python -m unittest discover -s tests -v
```

The executed copy keeps outputs locally. Source notebooks in Git must have empty
outputs and execution counts. The generation notebook's default execution must
continue to leave drafts unapproved and skip PDF export.

## Scope

Notebook instructions, comments, and sample personal notes are in English.
Chinese remains deliberate bilingual fixture/input content. The export API
supports Chinese notes; it does not translate manual text automatically.
See [PDF export](../api/EXPORT.md) for font coverage, literal formula syntax, source
protection, and limitations. The manual notebook does not generate AI content.
