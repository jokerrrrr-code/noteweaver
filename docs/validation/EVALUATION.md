# Evaluator Guide

[Repository home](../../README.md) · [Quick start](../guides/QUICKSTART.md) · [Repository map](../README.md)

This guide identifies what can be run today, what the checks demonstrate, and
where to inspect individual contributions. It is not a claim that every
assignment requirement is already complete.

## Current deliverable

NoteWeaver is an installable development Python package with English Jupyter
walkthroughs. It connects a real lecture PDF to original-page-anchored manual or
AI-generated drafts, explicit review/editing, and source-verified JSON save/load.
Approved-note supplementary pages and study-PDF export are implemented through the API and export script. Both notebooks now include PDF export, output-page previews, and download links.

The workflow preserves a note's ID and original page when edited, invalidates
old approval after edits, records generation requests, and rejects changed
source PDFs on reopening. These reusable operations are implemented separately
from the replaceable AI provider. They also work with manually written notes.

## Reproduce the offline checks

First follow [Quick start](../guides/QUICKSTART.md) to install the checkout with
`.[preview,export]`. Then run from the repository root:

```bash
python examples/export_demo.py
python examples/pdf_reader_demo.py
python examples/groq_notes_demo.py --offline
python -m unittest discover -s tests -v
python -m pip check
```

| Check | Expected result |
| --- | --- |
| Export demo | Five pages: originals 1, 2, English note, Chinese note, original 3; valid maps and bookmarks |
| Reader demo | Three pages; English and Chinese text from page 2; real PNG previews; invalid pages and missing files rejected |
| Offline workflow | Clearly labeled fixed provider content; a draft attached to page 2; JSON saved and successfully reopened |
| Test suite | All ordinary tests pass; the explicitly opt-in live test is skipped |
| Dependency check | No broken installed requirements |

The offline provider returns fixed demonstration content. It validates the
integration path, not the quality of an AI answer. The contract demo's export
page map is synthetic and does not demonstrate a working PDF exporter.

## Inspect the notebook workflows

Use [Notebook setup](../guides/NOTEBOOK_DEMO.md) to open the notebooks and select the
correct kernel. Outputs are cleared in Git so reviewers can reproduce them.

| Notebook | What to inspect |
| --- | --- |
| [Manual workflow](../../examples/manual_workflow_demo.ipynb) | Actual page preview; manual draft; editing/approval; save/reload; re-review; four-page study PDF and downloads; source unchanged |
| [Generation workflow](../../examples/generation_workflow_demo.ipynb) | Offline or explicit OpenRouter/Groq mode; editable draft; explicit review confirmation; JSON persistence; approved-note PDF export, preview and downloads |

The manual notebook's Run All replays review of the supplied sample note.
The generation notebook defaults to offline mode and does not approve generated
content automatically. The two notebooks intentionally demonstrate different
review behavior; read their instructions before running them on personal notes.

## Optional real AI verification

For the school-tested OpenRouter configuration, use `MODE = "openrouter"` in the
[generation notebook](../../examples/generation_workflow_demo.ipynb). Follow
[OpenRouter setup](../guides/OPENROUTER_SETUP.md); its free router can choose different models.
The [school record](SCHOOL_TEST_RECORD.md) distinguishes observed evidence from
operator reports and documents the Groq access issue.

With your own Groq key, run:

```bash
python examples/groq_notes_demo.py
```

An interactive terminal prompts for the key without displaying it, unless
`GROQ_API_KEY` is already configured. This sends selected lecture text and the
question to Groq. Account quotas apply. See [Groq setup](../guides/GROQ_SETUP.md) for
certificate configuration, response errors, and using your own lecture.

A key is not required for the offline checks. Ordinary test runs do not make
real AI calls merely because a key exists. The legacy generic-provider live
test requires explicit `NOTEWEAVER_RUN_OPENAI_TESTS=1` as well as credentials.

## Recorded evidence

