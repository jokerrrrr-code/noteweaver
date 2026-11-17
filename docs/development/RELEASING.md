# Preparing the first PyPI release

[Repository home](../../README.md) · [Changelog](../../CHANGELOG.md) · [School checks](../validation/SCHOOL_TEST_RECORD.md)

## Candidate decisions

| Item | Prepared value | Status |
| --- | --- | --- |
| Distribution name | `noteweaver` | Public project page and JSON endpoint returned HTTP 404 on 2026-11-17; not reserved or guaranteed available |
| Python import | `noteweaver` | Existing public API remains unchanged |
| First version | `0.1.0` | Functional beta candidate; not uploaded |
| Python requirement | `>=3.10` | Retained compatibility claim; local and school execution evidence currently covers Python 3.14 |
| Project license | `AGPL-3.0-only` | Approved by the project maintainer on 2026-11-17; license text, notice, and SPDX metadata included |
| Upload protection | `Private :: Do Not Upload` | Retained until the release decision |

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
project copyright/license grant is in [NOTICE](../../NOTICE).

The metadata includes:

```toml
license = "AGPL-3.0-only"
license-files = ["LICENSE", "NOTICE", "THIRD_PARTY_NOTICES.md"]
```

The build backend requires setuptools 77.0.3 or newer for these SPDX fields.
Both the wheel and source archive include the license and notices. The fixture
font retains its separately supplied OFL license. Dependencies retain their
own terms; see [third-party notices](../../THIRD_PARTY_NOTICES.md). This project
does not supply an Artifex commercial license for PyMuPDF/MuPDF.

The license approval does not authorize an upload or remove the upload blocker.

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

## Final release gate

- Verify that the approved license text, notices, and SPDX metadata are included
  in the final artifacts; preserve notices for any new third-party contributions.
- Verify name availability and package contents, then review and merge the release PR.
- Check supported Python versions beyond the currently recorded 3.14 runs before
  claiming them as tested; build success alone is not a runtime compatibility test.
- Remove `Private :: Do Not Upload` only after the explicit release decision,
  rebuild in a fresh output directory, and repeat metadata and installation checks.
- Set up the team's PyPI account and two-factor authentication. Keep any upload
  token outside Git and notebooks; a trusted publisher is an alternative.
- Upload only the reviewed wheel and source archive after explicit authorization.
  No upload command or automatic publication workflow is enabled by this preparation.
- Tag the exact release commit `v0.1.0` and retain artifact checksums and test logs.
- Verify the published project's owner, version, files, README rendering, and license.
- In a fresh school environment, install the verified published version with extras,
  run `pip check`, and repeat the manual-to-PDF demo. Only then update the public
  quick start to use the team's verified PyPI installation command.

A successful `twine check` validates distribution metadata/README, not name
ownership, runtime behavior, license approval, or publication. The upload blocker
is intentionally retained in preparation builds. Previous school checks installed
the checkout, not this release wheel and not a published PyPI package.

References: [PyPI naming](https://docs.pypi.org/project-management/choosing-a-name/),
[packaging metadata](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/),
[GNU AGPL v3](https://www.gnu.org/licenses/agpl-3.0.html).
