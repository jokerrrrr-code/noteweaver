# Generate Notes with OpenRouter

[Repository home](../../README.md) · [Notebook setup](NOTEBOOK_DEMO.md) · [School test record](../validation/SCHOOL_TEST_RECORD.md)

OpenRouter is an optional service for the existing `OpenAICompatibleProvider`.
No additional SDK or package dependency is required. Manual notes and offline
examples continue to work without credentials or model requests.

## Create a key and choose free routing

1. Sign in and create a key on the [OpenRouter keys page](https://openrouter.ai/keys).
2. Keep the complete key private. A key name, ID, or abbreviated display is not a key.
3. Use `openrouter/free` for this walkthrough. It selects an available free model
   that supports the requested features, so the actual model can change between calls.
   Free usage is limited; availability, latency, and response quality vary.

According to the [free-model guide](https://openrouter.ai/collections/free-models/),
free variants do not require purchasing credits. Some other zero-priced models
can require a funded account. The key's credit limit is a spending ceiling, not
a payment or deposit. A zero ceiling may still cause a budget rejection; inspect
the account settings and error before retrying, rather than assuming payment is
required. This walkthrough never configures a paid fallback.

Requests send selected lecture text and the question to OpenRouter and its
selected model provider. Review their data policies before using personal material.
The bundled original lecture is suitable for the first test.

## Use the generation notebook

Install this checkout with `python -m pip install -e ".[preview,export]"` in the
notebook kernel's environment. Open
[generation_workflow_demo.ipynb](../../examples/generation_workflow_demo.ipynb).

1. In the **first code cell**, change only the assignment to `MODE = "openrouter"`.
   Do not change the `if MODE == ...` conditions under **Choose the provider**.
2. Keep `CONFIRM_REVIEW = False` under **Confirm only after reviewing**.
3. Restart the kernel and run all cells. Enter the OpenRouter key at the hidden
   prompt. Alternatively, configure `OPENROUTER_API_KEY` using your environment's
   secret mechanism before launching the kernel. No `.env` file is loaded automatically.
4. Look for `Draft created:` under **Generate a draft**. Merely seeing
   `OpenRouter selected` does not establish successful authentication or generation.
5. Read the note and optionally edit it. After review, set `CONFIRM_REVIEW = True`
   and execute that cell, then the save, export, and preview/download cells.
6. Download the PDF and matching project JSON. Keep the original lecture PDF.

To fix a mistyped key, rerun the provider cell and then the generation cell, in
that order. The provider cell prefers `OPENROUTER_API_KEY` when present, so update
that variable if it is the source of an outdated key. Each generation execution
makes a new request. Do not rerun generation merely to export an existing note.

Default Run All remains offline and leaves notes as drafts. Live Run All also
leaves drafts unapproved unless you previously changed the confirmation flag.
Reset that flag before reviewing newly generated content. Saved notebook outputs
can contain lecture text and downloadable project data; clear them before committing.

## Public Python API

From the repository root after installing the checkout:

```python
from getpass import getpass
from pathlib import Path
from noteweaver import OpenAICompatibleProvider, create_project, generate_note
from noteweaver.pdf_reader import PDFReader

source = Path("examples/data/sample_lecture_3p.pdf").resolve()
project = create_project(PDFReader(render_preview=False).inspect(source), source)
provider = OpenAICompatibleProvider(
    api_key=getpass("OpenRouter API key (hidden): ").strip(),
    base_url="https://openrouter.ai/api/v1",
    model="openrouter/free",
    timeout=120,
)
project = generate_note(
    project,
    original_page=2,
    question="Why can a free choice still have an opportunity cost?",
    provider=provider,
    language="en",
    style="example",
)
print(project.notes[-1].title)
```

This creates a draft, not an approved note or PDF. Use the notebook for the full
review/export workflow. The explicit endpoint, model, and key prevent generic
`NOTEWEAVER_*` or `OPENAI_API_KEY` settings from selecting another destination.
`OPENROUTER_API_KEY` lookup is implemented in the notebook; the generic provider
does not automatically read that variable when used on its own.

## Troubleshooting

| Result | Action |
| --- | --- |
| HTTP 401 / key rejected | Check the endpoint and complete OpenRouter key; rerun provider, then generation. Never share the key to diagnose it. |
| HTTP 402 / budget issue | Check key limits, balance, and selected model in OpenRouter. This does not by itself mean you must pay for a free-model test. |
| HTTP 403 | Access, account policy, or budget restrictions may be involved. The package's generic message does not identify the exact cause. |
| HTTP 429 | Wait for the applicable quota window; avoid repeated retries. |
| HTTP 404 / unavailable provider | Check free-model availability and account data-policy settings; do not automatically enable paid routing. |
| Timeout or malformed response | Existing notes remain unchanged. Decide whether to retry; there is no automatic retry. |
| Provider selected but an old error remains | Compare execution numbers. Rerun generation once after provider setup. |
| No PDF after generation | Review and approve the note, then run save/export/preview. |

A preliminary terminal check is:

```bash
curl -sS --max-time 20 -o /dev/null -w "HTTP %{http_code}\n" https://openrouter.ai/api/v1/models
```

HTTP 200 only confirms access to the public model catalog, not authenticated
generation. The school record includes a subsequent successful real request.

Sources checked on 2026-11-17:
[authentication](https://openrouter.ai/docs/api_reference/authentication),
[free routing](https://openrouter.ai/docs/guides/routing/routers/free-router),
[usage limits](https://openrouter.ai/docs/api_reference/limits).
