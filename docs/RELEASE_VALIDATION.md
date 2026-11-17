# Release preparation validation

[Release checklist](RELEASING.md) · [School record](SCHOOL_TEST_RECORD.md)

Date: 2026-11-17. Candidate: **noteweaver 0.1.0**.
Environment: **CPython 3.14.7, macOS, arm64**. These are local preparation checks,
separate from the student's school JupyterHub results.

## Checks performed

| Check | Result |
| --- | --- |
| Isolated PEP 517 build | Source archive and universal Python wheel built successfully; the default build also built the wheel from its source archive |
| Strict metadata / README validation | `twine check --strict` passed for both archives |
| Wheel installation | Non-editable installation in a fresh virtual environment, including `preview,export` extras |
| Installed import / version | `python -I` imported from the environment's `site-packages`; public and distribution versions both `0.1.0` |
| Wheel dependency check | `No broken requirements found.` |
| Installed wheel regression suite | 133 tests, 132 passed, one opt-in live-provider test skipped |
| Tests copied into source archive | Extracted source archive's 133 tests also passed against the installed wheel, with the same one opt-in skip |
| Source archive installation | Separately built and installed into another fresh environment with only base dependencies |
| Base dependency isolation | Package imported with neither PyMuPDF nor pypdfium2 installed; dependency check passed |
| Base-only examples | Manual note editing, verified persistence, and offline fake-provider generation completed |
| Full-extra examples | Offline draft/save/reload completed; approved English and Chinese notes exported to a five-page study PDF with expected page maps |
| Archive contents | Checked package modules, `py.typed`, metadata/notices, source docs/tests/notebooks, sample PDF, font subset, and its OFL text |
| Notebook hygiene | Included notebooks had no execution outputs or execution counts |
| Public README links | Repository-relative links converted to absolute GitHub links for PyPI rendering |

Full-extra environment versions: pypdf 7.1.0, PyMuPDF 2.1, pypdfium2 5.15.2,
Pillow 13.0.0. Build tooling: build 1.6.1, setuptools 84.2.1, twine 7.0.0.
Dependency ranges remain in `pyproject.toml`; this record is an observed environment,
not a lockfile or a guarantee about all future dependency releases.

## Artifact boundaries

The wheel contains the importable package and its metadata/notices. The source
archive additionally provides reproducible examples, tests, documentation, and
licensed fixtures. Personal lecture PDFs, keys, local study data, generated outputs,
virtual environments, and Git history are excluded. The included PDF is the
repository's original bilingual sample, not a user's lecture upload.

Artifacts and logs stay in ignored local build/output directories. Rebuild from
the final reviewed release commit and retain that build's hashes when publishing.
The maintainer approved AGPL-3.0-only on 2026-11-17. Preparation artifacts
include the full license, project notice, and third-party notices in both archive
formats, with `License-Expression: AGPL-3.0-only` metadata. The artifacts retain
`Private :: Do Not Upload` while the final release decision is pending.

## Limits

No PyPI/TestPyPI upload, name reservation, paid service, or live AI call was made
for these checks. Successful metadata validation does not grant publishing rights
or approve a license. Python 3.10–3.13, other operating systems, and a clean school
installation of the eventual published version were not tested in this task.
The earlier school run used Python 3.14.9 and the development checkout. PDF layout
was not changed here; this task checked export behavior/page maps, with prior
visual evidence recorded separately in the school record.
