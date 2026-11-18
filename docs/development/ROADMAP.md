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
Earlier school checks installed a checkout. Version 0.1.0 is now published; its
PyPI installation was separately verified on macOS Python 3.14.

## Remaining release and assignment work

- [x] Verify the built wheel on Linux Python 3.10–3.14 in the release workflow.
- [x] Confirm PyPI accepted `noteweaver` at first publication.
- [x] Review final metadata, dependencies, and successful release workflow results.
- [x] Publish 0.1.0 and tag release commit `95d3457` as `v0.1.0`.
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
