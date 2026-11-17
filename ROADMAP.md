# Development Roadmap

[Repository home](README.md) · [Team responsibilities](TEAM_PLAN.md) · [Evaluation evidence](docs/EVALUATION.md)

## Implemented foundation

- Shared version-1 models, strict validation, source fingerprints, and module protocols.
- Real PDF inspection, selectable-text extraction, original-page previews, and clear failure states.
- Manual-note creation, editing, approval invalidation, filtering, and deletion.
- Verified JSON save/load with stable IDs, original-page anchors, and note order.
- Structured generation with an offline fake provider and configurable live providers.
- Groq-backed `generate_note()` orchestration, CLI example, and English notebooks.
- Offline integration tests and one recorded real English Groq generation.

See [current scope](README.md#current-scope) for the user-facing summary and
[evaluation](docs/EVALUATION.md) for the limits of the recorded verification.

## Implemented: supplementary pages and export

Member 3 supplied the initial exporter; Member 4 added shared-contract integration and validation fixes. See [PDF export](docs/EXPORT.md).

- [x] Render an approved short note after original page 2 of the three-page fixture.
- [x] Preserve original lecture content and ordering; export to a new destination.
- [x] Support Chinese/English fonts, wrapping, long notes, and multiple notes per page.
- [x] Return valid original/note page maps and implement the agreed bookmarks.
- [x] Reject source aliases and verify the source immediately before export.
- [x] Inspect rendered output for glyph problems, overlap, and clipping.
- [ ] Connect export to the manual and generation notebooks.

`ExportResult`, `validate_export`, and `PDFExporter` already define the shared
contract. The concrete PyMuPDFPDFExporter implements rendering and file publication. Reuse the approved-note
state produced by the existing project API; no AI service is needed for manual export.

## Then: release and course acceptance

- [ ] Verify installation and notebook execution in the actual course JupyterHub.
- [ ] Validate the final built distribution in a clean supported environment.
- [ ] Agree on the package-wide license and available PyPI distribution name.
- [ ] Review dependencies, public metadata, and documentation; remove the upload
      blocker only when the team is ready to publish.
- [ ] Publish a versioned package with the repository as its project homepage.
- [ ] Rehearse the one-minute joint demonstration and prepare labeled backup results.

Current metadata retains `Private :: Do Not Upload`. A local wheel build and a
public GitHub repository are not PyPI publication or course-environment acceptance.

## Ongoing verification

- Preserve existing notes when generation or saving fails.
- Verify IDs, review state, note order, and original-page anchors after save/reload.
- Keep ordinary tests offline and live-service checks explicitly opt-in.
- Expand live model-quality and bilingual evaluation beyond the recorded English example.
- Keep English guides, examples, and the status table synchronized with merged code.

## Later versions

OCR and handwriting recognition, image interpretation, automatic multi-document
topic search, generated diagrams, and migration to revised lecture PDFs are
outside the first release. Preserve unsupported formulas as source text or
report the limitation explicitly.
