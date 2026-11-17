# School JupyterHub Test Record

[Repository home](../../README.md) · [Evaluator guide](EVALUATION.md) · [OpenRouter setup](../guides/OPENROUTER_SETUP.md)

Date: **2026-11-17 (Asia/Hong_Kong)**. Operator: **Member 4**.

This record distinguishes student-run school checks from local inspection.
Evidence was supplied as terminal/notebook screenshots, pasted test output,
reported results, and four downloaded study PDFs. The coding assistant did not
execute commands on the school server. Credentials, session cookies, personal
server identifiers, notebook outputs, and generated PDFs are not committed.

## Tested checkout and environment

- Checkout: the repository cloned after PR #12 was merged. The corresponding
  main baseline is `9cf77c8e56435860e2415862cb2f0ec307e66f91`.
  A later terminal screenshot confirmed `git log -1 --oneline` at `9cf77c8`.
- Updated checkout: a subsequent screenshot confirmed a fast-forward to
  `04a8d5c` (merged PR #13) before the integrated OpenRouter notebook rerun.
- School kernel: Python **3.14.9**, conda-forge, Linux, Python 3 (ipykernel).
- Initial kernel install: editable checkout with `preview,export` extras.
  Installation output showed PyMuPDF 2.1, pypdf 5.9.0, pypdfium2 5.15.2,
  and Pillow 12.3.0.
- Separate clean environment: `.venv-school-check`, created with standard `venv`
  without system site packages. A non-editable installation built and installed
  `noteweaver-0.0.1.dev0` with PyMuPDF 2.1, pypdf 7.1.0,
  pypdfium2 5.15.2, and Pillow 13.0.0.

The student modified the school generation notebook's provider cell to instantiate
`OpenAICompatibleProvider` with the OpenRouter endpoint, `openrouter/free`, a hidden
key prompt, and a 120-second timeout. That local configuration produced the live
result. After updating to merged PR #13, the student also ran the integrated
`MODE = "openrouter"` workflow successfully. These are two separate live runs;
the earlier 127-test result belongs to the earlier checkout.

## Results and evidence strength

| Check | Observed result | Evidence |
| --- | --- | --- |
| Installation in school kernel | Successful editable install with preview/export extras | Installation output supplied by student |
| School kernel tests | 127 tests in 4.373 seconds, `OK (skipped=1)`, exit code 0 | Full pasted output and screenshot; 126 passed, one opt-in live test skipped |
| School kernel dependency check | Failed for other installed applications, including Jupyter AI and Hermes | Screenshot; no NoteWeaver requirement was directly listed; no pre-install baseline was available |
| Clean environment installation | Wheel built and installed successfully | Terminal screenshot |
| Clean environment dependency check | `No broken requirements found.` | Student report; full log was not supplied |
| Clean environment tests | `OK (skipped=1)` | Student report; exact count/timing were not supplied for this run |
| Manual notebook | Approved manual note inserted after original page 2 | Download screenshot and supplied four-page PDF, extracted and visually reviewed locally |
| Offline generation notebook | Draft first withheld from export, then exported after confirmation | Notebook screenshots and supplied four-page PDF, extracted and visually reviewed locally |
| Groq live request from school | HTTP 403; no note generated | Notebook screenshot; unauthenticated catalog request also returned 403 |
| Groq comparison from student's Mac | Unauthenticated catalog request returned 401 | Screenshot; demonstrates different access behavior, not valid-key authentication |
| OpenRouter catalog from school | HTTP 200 | Student report; this alone was not counted as live-generation success |
| OpenRouter live generation from school | `Draft created: Why a Free Choice Can Still Have an Opportunity Cost` | Provider configuration and generated-draft screenshots, followed by supplied exported PDF |
| Merged PR #13 notebook rerun | Generated a new English draft, approved it, and exported a four-page PDF | Updated Git hash screenshot, review output, and fourth supplied PDF; all four pages extracted and visually inspected locally |
| Real AI note export | Four-page PDF with the generated note after original page 2 | All pages extracted, rendered with Poppler, and visually inspected locally |

The skipped automated test is explicitly opt-in live-provider testing; the
OpenRouter notebook request is separate evidence. The school base environment
was not certified conflict-free. The isolated environment passed its dependency
check according to the operator's report. Groq's exact 403 cause was not established.

## Live OpenRouter example

- API base URL: `https://openrouter.ai/api/v1`.
- Requested model/router: `openrouter/free`. The actual routed model was not
  captured; do not attribute the result to a specific model company.
- Input: the bundled bilingual `examples/data/sample_lecture_3p.pdf`, original page 2.
- Question: `Why can a free choice still have an opportunity cost?`
- Output language: English; style: `example`.
- Draft: lecture-based explanation, AI-added explanation, campus-movie versus
  study example, a self-check question, and its answer.
- After student review and confirmation, output order: original page 1,
  original page 2, supplementary note, original page 3.
- Visual review: complete title, readable English note, readable Chinese/English
  source pages, and no observed clipping or overlapping text.

The merged-notebook rerun used a campus-concert versus a $15 hourly job example.
Its exported note retained the complete title and source labels without observed
clipping or overlap.

These two runs verify the English question-to-PDF workflow on the school server.
They do not establish general answer accuracy, live Chinese generation quality,
future free-model availability, unlimited requests, or universal network access.
Source labels identify claims and do not establish factual correctness.

## Reproduce the checks

In a notebook at the checkout root, install into the selected kernel:

```python
%pip install -e ".[preview,export]"
```

Restart the kernel after installation. For a separate clean installation check,
run these commands in the school's terminal **from the repository root**:

```bash
python -m venv .venv-school-check
.venv-school-check/bin/python -m pip install ".[preview,export]"
.venv-school-check/bin/python -m pip check
.venv-school-check/bin/python -m unittest discover -s tests -v
```

Use a fresh environment directory if that name already exists. These commands
do not switch the notebook kernel. They install the checkout, not a PyPI release.
The current test count may exceed the historical 127 as checks are added.
Never commit the virtual environment.

Run both notebooks using [notebook instructions](../guides/NOTEBOOK_DEMO.md). For live
generation, follow [OpenRouter setup](../guides/OPENROUTER_SETUP.md), explicitly review,
then save/export/preview without rerunning generation. Preserve test output and
the final PDF privately for the class demonstration.

## Remaining release checks

- Confirm package license, available distribution name, and release metadata.
- Build and validate the final release, publish it to PyPI, then verify installation
  of that published version on JupyterHub. GitHub installation is not PyPI publication.
- Rehearse the joint one-minute presentation with a clearly labeled saved backup.
