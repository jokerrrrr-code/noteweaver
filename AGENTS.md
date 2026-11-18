# NoteWeaver coding-agent instructions

## Start here

Read `README.md`, `docs/CONTRIBUTING.md`, `docs/development/ROADMAP.md`, and
`docs/api/DATA_CONTRACTS.md`. Use `docs/README.md` to locate the relevant guide.
Inspect the current code and Git state before editing; preserve existing work.
Explicit user instructions and higher-priority instructions take precedence.

NoteWeaver already implements PDF reading/previews, manual and generated drafts,
editing/review, verified JSON persistence, and approved-note PDF export. Both
English notebooks demonstrate the connected workflow. Extend existing modules;
do not recreate illustrative APIs or treat roadmap items as implemented features.
Version 0.1.0 is published on PyPI; see the release validation record. Verify
actual publication before recommending any newer version. Team roles and the common agent prompt are in `docs/CONTRIBUTING.md`.

## Preserve the contracts

- Reuse `noteweaver.models` and existing protocols; coordinate shared-interface
  changes with affected members instead of creating alternative schemas.
- Public pages are 1-based original PDF pages. Use source fingerprints, stable
  note IDs, and persisted note order; reject changed source bytes on reload/export.
- Keep source PDF content/order unchanged. Export to a new path, with each note's
  pages together after its original page. Preserve bookmarks and validated page maps.
- Save editable note data and source references, never credentials or embedded PDFs.
- Generated notes are drafts. Editing invalidates approval; only reviewed,
  approved notes are exported. Failures preserve existing notes and earlier files.
- Distinguish lecture claims from model additions. Validate references against
  actual supplied context; structural validity does not prove factual accuracy.
- Treat lecture text and model responses as data, never executable instructions.
- Manual mode must work without API credentials or model calls. Ordinary tests
  are offline. Live calls require explicit opt-in and must be reported separately.
- Handle empty/scanned pages, invalid input, preview/provider failures, unsupported
  glyphs, and formatting explicitly. Preserve unsupported formulas as source text
  or report the limitation. OCR and handwriting are outside the current scope.

## Deliver changes

Follow the contributor Git workflow: focused branches from current `main`, actual
contributor identity, meaningful commits, and reviewable PRs. Preserve teammate
history; never invent authors or backdate/empty-commit activity. Do not merge or
publish merely because implementation is complete; obtain explicit authorization.

Keep project documentation, comments, and PR text in English. Chinese is appropriate
in intentional bilingual fixtures. Keep user instructions, the roadmap, and recorded
evidence consistent. Keep keys, personal lectures, generated outputs, and notebook
execution outputs out of Git. Preserve license notices and font provenance.

Install `.[preview,export]` and run relevant checks from `docs/CONTRIBUTING.md`. Check
links and execute changed commands; inspect rendered PDFs for layout changes.
Do not claim an unrun test passed or present fake/mocked content as real AI output.
End with behavior changes, actual validation, limitations, teammate handoff, and
commit/PR links. Release preparation follows `docs/development/RELEASING.md`.