Historical baseline: `main` commit `b39aafd`, incorporating PRs #1 through #9.
PR #11 adds the exporter and integration fixes; its verification is recorded below. The following evidence was recorded during development:

| Evidence | Result and limitation |
| --- | --- |
| Full suite | 112 tests: 111 passed, 1 opt-in live test skipped; this is a recorded snapshot, not a permanent count |
| Reader + generator + project integration | English and Traditional Chinese offline scenarios passed with rendered, disabled, and unavailable previews |
| Notebook execution | Manual notebook executed; generation notebook executed from root/examples directories, plus mocked Groq success and HTTP 429 cases |
| Real Groq request, 2026-11-15 | `openai/gpt-oss-20b` returned an English explanation, student example, quiz, and answer for sample page 2; draft linkage, editing, save/reload, unchanged PDF, and no persisted key verified |
| Packaging | A wheel was built and installed into an isolated target; imports and offline generation/save/reload passed using existing environment dependencies |
| Fresh installation, 2026-11-16 | New Python 3.14 virtual environment; editable install with preview dependencies; six offline scripts, full suite, and pip dependency check passed |
| Runtime | Local verification used Python 3.14; this is not certification of every Python version or the university JupyterHub |

The live request is one successful English example. It does not establish
broad model quality, reliability, or live Chinese generation. Detailed feature
validation is recorded in the linked PRs below. Personal keys and locally
generated artifacts are not published as evidence.

## Exporter verification, 2026-11-17

PR #11 retains Member 3's initial exporter commit and adds Member 4's integration
repairs. The updated suite contains 124 tests: 123 passed and the opt-in live
provider test was skipped. This includes 12 exporter tests using real shared
models, not alternate fallback classes.

The same full suite passed with PyMuPDF 2.1 in the development environment and
PyMuPDF 1.26.7 after installing a built wheel with `preview,export` extras into
a new Python 3.14 environment. Short, long, and saved-project export demos,
offline generation, and `pip check` passed in the wheel environment. Importing
the base package without PyMuPDF still works and exporter creation provides an
installation message. No live AI request was made for this verification.

English and Traditional Chinese note pages, including continuation pages, were
rendered with Poppler and visually inspected. Tests verify original-page pixel
preservation, text coverage, page maps, source/destination protection, and
remapped internal links/bookmarks. At this historical checkpoint, JupyterHub, Windows, and other Python
versions were unverified; the later school record updates JupyterHub evidence.

## Notebook export verification, 2026-11-17

Both notebooks now connect review to PDF export, actual output-page previews,
and PDF/JSON download links. The updated full suite contains 127 tests: 126
passed and the opt-in live-provider test was skipped. Three notebook-cell tests
cover draft gating, current snapshots (including equivalent source paths),
repeat exports, and failure behavior without requiring Jupyter tooling.

Seven real-kernel executions passed: the manual notebook from root and examples,
generation with default draft behavior, confirmed generation from root and
examples, an injected export failure, and an injected preview failure. Successful
download link bytes matched the PDF/JSON files exactly; actual supplementary-page
previews were rendered and inspected. The original lecture remained unchanged.
All generation checks used the fixed offline provider; no live request was made.
Source notebooks retain cleared outputs and English instructions/comments.

Execution used local Python 3.14 and PyMuPDF 2.1. Browser download policies and
actual course JupyterHub behavior were still pending at this checkpoint; see
the later [school test record](SCHOOL_TEST_RECORD.md). The notebooks provide
a file-browser download fallback.

## School JupyterHub verification, 2026-11-17

See [School JupyterHub Test Record](SCHOOL_TEST_RECORD.md) for school installation,
127-test baseline, the separate clean-environment checks, manual/offline/live
OpenRouter PDF exports, and the limits of the evidence. The first live school notebook
used a locally replaced provider cell. The student subsequently updated to
merged PR #13 (`04a8d5c`) and successfully reran the integrated OpenRouter mode
through approval and PDF export. Publishing to PyPI remains pending.

