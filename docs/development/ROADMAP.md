# Development Roadmap

[Repository home](../../README.md) · [Team roles](../CONTRIBUTING.md#team-responsibilities) · [Release checklist](RELEASING.md)

## Completed milestones

- Shared version-1 contracts, validation, stable IDs, and source fingerprints.
- Real PDF text extraction and original-page previews.
- Manual note creation, editing, filtering, deletion, and approval invalidation.
- Source-verified JSON save/load and relinking of unchanged PDFs.
- Structured generation with fake, Groq, and configurable OpenAI-compatible providers.
- Approved-note PDF export with English/Chinese pagination, bookmarks, and page maps.
- Manual and generation notebooks with review, export, previews, and downloads.
- School JupyterHub sample workflows, including a live OpenRouter rerun at merged PR #13.
- 0.1.0 preparation builds, clean installation checks, and approved AGPL-3.0-only licensing.

See the [school record](../validation/SCHOOL_TEST_RECORD.md) and
[artifact validation](../validation/RELEASE_VALIDATION.md) for evidence and limits.
These checks installed a checkout or local artifact, not a published PyPI version.

## Remaining release and assignment work

- [ ] Verify supported Python versions beyond the recorded 3.14 runs.
- [ ] Confirm PyPI distribution-name acceptance at first publication.
- [ ] Review final metadata and dependencies; remove `Private :: Do Not Upload`
      only after an explicit release decision, then rebuild and validate.
- [ ] Publish reviewed versioned artifacts and tag the corresponding commit.
- [ ] Verify installation of the published version on school JupyterHub.
- [ ] Rehearse the joint presentation with clearly labeled backup results.

## Ongoing maintenance

Preserve source content, note identity/order, review state, and prior data on
failure. Keep ordinary tests offline, live evidence separate, and English guides
synchronized with the implementation. Expand live answer-quality and bilingual
evaluation beyond the recorded English examples.

## Later scope

OCR, handwriting and image interpretation, automatic cross-document topic search,
generated diagrams, and migration to revised lecture PDFs are deferred. Preserve
unsupported formulas as text or report the limitation explicitly.
