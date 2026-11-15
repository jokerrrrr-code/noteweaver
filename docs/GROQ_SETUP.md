# Generate Real Notes with Groq

NoteWeaver can send selected lecture text and a question to Groq, validate the
returned structured draft, and attach the draft and request to an editable
project. Manual notes still work without any API key. No web server is required.

## Install and obtain a key

Use Python 3.10+ and install this repository, not an unrelated PyPI distribution:

```bash
python -m pip install -e ".[preview]"
```

Create an API key at https://console.groq.com/keys. Keep your account on Groq's
Free Plan if you want to use its free allowance. Limits depend on the account
and model; the package cannot guarantee unlimited free usage or control the
billing plan of a key supplied by the user. There is no automatic service/model
fallback or automatic retry when a request fails.

Groq's official documentation:
- [OpenAI-compatible endpoint](https://console.groq.com/docs/openai)
- [GPT-OSS 20B and JSON support](https://console.groq.com/docs/model/openai/gpt-oss-20b)
- [Account/model rate limits](https://console.groq.com/docs/rate-limits)
- [Free Plan behavior](https://community.groq.com/t/do-i-get-charged-for-anything-on-the-groq-free-plan/832)

## Run the command-line example

From the repository root:

```bash
python examples/groq_notes_demo.py
```

This command uses the bundled lecture's original page 2. If `GROQ_API_KEY` is
not set, an interactive terminal prompts for the key without displaying it.
The key is held in memory only. In a noninteractive terminal, set `GROQ_API_KEY`
using your environment's secret mechanism first; no prompt is attempted.

The command makes one real request, prints the draft's sections and origins,
and saves a verified JSON project under a new ignored `generated/groq-demo/`
folder. It does not approve the note or export a study PDF. For your own lecture:

```bash
python examples/groq_notes_demo.py /path/to/lecture.pdf --page 2 \
  --question "Explain the main idea with an example." --language en
```

To check the integration without a key or network request:

```bash
python examples/groq_notes_demo.py --offline
```

Offline mode is explicitly labeled and uses fixed fake content. It cannot
answer arbitrary questions and is not proof of real AI quality.

## Run the English notebook

Open [generation_workflow_demo.ipynb](../examples/generation_workflow_demo.ipynb)
using the kernel setup in [NOTEBOOK_DEMO.md](NOTEBOOK_DEMO.md).

1. Change `MODE = "offline"` to `MODE = "groq"`.
2. Set the question, original page, and output language.
3. Run the provider cell and enter the key through its hidden prompt, unless
   `GROQ_API_KEY` is already available in the kernel environment.
4. Run the generation cell. It sends only the selected page by default.
5. Review the text, optionally edit it, and set `CONFIRM_REVIEW = True` only
   after review. This defaults to False, including when running all cells.
6. Save and reopen the project. Drafts can be saved without approval.

A generation failure prints a clear message and leaves existing project notes
unchanged. Rerunning the generation cell deliberately makes another request.
Successful repeated calls append new drafts with fresh request/note IDs.
Restarting the kernel clears a key entered through the hidden prompt; it does
not remove a key that you independently configured in the process environment.
Never hardcode keys in a notebook, save them in project JSON, or commit them.

## Public Python API

```python
from getpass import getpass
from pathlib import Path
from noteweaver import GroqProvider, create_project, generate_note, save_project
from noteweaver.pdf_reader import PDFReader

source = Path("examples/data/sample_lecture_3p.pdf").resolve()
reader = PDFReader(render_preview=False)
project = create_project(reader.inspect(source), source)
provider = GroqProvider(api_key=getpass("Groq API key: "))

project = generate_note(
    project,
    original_page=2,
    question="Why can a free choice still have an opportunity cost?",
    provider=provider,
    language="en",  # Use "zh-Hant" for Traditional Chinese.
    style="example",
)

note = project.notes[-1]  # A draft, not automatically approved.
print(note.title)
Path("local_data").mkdir(exist_ok=True)
save_project(project, "local_data/study.json")  # Refuses to overwrite by default.
```

`generate_note()` returns a new `ProjectState`. It verifies source identity and
actual PDF page count, reads the requested context, generates a validated draft,
checks the source again, and appends the request and note together only on
success. It requires an absolute source path; `load_project()` already returns
one. Existing notes, IDs, review states, and ordering are preserved.

Optional arguments: `context_pages=(1, 2, 3)`, `selected_text`, `level`, and
`style` (`simple`, `step_by_step`, `comparison`, or `example`). The target page
must be included. All supplied pages must have successfully extracted text.
The default context is just the target page; there is no automatic topic search
or OCR. Preview dependencies are not needed by `generate_note()` itself.

`GroqProvider()` reads `GROQ_API_KEY`. Explicit `api_key=` overrides it.
It ignores `OPENAI_API_KEY`, `NOTEWEAVER_API_KEY`, `NOTEWEAVER_BASE_URL`, and
`NOTEWEAVER_MODEL` to avoid sending another service's key to the wrong endpoint.
Defaults: model `openai/gpt-oss-20b`, timeout 60 seconds, and a completion cap of
4096 tokens. You can override `model=`, `timeout=`, and `max_completion_tokens=`.
A cap limits response length; it is not an account billing limit. Long answers
can be truncated and rejected as malformed; request a shorter answer or choose
an appropriate cap before explicitly retrying.

The generic `OpenAICompatibleProvider` remains available with its original
environment configuration, plus explicit constructor settings. Shared data
models and persisted JSON schemas have not changed.

## Failures and validation

- Missing/rejected key: configure a valid Groq key and rerun deliberately.
- HTTP 429: wait for the applicable quota window, then retry; no paid fallback.
- Timeout/network failure: check the connection before retrying.
- Malformed response: no draft is attached; previous notes remain available.
- Invalid page/context or changed source: rejected before sending where possible;
  a source change during generation also prevents attachment.

Run `python -m unittest discover -s tests -v` for offline checks. The legacy
OpenAI-compatible live test now requires both `NOTEWEAVER_RUN_OPENAI_TESTS=1`
and its provider key, so merely configuring credentials does not trigger a live
call during the ordinary test suite. Groq transport tests mock HTTP responses;
a successful real CLI/notebook call is a separate live verification.

Source labels and structural validation do not establish factual correctness.
Always review generated explanations. PDF layout and supplementary-page export
remain separate Member 3 functionality.