## OpenRouter setup integration verification, 2026-11-17

Local verification of the integrated notebook passed 133 tests: 132 passed and
one explicitly opt-in live-provider test was skipped. Six new tests execute the
actual provider-selection cell and check offline defaults, prompted/environment
credentials, explicit OpenRouter routing, the retained Groq path, disabled
generation for a blank key, invalid modes, and preservation on HTTP errors.
HTTP responses are mocked; these tests make no live model requests.

Three real-kernel executions passed: default offline draft, mocked OpenRouter
draft, and mocked OpenRouter approval/export from the examples directory. The
last run produced four pages, rendered a preview, and exposed PDF/JSON download
links whose decoded bytes matched the saved files. Source identity remained
unchanged. Local `pip check` also reported no broken requirements. The earlier
school live request is recorded separately; no real key was used for this local
integration verification. Committed notebooks have no outputs or execution counts.

## PyPI preparation verification, 2026-11-17

See [release artifact validation](RELEASE_VALIDATION.md) for wheel/source builds,
clean installation checks, and offline regression results for the 0.1.0 candidate.
AGPL-3.0-only is approved and included in the artifacts. Final release
authorization remains pending.

## Inspect contributions

Review the [commit history](https://github.com/jokerrrrr-code/noteweaver/commits/main/)
and [pull requests](https://github.com/jokerrrrr-code/noteweaver/pulls?q=is%3Apr).
PR authorship and commit authorship can differ; inspect both for work added
during integration. Merging a PR does not mean its merger authored every change.

| Contribution area | PRs |
| --- | --- |
| Member 4: team onboarding and shared contracts | [#1](https://github.com/jokerrrrr-code/noteweaver/pull/1), [#2](https://github.com/jokerrrrr-code/noteweaver/pull/2) |
| Member 4: manual-note operations and persistence | [#3](https://github.com/jokerrrrr-code/noteweaver/pull/3), [#4](https://github.com/jokerrrrr-code/noteweaver/pull/4) |
| Member 1: PDF reader, bilingual fixture, tests, and docs | [#5](https://github.com/jokerrrrr-code/noteweaver/pull/5) |
| Member 4: preview integration fixes and notebook | [#6](https://github.com/jokerrrrr-code/noteweaver/pull/6), [#7](https://github.com/jokerrrrr-code/noteweaver/pull/7) |
| Member 2: generator/providers, with Member 4 validation fixes | [#8](https://github.com/jokerrrrr-code/noteweaver/pull/8) |
| Member 4: Groq configuration and runnable generation integration | [#9](https://github.com/jokerrrrr-code/noteweaver/pull/9) |
| Member 3: initial PDF exporter; Member 4: shared-contract and validation fixes | [#11](https://github.com/jokerrrrr-code/noteweaver/pull/11) |

AI-assisted development is permitted by the team's contribution guide. Each
contributor remains responsible for understanding and demonstrating the work.

## One-minute demonstration of the current version

Install dependencies and open the notebook before the presentation.

| Time | Demonstration |
| --- | --- |
| 0-15 seconds | Show the original lecture's page 2 and its preview |
| 15-30 seconds | Show a draft and its question; identify whether it was manually written, generated live, previously generated, or produced by the fake provider |
| 30-45 seconds | Edit the note and show its draft/review state |
| 45-60 seconds | Export, preview the supplementary page, and show PDF/JSON downloads and page maps |

Label prepared backup results honestly. The export demo can now show the final PDF and original/note page maps.

## Remaining assignment work

- Test installation of the eventual published PyPI version on school JupyterHub.
- Confirm PyPI distribution-name acceptance, then
  complete packaging/release checks and publication. Metadata currently retains
  `Private :: Do Not Upload`.
- Rehearse the final joint presentation and update this evidence when behavior changes.

The [roadmap](../development/ROADMAP.md) tracks these remaining tasks. The repository is
public; that alone does not mean the package is published on PyPI.
