# Publishing NoteWeaver

[Repository home](../../README.md) · [Changelog](CHANGELOG.md) · [School checks](../validation/SCHOOL_TEST_RECORD.md)

## Release configuration

| Item | Prepared value | Status |
| --- | --- | --- |
| Distribution name | `noteweaver` | Accepted at publication on 2026-11-18 |
| Python import | `noteweaver` | Existing public API remains unchanged |
| First version | `0.1.0` | Published on 2026-11-18 |
| Python requirement | `>=3.10` | Release workflow passed on Linux Python 3.10–3.14; school checkout checks cover 3.14 |
| Project license | `AGPL-3.0-only` | Approved by the project maintainer on 2026-11-17; license text, notice, and SPDX metadata included |
| Publication | Manual GitHub Actions dispatch | Requires matching version, `main`, passing checks, and the `pypi` trusted publisher |

PyPI can reject names that are reserved, prohibited, or too similar to another
project even when no public project page exists. Recheck immediately before the
first upload. TestPyPI and PyPI are separate registries; registering on one does
not reserve the name on the other. Do not rename the import package merely to
resolve a distribution-name conflict.

The single version source is `src/noteweaver/_version.py`. Setuptools reads it
without importing the package's runtime dependencies. The HTTP User-Agent uses
the same value. `0.1.0` describes the first functional beta, without promising a
stable 1.x API. It does not change the existing JSON `schema_version = 1`.

## License decision

The project maintainer approved GNU AGPL version 3 only on 2026-11-17 for the
team's original code and documentation. The SPDX identifier is `AGPL-3.0-only`.
The full, unmodified GNU license text is in [LICENSE](../../LICENSE), and the
project copyright/license grant is in [project notice](../LICENSE_NOTICES.md).

The metadata includes:

```toml
license = "AGPL-3.0-only"
license-files = ["LICENSE", "docs/LICENSE_NOTICES.md"]
```

The build backend requires setuptools 77.0.3 or newer for these SPDX fields.
Both the wheel and source archive include the license and notices. The fixture
font retains its separately supplied OFL license. Dependencies retain their
own terms; see [third-party notices](../LICENSE_NOTICES.md). This project
does not supply an Artifex commercial license for PyMuPDF/MuPDF.

The maintainer requested publication after approving the license. The release
workflow removes the preparation-only upload blocker; merging a PR does not publish.

## Build and validate locally

Run from a clean release checkout. Use new environment/output directory names
if these already exist, so old artifacts are never mistaken for new ones.
The commands below do not upload anything.

```bash
python3 -m venv .venv-release-tools
.venv-release-tools/bin/python -m pip install build twine
.venv-release-tools/bin/python -m build --outdir dist/release-0.1.0
.venv-release-tools/bin/python -m twine check --strict dist/release-0.1.0/*

python3 -m venv .venv-release-check
.venv-release-check/bin/python -m pip install "./dist/release-0.1.0/noteweaver-0.1.0-py3-none-any.whl[preview,export]"
.venv-release-check/bin/python -m pip check
.venv-release-check/bin/python -I -c "import noteweaver; from importlib.metadata import version; print(noteweaver.__file__); assert noteweaver.__version__ == version('noteweaver') == '0.1.0'"
.venv-release-check/bin/python -I -m unittest discover -s tests -v
```

On Windows use `Scripts/python.exe` instead of `bin/python`. Use the same Python
interpreter for environment creation and each subsequent check. `-I` ensures
imports do not depend on the current directory or `PYTHONPATH`. Do not enable the
opt-in live-provider test for ordinary release checks.

Inspect both archives before release. The wheel contains the Python package,
`py.typed`, and distribution metadata/notices. The source archive also contains
English docs, tests, example notebooks/scripts, the original sample PDF, and the
font with its license. No API keys, personal lectures, generated PDFs, environments,
Git metadata, notebook execution outputs, or local study JSON should be present.
Extract the source archive into a temporary folder, build/install it independently,
and run its tests to check that fixtures are not accidentally missing.

## Recorded preparation checks

See [local artifact validation](../validation/RELEASE_VALIDATION.md) for the checks actually
performed on this candidate. These do not replace the final release gate.

The first release is complete; see [published-release verification](../validation/RELEASE_VALIDATION.md#published-010-verification).
The setup below is retained for maintainers. After first publication, the pending
publisher becomes the project's regular trusted publisher. Do not recreate it for
each version.

## Connect PyPI to GitHub (one-time setup)

The maintainer must have a verified PyPI email and two-factor authentication.
No PyPI API token or AI provider key is needed for this workflow.

1. In GitHub repository Settings → Environments, create an environment named
   `pypi`. Restrict deployment branches to `main`. Add a required reviewer if
   the repository settings support it and the team wants a separate release approval.
2. Open [PyPI account publishing](https://pypi.org/manage/account/publishing/).
   Under **Add a new pending publisher**, select GitHub and enter:

   | Field | Value |
   | --- | --- |
   | PyPI project name | `noteweaver` |
   | Owner | `jokerrrrr-code` |
   | Repository name | `noteweaver` |
   | Workflow name | `publish.yml` |
   | Environment name | `pypi` |

3. Save the pending publisher. This does not reserve the package name or upload
   anything. If PyPI rejects the name, stop and agree a distribution name first.

The workflow file is `.github/workflows/publish.yml`. PyPI expects only its
filename, not the `.github/workflows/` prefix. Settings must match exactly.

## Validate and publish

Pull requests and pushes to `main` run build checks and an offline Python
3.10–3.14 matrix. The default build creates the wheel from the source archive.
Each matrix job installs that same wheel with preview/export extras, runs
`pip check`, unit tests, and the offline PDF export example. A configured matrix
is not evidence of a pass; inspect the actual results for the release commit.

The build checks the package name, version, license metadata and bundled notices,
and records artifact SHA-256 hashes and the commit in the Actions summary.
Actions retain the distributions for 30 days. Download them and retain the run
URL/checksums with the release record.

1. Review and merge the release PR after its validation checks pass.
2. Confirm the pending publisher and GitHub `pypi` environment are configured.
3. Open **Actions → Validate and publish → Run workflow**. Select branch `main`
   and enter `0.1.0` (or the exact version in `_version.py` for a later release).
   Dispatching this workflow requests publication; a PR merge alone does not.
4. The dispatch rebuilds and reruns all checks. Only the final publish job has
   `id-token: write`; it downloads the checked artifacts without checking out or
   building source. It authenticates through PyPI Trusted Publishing.
5. If an environment approval is configured, review the run commit and checksums
   before approving. A version mismatch, failed check, or non-main dispatch stops
   publication. Upload failures remain failures; existing files are not silently skipped.
6. Verify the published project's owner, version, files, README rendering, and
   license. Tag the exact successful run commit `v0.1.0`; do not tag a newer HEAD.
7. Install the published version in a fresh school environment, run `pip check`,
   and repeat the manual-to-PDF demo. Only then update the public quick start to
   use the verified PyPI installation command and mark the changelog released.

A successful `twine check` validates metadata/README, not ownership, runtime
behavior, or publication. Earlier school checks installed a checkout, not a
published PyPI distribution. No live AI request is part of this release workflow.

References: [PyPI naming](https://docs.pypi.org/project-management/choosing-a-name/),
[Trusted Publishing setup](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/),
[Publishing action](https://github.com/pypa/gh-action-pypi-publish),
[packaging metadata](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/).
