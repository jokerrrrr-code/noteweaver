# Development roadmap

## Workstreams

The project is planned for four members: member 1 owns A, member 2 owns B, member 3 owns C, and member 4 owns D. Names have not been assigned. See [the detailed team plan](TEAM_PLAN.md) for deliverables, interfaces, review responsibilities, and first tasks.

| Workstream | Responsibility | Acceptance criterion |
| --- | --- | --- |
| A: PDF input and anchoring | Read PDFs, preview pages, extract text, retain original-page identity | Return the correct page content or an explicit extraction failure |
| B: Explanation generation | Select context, implement a provider interface and structured note output | Return editable notes with valid supplied source-page references and clear failure handling |
| C: Layout and export | Render notes, paginate, insert pages, maintain references and bookmarks | Export readable notes without cropping or reordering original lecture pages |
| D: Public API and integration | Editing, persistence, notebook interaction, packaging | Run the complete workflow and reload an existing project successfully |

Every contributor should document and test their own module and review another contributor's changes.

## Shared data contracts v1

Implemented in `src/noteweaver/models.py`, with signatures in `interfaces.py`, synthetic JSON fixtures, and offline tests. Read [the full contract](docs/DATA_CONTRACTS.md) for exact fields, provenance, draft/approval handling, persistence, and export mappings. Member 4's [in-memory note management](docs/PROJECT_WORKFLOW.md) and [verified save/load](docs/PERSISTENCE.md) are implemented; reader, generator, and exporter integration remain pending.

- `PageContent`: original page number, extracted text, preview, extraction status.
- `NoteRequest`: target original page number, selected text, question, language, level, style.
- `GeneratedNote`: note ID, original page anchor, title, sections, supplied source-page references, draft/approved state.

All public page numbers are 1-based. Insertions never change an existing original-page anchor. Define ordering for multiple notes attached to the same page.

## Milestones

1. **Manual end-to-end path:** load a PDF, add a handwritten-text note, export it after the right page.
2. **Generation:** create a draft from a page and question, preview and edit it, then export.
3. **Reliability:** multiple notes, long notes, Chinese text, save/reload, extraction/provider errors.
4. **Release:** documentation, package build, clean-environment installation, JupyterHub check, PyPI publication, one-minute demo.

## Verification

- Original content and ordering survive multiple note insertions.
- Notes stay attached to the intended original pages after save/reload.
- Long Chinese/English notes do not overlap or clip.
- Invalid source-page references are rejected or surfaced.
- Failed generation does not erase existing notes.
- Manual-note mode works without a model account.
- A built distribution installs and runs in the target notebook environment.

## Later versions

OCR and handwriting, image interpretation, topic-wide anchoring, multiple lecture sources, generated diagrams, and migration to revised lecture PDFs.

## One-minute demo

Show a lecture page, ask a question, preview and edit the explanation, export, and show the supplementary page immediately after the original page. Demonstrate with original sample material and explain which features are AI-assisted.
